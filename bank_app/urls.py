from django.urls import path
from . import views

app_name = "bank_app"

urlpatterns = [
    path('', views.home, name="home"),
    path('deposit/', views.DepositView.as_view(), name="deposit"),
    path('withdraw/', views.WithdrawView.as_view(), name="withdraw"),
    path('report/', views.ReportView.as_view(), name="report"),
    path('transfer_amount/', views.transfer_amountView, name="transfer"),
    path('bank/', views.AddBankAccountView.as_view(), name="bank"),
    path('list_account/', views.ListBankAccountView.as_view(), name="list_account"),
    path('delete_account/<int:pk>/',
         views.Accountdelete.as_view(), name="delete_account"),
    path('history/', views.TransactionHistoryView.as_view(), name="history"),
    path('balance_user/', views.BalanceUserView.as_view(), name="balance_user"),
]
