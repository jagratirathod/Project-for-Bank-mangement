from django import  forms
from .models import Transction

class DepositForm(forms.ModelForm):
    class Meta:
        model = Transction
        fields = ("amount",)
