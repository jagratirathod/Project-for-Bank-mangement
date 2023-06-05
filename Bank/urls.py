from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from bank_app.bank_api.views import (
    DepositView, WithdrawView, ReportView, AddBankAccountView
)


# routers
router = routers.DefaultRouter()
router.register('deposit', DepositView,   basename='deposit'),
router.register('withdraw', WithdrawView, basename='withdraw'),
router.register('report',  ReportView,    basename='report'),
router.register('bank_account',  AddBankAccountView, basename='bank_account'),


urlpatterns = [
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
    path('', include('user_app.urls')),
    path('bank_app/', include('bank_app.urls')),

    # api  -
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('user_api/', include('user_app.api.urls')),
    path('bank_api/', include('bank_app.bank_api.urls')),
]
