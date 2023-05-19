from django.urls import path
from . import views

app_name = "bank_app"


urlpatterns = [
    path('', views.home, name="home"),
    path('deposit/', views.DepositView.as_view(), name="deposit"),
    path('withdraw/', views.WithdrawView.as_view(), name="withdraw"),
    path('report/', views.ReportView.as_view(), name="report"),
    path('transfer_amount/', views.TransferAmountView, name="transfer")
]
