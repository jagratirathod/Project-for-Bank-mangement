from django.urls import path
from. import views

app_name = "user_app"

urlpatterns = [
    path('',views.home),
    path('signup/',views.SignupView.as_view(),name='signup'),
    path('login/',views.LoginView.as_view(),name='login')

]