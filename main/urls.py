from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='accounts/logout.html'), name='logout'),
    path('register/', views.register, name='register'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
    path('search/', views.index, name='search'),
    path('food/<int:id>/details/', views.food_details, name='food-details'),
    path('food/<int:id>/details/review/', views.review, name='review'),
    path('food/<int:food_id>/details/review/<int:review_id>/reply/', views.reply, name='reply'),
    path('delete-review/<int:id>', views.delete_review, name="delete-review"),
    path('delete-reply/<int:id>', views.delete_reply, name="delete-reply"),
    path('cart/', views.cart, name="cart"),
    path('add-to-cart/', views.add_to_cart, name="add-to-cart"),
    path('remove-from-cart/<id>', views.remove_from_cart, name="remove-from-cart"),
    path('profile/', views.profile, name='profile'),
    path('checkout/', views.checkout, name="checkout"),
    path('handle-checkout/', views.handle_checkout, name="handle-checkout"),
    path('payment/<uuid:id>', views.handle_checkout, name="payment"),
    path('cancel-order/', views.cancel_order, name="cancel-order"),
    path('open-payment/', views.open_payment, name="open-payment"),
    path('handle-payment/', views.handle_payment, name="handle-payment"),
    path('wishlist/', views.wishlist, name="wishlist"),
    path('add-to-wishlist/', views.add_to_wishlist, name="add-to-wishlist"),
    path('remove-from-wishlist/<int:id>', views.remove_from_wishlist, name="remove-from-wishlist"),
]
