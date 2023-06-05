from django.urls import path
from . import views


app_name = "bank_app.bank_api"

urlpatterns = [
    path('', views.Home.as_view(), name="home"),
    path('list_bank_account/', views.ListBankAccountView.as_view(),
         name="list_bank_account"),
    path('delete_bank_account/<int:pk>/', views.AccountdeleteView.as_view(),
         name="delete_bank_account"),
    path('transction_history/', views.TransactionHistoryView.as_view(),
         name="transction_history"),
    path('tranfer/', views.TransferamountView.as_view(),
         name="tranfer"),
    path('balance_user/', views.BalanceUserView.as_view(),
         name="balance_user"),
]
