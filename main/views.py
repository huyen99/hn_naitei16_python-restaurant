from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django.db.models import Avg, Q
from django.db import transaction
import functools
import copy
import json
from decimal import Decimal
from .models import Food, Review, Reply, Bill, Item, Status
from .forms import UserRegisterForm
from .utils.constant import RATE_TEMPLATE

def get_cart(request):
    bill, cart_items, in_cart = None, None, []
    if request.user.is_authenticated:
        status = get_object_or_404(Status, name='cart')
        bill = Bill.objects.prefetch_related('item_set').filter(user=request.user, status=status).first()
        cart_items = bill.item_set.all()
        in_cart = [item.food for item in cart_items]
    
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

@login_required
def checkout(request):
    cart = request.POST.get('checkoutip')
    cart = json.loads(cart)
    bill, _, _ = get_cart(request)
    final_price = 0
    
    with transaction.atomic():
        for keys, values in cart.items():
            food = get_object_or_404(Food, id=int(keys))
            item = get_object_or_404(Item, food=food, bill=bill)
            item.quantity = int(values)
            item.save()
            final_price = final_price + item.unit_price * int(values)
    
    if bill.coupon:
        final_price = Decimal(final_price * bill.coupon.value) + floatbill.delivery_charges
    else:
        final_price = Decimal(final_price) + bill.delivery_charges
        
    context = {
        "fprice": final_price
    }

    return render(request,'cart/checkout.html', context)
    
@login_required
def handle_checkout(request):
    if request.method == "POST":
        final_price = request.POST.get('fprice')
        inputName = request.POST.get('inputName')
        inputPhoneNo = request.POST.get('inputPhoneNo')
        inputAddress = request.POST.get('inputAddress')
        inputCity = request.POST.get('inputCity')
        inputCountry = request.POST.get('inputCountry')
        inputZip = request.POST.get('inputZip')
        inputShipNote = request.POST.get('inputShipNote')

        for v in [inputName, inputPhoneNo, inputAddress, inputCity, inputCountry, inputZip, final_price]:
            if len(v.split()) == 0:
                return redirect('cart')
        
        current_bill, _, _ = get_cart(request)
        status = get_object_or_404(Status, name='processing')
        
        with transaction.atomic():
            new_bill, notExist = Bill.objects.get_or_create(
                user = request.user,
                recipient = inputName,
                phone_number = inputPhoneNo,
                address = inputAddress,
                city = inputCity,
                country = inputCountry,
                zip_code = inputZip,
                total = final_price,
                shipping_note = inputShipNote,
                status = status,
            )
            Item.objects.filter(bill=current_bill).update(bill=new_bill)

        context = {
            "order" : new_bill,
        }

        return render(request,'cart/payment.html', context)
    else:
        messages.error(request, _(f"Bill checkout processing failed."))
        return redirect('index')
