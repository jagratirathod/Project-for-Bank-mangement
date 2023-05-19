from django.db import models
from user_app.models import User
from django.db.models import Sum

# Create your models here.


class Transction(models.Model):

    TRANSACTION_TYPE_CHOICES = (
        ('Deposit', 'Deposit'),
        ('Withdrawal', 'Withdrawal'),
        ('Transfer', 'Transfer'),
        ('Receive', 'Receive'),
    )

    AMOUNT_TYPE_CHOICES = (
        ('Credit', 'Credit'),
        ('Debit', 'Debit'),
    )
    amount_type = models.CharField(
        max_length=20, choices=AMOUNT_TYPE_CHOICES, null=True, blank=True)
    transction_type = models.CharField(
        max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    current_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(decimal_places=2, max_digits=12)

    def __int__(self):
        return self.amount

    def save(self, *args, **kwargs):
        if self.transction_type in ['Deposit', 'Receive']:
            self.amount_type = Transction.AMOUNT_TYPE_CHOICES[0][0]
        else:
            self.amount_type = Transction.AMOUNT_TYPE_CHOICES[1][1]
        super().save(*args, **kwargs)

    # def calculate_balance(user):                                                //function
    #     transactions = Transction.objects.filter(user=user)
    #     balance = 0
    #     for transaction in transactions:
    #         if transaction.amount_type == 'Credit':
    #             balance += transaction.amount
    #         elif transaction.amount_type == 'Debit':
    #             balance -= transaction.amount
    #     return balance

    # @property                                                                    //@property using for loop
    # def balance(self):
    #     transactions = Transction.objects.filter(user=self.user)
    #     balance = 0
    #     for transaction in transactions:
    #         if transaction.amount_type == 'Credit':
    #             balance += transaction.amount
    #         elif transaction.amount_type == 'Debit':
    #             balance -= transaction.amount
    #     return balance

    @property
    def balance(self):
        credits = Transction.objects.filter(
            user=self.user, amount_type="Credit").aggregate(balance=Sum('amount'))['balance'] or 0

        debit = Transction.objects.filter(
            user=self.user, amount_type="Debit").aggregate(balance=Sum('amount'))['balance'] or 0
        balance = credits - debit
        return balance
