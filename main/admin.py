from django.contrib import admin
from .models import Notify, User, Food, Review, Image, Coupon, Status, Bill, Item

admin.site.register(Status)

@admin.register(Notify)
class Notify(admin.ModelAdmin):
    list_display = ('message', 'is_active', 'duration', 'created_date')

@admin.register(User)
class User(admin.ModelAdmin):
    list_display = ('email', 'last_name', 'first_name', 'phone_number', 'address', 'is_admin', 'is_staff', 'is_active')

class ImageInline(admin.TabularInline):
    model = Image

@admin.register(Food)
class Food(admin.ModelAdmin):
    list_display = ('name', 'price', 'description', 'discount', 'order_count', 'rating')
    inlines = [ImageInline]

@admin.register(Review)
class Review(admin.ModelAdmin):
    list_display = ('user', 'food', 'rating', 'comment')

@admin.register(Coupon)
class Coupon(admin.ModelAdmin):
    list_display = ('code', 'value', 'is_active', 'start', 'end')

class ItemInline(admin.TabularInline):
    model = Item

@admin.register(Bill)
class Bill(admin.ModelAdmin):
    list_display = ('id', 'recipient', 'status', 'total', 'phone_number', 'address', 'order_date', 'received_date', 'coupon', 'shipping_note')
    inlines = [ItemInline]
