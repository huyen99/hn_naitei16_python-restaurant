from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _
from .models import User
from .utils.constant import PHONE_NUMBER_VALIDATOR as regex

class UserRegisterForm(UserCreationForm):
    phone_regex = RegexValidator(regex, message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."))
    phone_number = forms.CharField(required=False, validators=[phone_regex], max_length=17, label=_("Phone number"))
    address = forms.CharField(required=False, max_length=255, label=_("Address"))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'phone_number', 'address']
