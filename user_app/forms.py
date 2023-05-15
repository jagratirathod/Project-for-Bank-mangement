from django import  forms
from .models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email","password1","password2","first_name","last_name")

    def clean_account_number(self):
        account_number = str(self.cleaned_data['account_number'])
        if len(account_number)!=12:
            raise ValidationError("Account Number should be of 12 digit")
        return account_number
    
class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("email", "password")
