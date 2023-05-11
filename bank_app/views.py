from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.edit import CreateView
from . forms import DepositForm , WithdrawForm
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.list import ListView
from .models import Transction
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.db import transaction
from django.contrib import messages

# Create your views here.

def home(request):
    return render(request,"b_base.html")

class DepositView(SuccessMessageMixin,CreateView):
    form_class = DepositForm
    template_name = "deposit.html"
    success_url = reverse_lazy('bank_app:deposit')
    success_message = "Successfully Deposit Amount !"
    
    def form_valid(self,form):
        amount = self.request.POST.get("amount")
        form.instance.user = self.request.user
        form.instance.transction_type = Transction.type[0][0]
        last_amount = Transction.objects.filter(user=self.request.user).last()
        if last_amount:
            form.instance.balance_after_transaction= int(amount) + last_amount.balance_after_transaction
        else:
            form.instance.balance_after_transaction = int(amount)
        return super().form_valid(form)

class WithdrawView(SuccessMessageMixin,CreateView):
    form_class = WithdrawForm
    template_name = "withdraw.html"
    success_url = reverse_lazy('bank_app:withdraw')
    success_message = "Successfully Withdraw Amount !"

    def form_valid(self,form):
        amount = self.request.POST.get("amount")
        form.instance.user = self.request.user
        form.instance.transction_type = Transction.type[1][1]
        last_amount =Transction.objects.filter(user=self.request.user).last()
        if last_amount:
            form.instance.balance_after_transaction = last_amount.balance_after_transaction - int(amount) 
        else:
            form.instance.balance_after_transaction = int(amount)
        return super().form_valid(form)
    
class ReportView(ListView):
    model = Transction
    template_name = "report.html"
    context_object_name = "tran_report"

    def get_queryset(self):
        trans = Transction.objects.all() 
        return trans if self.request.user.is_manager==True else Transction.objects.filter(user=self.request.user)
        
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        last_amount = Transction.objects.all() 
        last_amount = last_amount if self.request.user.is_manager==True else Transction.objects.filter(user=self.request.user).last()

        if last_amount:
            if self.request.user.is_manager==True:
                context['total'] = ''
            else: 
                context['total'] = last_amount.balance_after_transaction
            return context
        else:
            return None

def TransferAmountView(request):
    if request.method == "POST":
        try:
            send = request.POST.get("send")
            amount = request.POST.get("amount")

            with transaction.atomic():
                user1 = Transction.objects.filter(user=request.user).last()

                if user1.balance_after_transaction >= int(amount):
                    user1.transction_type = Transction.type[1][1]   
                    user1.balance_after_transaction-= int(amount)
                    user1.user = request.user
                    user1.amount = int(amount)
                    user1.save()
                    
                else:
                    messages.success(request,'Not Enough Balance!')
               
                user2 = Transction.objects.filter(user__account_number=send).last()
                user2.balance_after_transaction+=int(amount)
                user2.transction_type = Transction.type[0][0]
                user2.amount = int(amount)
                user2.save()
                messages.success(request,'Successfully your Amount is transfered')
        except Exception as e:
            print(e) 
            messages.success(request,'Something went wrong!')
    return render(request,"transfer.html")







     