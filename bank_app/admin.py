from django.contrib import admin
from . models import Transction

# Register your models here.


class TransctionAdmin(admin.ModelAdmin):
    list_display = ['transction_type', 'current_time', 'user',
                    'amount', 'amount_type']


admin.site.register(Transction, TransctionAdmin)
