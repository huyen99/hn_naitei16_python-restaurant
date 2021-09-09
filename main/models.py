from django.db import models
from django.db.models.deletion import SET_NULL
from django.db.models.fields import BooleanField, SmallIntegerField, TextField
from django.urls import reverse
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MaxValueValidator, MinValueValidator 
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
import collections

class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )
        
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_staff = True
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Notify(models.Model):
    message = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    duration = models.TimeField(null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "notifies"

class User(AbstractUser):
    email = models.EmailField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=12, null=True, blank=True)
    address = models.CharField(max_length=255,null=True, blank=True)
    avatar_url = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    zip_code = models.CharField(max_length=100, null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    food_saved = models.ManyToManyField('Food', blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] # Email & Password are required by default.

    objects = UserManager()

    def __str__(self):
        """String for representing the User Model object."""
        return f'{self.last_name} {self.first_name}' if self.last_name and self.first_name else self.username

@receiver(post_save, sender=User)
def create_cart(sender, instance, created, **kwargs):
    # Create a bill with `cart` status for new user
    if created:
        status, notExist = Status.objects.get_or_create(name='cart')
        Bill.objects.create(user=instance, status=status)

class Food(models.Model):
    name = models.CharField(max_length=45)
    description = models.TextField(null=True, blank=True)
    price = models.FloatField()
    discount = models.FloatField(null=True, blank=True)
    order_count = models.IntegerField(default=0)

    def __str__(self):
        """String for representing the Model object."""
        return self.name
        
    class Meta:
        verbose_name_plural = "foods"

class Review(models.Model):
    comment = models.TextField()
    rating = models.SmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    user = models.ForeignKey('User', on_delete=models.CASCADE, null=True)
    food = models.ForeignKey('Food', on_delete=models.CASCADE, null=True)
    date_created = models.DateTimeField(default=timezone.now)
    
class Reply(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, null=True)
    parent = models.ForeignKey('Review', on_delete=models.CASCADE, null=True)
    content = models.TextField()
    date_created = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name_plural = "replies"

class Image(models.Model):
    food = models.ForeignKey('Food', on_delete=models.CASCADE, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        """String for representing the Model object."""
        return self.url

class Coupon(models.Model):
    code = models.CharField(max_length=50)
    value = models.FloatField()
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        """String for representing the Model object."""
        return self.code

class Status(models.Model):
    name = models.CharField(unique=True, null=True, max_length=50)
    description = models.CharField(null=True, blank=True, max_length=255)

    def __str__(self):
        """String for representing the Model object."""
        return self.name
    
    class Meta:
        verbose_name_plural = "statuses"

class Bill(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    total = models.FloatField(default=0)
    order_date = models.DateTimeField(default=timezone.now)
    received_date = models.DateTimeField(null=True, blank=True)
    recipient = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=12)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=100, null=True)
    zip_code = models.CharField(max_length=100, null=True)
    delivery_charges = models.DecimalField(default=0, max_digits=15, decimal_places=2)
    shipping_note = models.TextField(null=True, blank=True)
    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.ForeignKey('Status', on_delete=models.SET_NULL, null=True)
    rzp_id = models.CharField(max_length=255, default='')
    rzp_payment_id = models.CharField(max_length=255, default='')
    rzp_signature = models.CharField(max_length=255, default='')

    def __str__(self):
        """String for representing the Model object."""
        return str(self.id)

class Item(models.Model):
    unit_price = models.FloatField()
    quantity = models.IntegerField()
    note = models.TextField(null=True, blank=True)
    food = models.ForeignKey('Food', on_delete=models.CASCADE, null=True)
    bill = models.ForeignKey('Bill', on_delete=models.SET_NULL, null=True)
