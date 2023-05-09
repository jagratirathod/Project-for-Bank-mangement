from django import  forms
from .models import User
from django.contrib.auth.forms import UserCreationForm

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email","password1","password2","first_name","last_name",'account_number')


class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("email", "password")
