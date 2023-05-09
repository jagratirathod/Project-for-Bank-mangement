from django.urls import path
from. import views

app_name = "bank_app"


urlpatterns = [
    path('',views.home),
    path('deposit/',views.DepositView.as_view(),name="deposit")

]