from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.views.generic.edit import CreateView
from . forms import SignupForm , LoginForm
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import authenticate, login

# Create your views here.

def home(request):
    return render(request,"base.html")


class SignupView(SuccessMessageMixin,CreateView):
    form_class = SignupForm
    template_name = "signup.html"
    success_url = reverse_lazy('user_app:signup')
    success_message = "Successfully Signup !"

class LoginView(CreateView):
    form_class = LoginForm
    template_name = "login.html"

    def post(self,request):
        email =  request.POST.get("email")
        password = request.POST.get("password")
        
        user = authenticate(email=email,password=password)
        if user:
            return redirect("/bank_app/")
        return HttpResponse("You have not signup ! please signup first")