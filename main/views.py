from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django.db.models import Avg, Q
import functools
import copy
from .models import Food, Review, Reply
from .forms import UserRegisterForm
from .utils.constant import RATE_TEMPLATE

def index(request):
    foods = Food.objects.prefetch_related('image_set').annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')
    query = ''

    if request.method == 'GET' and 'query' in request.GET:
        query = request.GET['query'].strip()
        keywords = query.split()
        # Search for each keyword in query. For example: "sushi pizza"
        foods = foods.filter(functools.reduce(lambda x, y: x | y, [Q(name__icontains=word) for word in keywords]))

    context = {
        "foods": foods,
        "keyword": query
    }
    return render(request, 'index.html', context)

@csrf_protect
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST or None)
        
        if form.is_valid():
            form.save()
            messages.success(request, _(f"Your account has been created! You can login now"))
            
            return redirect('login')
            
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})
    
def food_details(request, id):
    food = Food.objects.prefetch_related('review_set').annotate(avg_rating=Avg('review__rating')).filter(id=id).first()
    
    # Copy constant to another dict to reset dict value on page refresh
    _rate = copy.deepcopy(RATE_TEMPLATE)
    
    # How many reviews per star?
    for review in food.review_set.all():
        i = review.rating
        if i in _rate:
            _rate[i][1] += 1
            _rate[i][2] = int(_rate[i][1]/5 * 100)

    context = {
        "food": food,
        "rate_dict": _rate,
    }
    return render(request, 'foods/details.html', context)

@login_required
def review(request, id):
    if request.method == 'POST':
        user = request.user
        food = Food.objects.prefetch_related('review_set').filter(id=id).first()
        comment = request.POST.get('comment').strip()
        rating = request.POST.get('rating')
        
        if not comment or int(rating) == 0:
            review_id = -1
        else:
            review = Review.objects.create(comment=comment, rating=rating, user=user, food=food)
            review_id = review.id

        context = {
            "review_id": review_id,
        }

        return JsonResponse(context)
        
@login_required
def reply(request, food_id, review_id):
    if request.method == 'POST':
        user = request.user
        parent = Review.objects.prefetch_related('reply_set').filter(id=review_id).first()
        content = request.POST.get('content').strip()

        if not content:
            reply_id = -1
        else:
            reply = Reply.objects.create(content=content, parent=parent, user=user)
            reply_id = reply.id

        context = {
            "reply_id": reply_id,
        }

        return JsonResponse(context)
