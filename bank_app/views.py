from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from user_app.models import User

from .forms import DepositForm, WithdrawForm
from .models import Transction


def home(request):
    return render(request, "b_base.html")


class DepositView(SuccessMessageMixin, CreateView):
    form_class = DepositForm
    template_name = "deposit.html"
    success_url = reverse_lazy('bank_app:deposit')
    success_message = "Successfully Deposit Amount !"

    def form_valid(self, form):
        amount = self.request.POST.get("amount")
        form.instance.user = self.request.user
        form.instance.transction_type = Transction.TRANSACTION_TYPE_CHOICES[0][0]
        last_amount = Transction.objects.filter(user=self.request.user).last()
        if last_amount:
            form.instance.balance_after_transaction = int(
                amount) + last_amount.balance_after_transaction
        else:
            form.instance.balance_after_transaction = int(amount)
        return super().form_valid(form)


class WithdrawView(SuccessMessageMixin, CreateView):
    form_class = WithdrawForm
    template_name = "withdraw.html"
    success_url = reverse_lazy('bank_app:withdraw')
    success_message = "Successfully Withdraw Amount !"

    def form_valid(self, form):
        amount = self.request.POST.get("amount")
        form.instance.user = self.request.user
        form.instance.transction_type = Transction.TRANSACTION_TYPE_CHOICES[1][1]

        last_amount = Transction.objects.filter(user=self.request.user).last()
        if last_amount:
            if last_amount.balance_after_transaction >= int(amount):
                form.instance.balance_after_transaction = last_amount.balance_after_transaction - \
                    int(amount)
            else:
                return render(self.request, "withdraw.html", {'form': form, 'error_message': 'Insufficient Balance!'})
        else:
            return render(self.request, "withdraw.html", {'form': form, 'error_message': 'Low Balance!'})
        return super().form_valid(form)


class ReportView(ListView):
    model = Transction
    template_name = "report.html"
    context_object_name = "tran_report"

    def get_queryset(self):
        trans = Transction.objects.all()
        return trans if self.request.user.is_manager == True else Transction.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        last_amount = Transction.objects.all()
        last_amount = last_amount if self.request.user.is_manager == True else Transction.objects.filter(
            user=self.request.user).last()

        if last_amount:
            if self.request.user.is_manager == True:
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
                    user1.balance_after_transaction -= int(amount)
                    trans = Transction.objects.create(transction_type=Transction.TRANSACTION_TYPE_CHOICES[2][0], user=request.user, amount=int(
                        amount), balance_after_transaction=user1.balance_after_transaction)
                else:
                    return render(request, "transfer.html", {'error_message': 'Insufficient Balance!'})

                user2 = User.objects.filter(Q(account_number=send) & ~Q(
                    account_number=request.user.account_number)).last()
                if user2.transactions.last():
                    last_amount = user2.transactions.last().balance_after_transaction
                    last_amount += int(amount)
                    trans = Transction.objects.create(transction_type=Transction.TRANSACTION_TYPE_CHOICES[3][0], user=user2, amount=int(
                        amount), balance_after_transaction=last_amount)
                else:
                    trans = Transction.objects.create(transction_type=Transction.TRANSACTION_TYPE_CHOICES[3][0], user=user2, amount=int(
                        amount), balance_after_transaction=amount)
                messages.success(
                    request, 'Successfully your Amount is transfered')
        except Exception as e:
            print(e)
            messages.error(request, 'Account Number does not Exists!')
    return render(request, "transfer.html")
