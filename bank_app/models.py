from django.db import models
from user_app.models import User

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
    balance_after_transaction = models.DecimalField(
        decimal_places=2, max_digits=12, default=0)

    def __int__(self):
        return self.amount

    def save(self, *args, **kwargs):
        if self.transction_type in ['Deposit', 'Receive']:
            self.amount_type = Transction.AMOUNT_TYPE_CHOICES[0][0]
        else:
            self.amount_type = Transction.AMOUNT_TYPE_CHOICES[1][1]
        super().save(*args, **kwargs)
