from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import ugettext_lazy as _
from django.db.models import Avg, Q
import functools
from .models import Food
from .forms import UserRegisterForm
from .utils.constant import RATE_TEMPLATE as _rate

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
