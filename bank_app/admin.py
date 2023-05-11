from django.contrib import admin
from . models import Transction
# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display=['transction_type','current_time','user','amount','balance_after_transaction']
admin.site.register(Transction,UserAdmin)