from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.db.models import Q, Sum, Value
from django.db.models.functions import Concat
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.list import ListView
from user_app.models import User

from .forms import BankAccountForm, DepositForm, WithdrawForm
from .models import BankAccounts, Transction


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
        amount = self.request.POST.get("amount")
        if int(amount) > 5000:
            messages.error(
                self.request, "You can deposit up to 5000 at a time.")
            return self.form_invalid(form)

        # check total amount of 24 hours
        today = timezone.now().date()
        total_withdrawal = Transction.objects.filter(
            user=self.request.user, transction_type=Transction.TRANSACTION_TYPE_CHOICES[0][0], current_time__date=today).aggregate(Sum('amount'))['amount__sum'] or 0
        if total_withdrawal + int(amount) > 20000:
            messages.error(
                self.request, "You have reached the maximum daily withdrawal limit of 20,000.")
            return self.form_invalid(form)

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
        trans = Transction.objects.filter(
            user=self.request.user).first()

        if int(amount) > 10000:
            messages.error(
                self.request, "You can withdraw up to 10,000 at a time.")
            return self.form_invalid(form)

        if trans.balance < int(amount):
            messages.error(
                self.request, "Low balance. Unable to withdraw amount.")
            return self.form_invalid(form)

        # check total amount of 24hours
        today = timezone.now().date()
        total_withdrawal = Transction.objects.filter(
            user=self.request.user, transction_type=Transction.TRANSACTION_TYPE_CHOICES[1][1], current_time__date=today).aggregate(Sum('amount'))['amount__sum'] or 0
        if total_withdrawal + int(amount) > 30000:
            messages.error(
                self.request, "You have reached the maximum daily withdrawal limit of 30,000.")
            return self.form_invalid(form)

        form.instance.user = self.request.user
        form.instance.transction_type = Transction.TRANSACTION_TYPE_CHOICES[1][1]
        return super().form_valid(form)


class ReportView(ListView):
    model = Transction
    context_object_name = "tran_report"
    template_name = "report.html"

    def get_queryset(self):
        return Transction.objects.filter(user=self.request.user).order_by('-current_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transaction = Transction.objects.filter(
            user=self.request.user).first()
        if transaction and transaction.balance:
            context['balance'] = transaction.balance
        else:
            context['balance'] = 0
        return context


class BalanceUserView(ListView):
    model = Transction
    context_object_name = "combined_data"
    template_name = "report_manager.html"

    def get_queryset(self):
        if self.request.user.is_manager == True:
            balances = []

            for user in User.objects.all().exclude(email=self.request.user):
                credits = Transction.objects.filter(
                    user=user, amount_type="Credit").aggregate(balance=Sum('amount'))['balance'] or 0

                debits = Transction.objects.filter(
                    user=user, amount_type="Debit").aggregate(balance=Sum('amount'))['balance'] or 0
                balance = credits - debits
                balances.append(balance)
                combined_data = zip(User.objects.all().exclude(
                    email=self.request.user), balances)
            return combined_data


def transfer_amountView(request):
    user2 = None
    if request.method == "POST":
        try:
            send = request.GET.get("send")
            amount = request.POST.get("amount")

            if int(amount) > 4000:
                return render(request, "transfer.html", {'error_message': 'Maximum transfer limit is 4000!'})

            # check total amount of 24hours
            today = timezone.now().date()
            total_withdrawal = Transction.objects.filter(
                user=request.user, transction_type=Transction.TRANSACTION_TYPE_CHOICES[2][0], current_time__date=today).aggregate(Sum('amount'))['amount__sum'] or 0

            if total_withdrawal + int(amount) > 25000:
                return render(request, "transfer.html", {'error_message': 'You have reached the maximum daily withdrawal limit of 25,000.'})

            with transaction.atomic():
                tran = Transction.objects.filter(
                    user=request.user).first()
                if tran.balance > int(amount):
                    sender_transaction = Transction.objects.create(
                        transction_type=Transction.TRANSACTION_TYPE_CHOICES[2][0], user=request.user, amount=int(amount))
                else:
                    return render(request, "transfer.html", {'error_message': 'Insufficient Balance!'})

                user2 = User.objects.filter(
                    Q(account_number=send) & ~Q(account_number=request.user.account_number)).last()

                recipient_transaction = Transction.objects.create(
                    transction_type=Transction.TRANSACTION_TYPE_CHOICES[3][0], user=user2, amount=int(amount))

                sender_transaction.recipient = user2.first_name + " " + user2.last_name
                sender_transaction.save()

                recipient_transaction.sender = request.user.first_name + " " + request.user.last_name
                recipient_transaction.save()

                messages.success(
                    request, 'Successfully your Amount is transfered')
        except Exception as e:
            print(e)
            messages.error(request, 'Account Number does not Exists!')
    else:
        send = request.GET.get("send")
        user2 = User.objects.filter(Q(account_number=send)).last()
        if user2:
            return render(request, "transfer.html", {"user_name": user2.first_name})
    return render(request, "transfer.html")


class AddBankAccountView(SuccessMessageMixin, CreateView):
    form_class = BankAccountForm
    template_name = "account_create.html"
    success_url = reverse_lazy('bank_app:list_account')
    success_message = "Successfully  Added"

    def form_valid(self, form):
        form.instance.user = self.request.user
        account_number = form.cleaned_data['account_number']
        user = User.objects.filter(Q(account_number=account_number) & ~Q(
            account_number=self.request.user.account_number)).first()
        if not user:
            return render(self.request, "account_create.html", {'error_message': "Account Number does not exists", "form": form})
        form.instance.payee = user
        bank = BankAccounts.objects.filter(
            user=self.request.user, payee=form.instance.payee)
        if bank.exists():
            return render(self.request, "account_create.html", {'error_message': "User with this account number already exists ", "form": form})
        return super().form_valid(form)


class ListBankAccountView(ListView):
    model = BankAccounts
    context_object_name = "bank_account"
    template_name = "account_list.html"

    # def get_queryset(self):
    #     return BankAccounts.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = BankAccounts.objects.filter(user=self.request.user)
        account_numbers = zip(BankAccounts.objects.filter(
            user=self.request.user).values_list('payee__account_number', flat=True), user)
        context['account_numbers'] = account_numbers
        return context


class Accountdelete(DeleteView):
    model = BankAccounts
    template_name = "account_delete.html"
    success_url = reverse_lazy("bank_app:list_account")


class TransactionHistoryView(View):
    template_name = "report.html"

    def get(self, request):
        acc = self.request.GET.get("account_number")
        user_name = User.objects.annotate(full_name=Concat('first_name', Value(
            ' '), 'last_name')).filter(account_number=acc).values_list('full_name').first()
        tran = Transction.objects.filter(
            Q(user=self.request.user) & Q(
                recipient__in=user_name) | Q(sender__in=user_name))
        context = {
            'tran_report': tran,
        }

        return render(request, self.template_name, context)
