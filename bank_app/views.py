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
    transaction = Transction.objects.filter(user=request.user).first()
    if transaction is not None:
        balance = transaction.balance
    else:
        balance = 0
    return render(request, "home.html", {"balance": balance})


class DepositView(SuccessMessageMixin, CreateView):
    form_class = DepositForm
    template_name = "deposit.html"
    success_url = reverse_lazy('bank_app:deposit')
    success_message = "Successfully Deposit Amount !"

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.transction_type = Transction.TRANSACTION_TYPE_CHOICES[0][0]
        return super().form_valid(form)


class WithdrawView(SuccessMessageMixin, CreateView):
    form_class = WithdrawForm
    template_name = "withdraw.html"
    success_url = reverse_lazy('bank_app:withdraw')
    success_message = "Successfully Withdraw Amount !"

    def form_valid(self, form):
        amount = self.request.POST.get("amount")
        balance = Transction.objects.filter(
            user=self.request.user).first().balance
        if balance < int(amount):
            messages.error(
                self.request, "Low balance. Unable to withdraw amount.")
            return self.form_invalid(form)
        form.instance.user = self.request.user
        form.instance.transction_type = Transction.TRANSACTION_TYPE_CHOICES[1][1]
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
        transaction = Transction.objects.filter(
            user=self.request.user).first()

        if transaction and transaction.balance:
            context['balance'] = transaction.balance
        else:
            context['balance'] = 0
        return context


def TransferAmountView(request):
    if request.method == "POST":
        try:
            send = request.POST.get("send")
            amount = request.POST.get("amount")

            with transaction.atomic():
                balance = Transction.objects.filter(
                    user=request.user).first().balance
                if balance > int(amount):
                    trans = Transction.objects.create(
                        transction_type=Transction.TRANSACTION_TYPE_CHOICES[2][0], user=request.user, amount=int(amount))
                else:
                    return render(request, "transfer.html", {'error_message': 'Insufficient Balance!'})

                user2 = User.objects.filter(Q(account_number=send) & ~Q(
                    account_number=request.user.account_number)).last()
                trans = Transction.objects.create(
                    transction_type=Transction.TRANSACTION_TYPE_CHOICES[3][0], user=user2, amount=int(amount))
                messages.success(
                    request, 'Successfully your Amount is transfered')
        except Exception as e:
            print(e)
            messages.error(request, 'Account Number does not Exists!')
    return render(request, "transfer.html")
