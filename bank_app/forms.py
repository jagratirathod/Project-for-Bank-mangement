from django import forms
from .models import Transction, BankAccounts
from django.core.exceptions import ValidationError


class DepositForm(forms.ModelForm):
    class Meta:
        model = Transction
        fields = ("amount",)

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if not amount > 0:
            raise ValidationError("Amount should be Positive Number")
        return amount


class WithdrawForm(forms.ModelForm):
    class Meta:
        model = Transction
        fields = ("amount",)

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if not amount > 0:
            raise ValidationError("Amount should be Positive Number")
        return amount


class BankAccountForm(forms.ModelForm):
    account_number = forms.CharField(max_length=20)

    class Meta:
        model = BankAccounts
        fields = ("nickname",)
