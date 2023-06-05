from bank_app.models import BankAccounts, Transction
from django.db import transaction
from django.db.models import Q, Sum, Value
from django.db.models.functions import Concat
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from user_app.models import User

from .serializers import (BalanceUserSerializer, BankAccountSerializer,
                          DepositSerializer, ReportSerializer,
                          TransctionSerializer, TransferamountSerializer,
                          WithdrawSerializer)

# Create your views here.


class Home(APIView):
    # GET -  http://localhost:8000/bank_api/
    def get(self, request):
        return HttpResponse("bank api testing")


class DepositView(viewsets.ModelViewSet):
    # POST - http://localhost:8000/api/deposit/
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Transction.objects.all()
    serializer_class = DepositSerializer
    http_method_names = ['post']

    def perform_create(self, serializer):
        serializer.save(transction_type=Transction.TRANSACTION_TYPE_CHOICES[0][0],
                        amount_type=Transction.AMOUNT_TYPE_CHOICES[0][0],
                        user=self.request.user
                        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"user": self.request.user})
        return context


class WithdrawView(viewsets.ModelViewSet):
    # POST -http://localhost:8000/api/withdraw/
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Transction.objects.all()
    serializer_class = WithdrawSerializer
    http_method_names = ['post']

    def perform_create(self, serializer):
        serializer.save(
            transction_type=Transction.TRANSACTION_TYPE_CHOICES[1][1],
            amount_type=Transction.AMOUNT_TYPE_CHOICES[1][1],
            user=self.request.user
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"user": self.request.user})
        return context


class ReportView(viewsets.ModelViewSet):
    # GET - http://localhost:8000/api/report/
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ReportSerializer
    http_method_names = ['get']

    def get_queryset(self):
        queryset = Transction.objects.filter(
            user=self.request.user).order_by('-id')
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        transaction = Transction.objects.filter(
            user=self.request.user).first()

        if transaction and transaction.balance:
            context['balance'] = transaction.balance
        else:
            context['balance'] = 0
        return context


class BalanceUserView(ListAPIView):
    # GET - localhost:8000/bank_api/balance_user/
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = BalanceUserSerializer
    queryset = Transction.objects.all()

    def get_queryset(self):
        if self.request.user.is_manager == True:
            queryset = []

            for user in User.objects.all().exclude(email=self.request.user):
                credits = Transction.objects.filter(
                    user=user, amount_type="Credit").aggregate(balance=Sum('amount'))['balance'] or 0

                debits = Transction.objects.filter(
                    user=user, amount_type="Debit").aggregate(balance=Sum('amount'))['balance'] or 0
                balance = credits - debits

                data = {
                    'user': user,
                    'balance': balance,
                }
                queryset.append(data)
            return queryset


class AddBankAccountView(viewsets.ModelViewSet):
    # POST - http://localhost:8000/api/bank_account/
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = BankAccountSerializer
    http_method_names = ['post']

    def perform_create(self, serializer):
        account_number = self.request.data["account_number"]
        user = User.objects.filter(account_number=account_number).first()

        bank = BankAccounts.objects.filter(
            user=self.request.user, payee=user)
        if bank.exists():
            raise ValidationError(
                "User with this account number already exist!")
        if user:
            serializer.save(user=self.request.user, payee=user)

        else:
            raise ValidationError(
                "User with this account number does not exist.")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"account_number": self.request.data["account_number"]})
        return context


class ListBankAccountView(ListAPIView):
    # GET - localhost:8000/bank_api/list_bank_account/
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = BankAccounts.objects.all()
    serializer_class = BankAccountSerializer

    def get_queryset(self):
        queryset = BankAccounts.objects.filter(
            user=self.request.user)
        return queryset


class AccountdeleteView(DestroyAPIView):
    # Delete -localhost:8000/bank_api/delete_bank_account/24/
    queryset = BankAccounts
    serializer_class = BankAccountSerializer


class TransactionHistoryView(ListAPIView):
    # GET - localhost:8000/bank_api/transction_history/?account_number=889652310478
    queryset = Transction.objects.all()
    serializer_class = TransctionSerializer

    def get_queryset(self):
        acc = self.request.GET.get("account_number")
        user_name = User.objects.annotate(full_name=Concat('first_name', Value(
            ' '), 'last_name')).filter(account_number=acc).values_list('full_name').first()
        trans = Transction.objects.filter(
            Q(user=self.request.user) & Q(
                recipient__in=user_name) | Q(sender__in=user_name))
        return trans


class TransferamountView(CreateAPIView):
    # POST  - localhost:8000/bank_api/tranfer/?account_number=720961087582
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Transction.objects.all()
    serializer_class = TransferamountSerializer

    def create(self, request, *args, **kwargs):
        account_number = self.request.GET.get("account_number")
        amount = self.request.data["amount"]

        if int(amount) > 4000:
            return Response("Maximum transfer limit is 4000!")

        # check total amount of 24hours
        today = timezone.now().date()
        total_withdrawal = Transction.objects.filter(
            user=request.user, transction_type=Transction.TRANSACTION_TYPE_CHOICES[2][0], current_time__date=today).aggregate(Sum('amount'))['amount__sum'] or 0

        if total_withdrawal + int(amount) > 25000:
            return Response("You have reached the maximum daily withdrawal limit of 25,000.")

        try:
            with transaction.atomic():
                balance = Transction.objects.filter(
                    user=self.request.user).first().balance
                if balance > int(amount):
                    sender_transaction = Transction.objects.create(
                        transction_type=Transction.TRANSACTION_TYPE_CHOICES[2][0], user=self.request.user, amount=int(amount))
                else:
                    return Response("Insufficient Balance!")

                user2 = User.objects.filter(
                    Q(account_number=account_number) & ~Q(account_number=self.request.user.account_number)).last()

                recipient_transaction = Transction.objects.create(
                    transction_type=Transction.TRANSACTION_TYPE_CHOICES[3][0], user=user2, amount=int(amount))

                sender_transaction.recipient = user2.first_name + " " + user2.last_name
                sender_transaction.save()

                recipient_transaction.sender = self.request.user.first_name + \
                    " " + self.request.user.last_name
                recipient_transaction.save()
                return Response("Transaction successful", status=status.HTTP_201_CREATED)

        except Exception as e:
            print(e)
            return Response("Account Number does not Exists!")
