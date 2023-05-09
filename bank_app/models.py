from django.db import models
from user_app.models import User

# Create your models here.

class Transction(models.Model):
    type = (('credit', 'credit'),
            ('debit', 'debit')
            )
    transction_type = models.CharField(max_length=20,choices=type)
    current_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2,max_digits=12)
    balance_after_transaction = models.DecimalField(decimal_places=2,max_digits=12,default=0)

    def __int__(self):
        return self.user.account_number


class bank_Transction(models.Model):
    pass
