from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.utils.translation import ugettext_lazy as _
from django.db.models import Avg, Q, Func
from django.forms import modelform_factory
from django.db import transaction
from django.core import serializers
from django.conf import settings
from django.forms.models import model_to_dict
import functools
import copy
import json
import re
import razorpay
from decimal import Decimal
from .models import Food, Review, Reply, Bill, Item, Status, User
from .forms import UserRegisterForm
from .utils.constant import RATE_TEMPLATE, PHONE_NUMBER_VALIDATOR

def get_cart(request):
    bill, cart_items, in_cart = None, None, []
    if request.user.is_authenticated:
        status = get_object_or_404(Status, name='cart')
        bill = Bill.objects.prefetch_related('item_set').filter(user=request.user, status=status).first()
        cart_items = bill.item_set.all()
        in_cart = [item.food for item in cart_items]
    
    return bill, cart_items, in_cart
    
def count_rating(reviews):
    # Copy constant to another dict to reset dict value on page refresh
    _rate = copy.deepcopy(RATE_TEMPLATE)
    
    # How many reviews per star?
    for review in reviews:
        i = review.rating
        if i in _rate:
            _rate[i][1] += 1
            _rate[i][2] = int(_rate[i][1]/len(reviews) * 100)
    
    return _rate

def index(request):
    foods = Food.objects.prefetch_related('image_set').annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')
    query = ''
    wishlist = None
    if request.user.is_authenticated:
        wishlist = request.user.food_saved.all()

    if request.method == 'GET' and 'query' in request.GET:
        query = request.GET['query'].strip()
        keywords = query.split()
        # Search for each keyword in query. For example: "sushi pizza"
        foods = foods.filter(functools.reduce(lambda x, y: x | y, [Q(name__icontains=word) for word in keywords]))

    bill, _, in_cart = get_cart(request)

    context = {
        "foods": foods,
        "keyword": query,
        "in_cart": in_cart,
        "wishlist": wishlist,
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

class Round(Func):
    function = 'ROUND'
    template='%(function)s(%(expressions)s, 2)'

def food_details(request, id):
    food = Food.objects.prefetch_related('review_set').annotate(avg_rating=Round(Avg('review__rating'))).filter(id=id).first()
    _, _, in_cart = get_cart(request)
    reviews = food.review_set.all()
    _rate = count_rating(reviews)
    wishlist = None
    if request.user.is_authenticated:
        wishlist = request.user.food_saved.all()

    context = {
        "food": food,
        "rate_dict": _rate,
        "in_cart": in_cart,
        "wishlist": wishlist,
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
def delete_review(request, id):
    success = False
    review = Review.objects.filter(id=id).first()
    food_id = review.food.id

    if review.delete():
        success = True

    food = Food.objects.prefetch_related('review_set').annotate(avg_rating=Round(Avg('review__rating'))).filter(id=food_id).first()
    reviews = food.review_set.all()
    _rate = count_rating(reviews)

    context = {
        "success": success,
        "new_average": food.avg_rating,
        "rate_dict": _rate,
    }

    return JsonResponse(context)

@login_required
def delete_reply(request, id):
    success = False
    if Reply.objects.filter(id=id).delete():
        success = True
    
    context = {
        "success": success,
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
    if request.method == "POST":
        if request.POST.get('password-reset'):
            form = PasswordChangeForm(user=request.user, data=request.POST)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user)
                messages.success(request, _("Your password was successfully updated."))
            messages.warning(request, form.errors)

        else:
            UserEditForm = modelform_factory(
                User, 
                fields=('first_name', 'last_name', 'phone_number', 'address', 'city', 'country', 'zip_code'), 
            )
            form = UserEditForm(instance=request.user, data=request.POST or None)
            if form.is_valid():
                pattern = re.compile(PHONE_NUMBER_VALIDATOR)
                phone = form.cleaned_data['phone_number']
                if phone and not pattern.search(phone):
                    form.add_error('phone_number', _("Your phone number is invalid."))
                else:
                    form.save()
                    messages.success(request, _("Your information was succesfully updated."))
            messages.warning(request, form.errors)

        return redirect('profile')

    else:
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
        final_price = Decimal(final_price * bill.coupon.value) + bill.delivery_charges
    else:
        final_price = Decimal(final_price) + bill.delivery_charges
        
    context = {
        "fprice": final_price
    }

    return render(request, 'cart/checkout.html', context)

@login_required
def handle_checkout(request, id):
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
        
    elif request.method == "GET":
        bill = get_object_or_404(Bill, id=id)
        
        context = {
            "order" : bill,
        }

        return render(request,'cart/payment.html', context)
    
    else:
        messages.error(request, _(f"Bill checkout processing failed."))
        return redirect('index')

@login_required
def cancel_order(request):
    success = False
    new_status = ''
    order_id = request.POST.get('uuid')
    order = Bill.objects.prefetch_related('item_set').filter(user=request.user, id=order_id).first()
    cancelled_status, notExist = Status.objects.get_or_create(name='cancelled')
    if order and cancelled_status:
        order.status = cancelled_status
        order.save()
        success = True
        new_status = cancelled_status.name
        
    context = {
        "success": success,
        "new_status": new_status,
    }
    return JsonResponse(context)

@login_required
def open_payment(request):
    if request.method == "POST":
        language = request.POST.get('lang')
        order_id = request.POST.get('order_id')
        current_order = get_object_or_404(Bill, id=order_id)
        order_total = current_order.total
        order_currency = 'USD'
        callback_url = f'http://localhost:8000{language}handle-payment/'
        order_receipt = order_id
        notes = {
            'recipient': current_order.recipient,
            'shipping_address': current_order.address,
            'phone_number': current_order.phone_number,
            'city': current_order.city,
            'country': current_order.country,
            'zip_code': current_order.zip_code,
            'shipping_note': current_order.shipping_note,
        }
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        payment = client.order.create(dict(amount=order_total, currency=order_currency, receipt=order_receipt, notes=notes, payment_capture=0))
        current_order.rzp_id = payment['id']
        current_order.save()

        context = {
            "order_id": order_id,
            "rp_order_id": payment['id'],
            "order": model_to_dict(current_order),
            "email": request.user.email,
            "amount": current_order.total,
            "razorpay_id": settings.RAZORPAY_KEY_ID,
            "callback_url": callback_url,
        }
        
        return JsonResponse(context)

@csrf_exempt
def handle_payment(request):
    if request.method == "POST":
        rzp_payment_id = request.POST.get('razorpay_payment_id', '')
        rzp_id = request.POST.get('razorpay_order_id', '')
        rzp_signature = request.POST.get('razorpay_signature', '')
        params_dict = {
            'razorpay_order_id': rzp_id,
            'razorpay_payment_id': rzp_payment_id,
            'razorpay_signature': rzp_signature,
        }
        order_db = get_object_or_404(Bill, rzp_id=rzp_id)
        order_db.rzp_payment_id = rzp_payment_id
        order_db.rzp_signature = rzp_signature
        order_db.save()
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        result = client.utility.verify_payment_signature(params_dict)

        if result == None:
            amount = order_db.total
            try:
                client.payment.capture(rzp_payment_id, amount)
                purchased = get_object_or_404(Status, name='purchased')
                order_db.status = purchased
                order_db.save()
                extra = {
                    'order_id': order_db.rzp_id,
                }
                return render(request, 'cart/payment_success.html', extra)
            except:
                payment_failed = get_object_or_404(Status, name='payment failed')
                order_db.status = payment_failed
                order_db.save()
                return render(request, 'cart/payment_failed.html')
        else:
            payment_failed = get_object_or_404(Status, name='payment failed')
            order_db.status = payment_failed
            order_db.save()
            return render(request, 'cart/payment_failed.html')

@login_required
def wishlist(request):
    user = request.user
    wishlist = user.food_saved.annotate(avg_rating=Avg('review__rating')).all()
    _, _, in_cart = get_cart(request)

    context = {
        "wishlist": wishlist,
        "in_cart": in_cart
    }
    return render(request, 'accounts/wishlist.html', context)
    
@login_required
def add_to_wishlist(request):
    '''Add/remove from menu view'''
    if request.method == "POST":
        action = ''
        user = request.user
        food = get_object_or_404(Food, id=request.POST.get('food_id'))

        if user.food_saved.filter(id=food.id).exists():
            user.food_saved.remove(food)
            action = 'remove'
        else:
            user.food_saved.add(food)
            action = 'add'

        context = {
            "action": action,
        }

        return JsonResponse(context)

@login_required
def remove_from_wishlist(request, id):
    '''Remove from wishlist view'''
    if request.method == "DELETE":
        success = False
        user = request.user
        food = get_object_or_404(Food, id=id)
        try:
            user.food_saved.remove(food)
            success = True
        except:
            messages.error(request, _(f"Failed removing item from wishlist."))

        context = {
            "success": success,
        }
        return JsonResponse(context)
