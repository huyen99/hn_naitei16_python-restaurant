from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django.db.models import Avg, Q
import functools
import copy
from .models import Food, Review, Reply, Bill, Item, Status
from .forms import UserRegisterForm
from .utils.constant import RATE_TEMPLATE

def get_cart(request):
    bill, cart_items, in_cart = None, None, []
    if request.user.is_authenticated:
        status = get_object_or_404(Status, name='cart')
        bill = Bill.objects.prefetch_related('item_set').filter(user=request.user, status=status).first()
        cart_items = bill.item_set.all()
        in_cart = [item.food for item in bill.item_set.all()]
    
    return bill, cart_items, in_cart

def index(request):
    foods = Food.objects.prefetch_related('image_set').annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')
    query = ''

    if request.method == 'GET' and 'query' in request.GET:
        query = request.GET['query'].strip()
        keywords = query.split()
        # Search for each keyword in query. For example: "sushi pizza"
        foods = foods.filter(functools.reduce(lambda x, y: x | y, [Q(name__icontains=word) for word in keywords]))

    bill, _, in_cart = get_cart(request)

    context = {
        "foods": foods,
        "keyword": query,
        "in_cart": in_cart
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
    _, _, in_cart = get_cart(request)

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
        "in_cart": in_cart
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

@login_required
def cart(request):
    bill, cart_items, _ = get_cart(request)
    
    context = {
        "cart": bill,
        "items": cart_items
    }
    return render(request, 'cart/cart.html', context)

@login_required
def add_to_cart(request):
    bill, cart_items, _ = get_cart(request)
    food = get_object_or_404(Food, id=request.POST.get('id'))
    action = ''

    if cart_items.filter(food=food).exists():
        get_object_or_404(Item, food=food, bill=bill).delete()
        action = 'remove'
    else:
        if food.discount:
            unit_price = float(food.price) * float(food.discount)
        else:
            unit_price = food.price
        Item.objects.create(food=food, bill=bill, quantity=1, unit_price=unit_price)
        action = 'add'

    context = {
        "action": action,
    }

    return JsonResponse(context)

@login_required
def remove_from_cart(request, id):
    success = False
    if get_object_or_404(Item, id=id).delete():
        success = True
    
    context = {
        "success": success,
    }
    return JsonResponse(context)

@login_required
def profile(request):
    reviews = Review.objects.filter(user=request.user)
    replies = Reply.objects.filter(user=request.user)
    status = get_object_or_404(Status, name='cart')
    orders = Bill.objects.filter(user=request.user).exclude(status=status)
    
    context = {
        "reviews": reviews,
        "comments": replies,
        "orders": orders
    }
    
    return render(request, 'accounts/profile.html', context)
