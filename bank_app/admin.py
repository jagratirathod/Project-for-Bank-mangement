from django.contrib import admin
from . models import Transction, BankAccounts


# Register your models here.


class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'transction_type', 'current_time', 'user',
                    'amount', 'amount_type', 'sender', 'recipient']


admin.site.register(Transction, TransactionAdmin)


class BankAccountsAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'payee', 'nickname']


admin.site.register(BankAccounts, BankAccountsAdmin)
