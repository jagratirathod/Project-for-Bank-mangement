from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.views.generic.edit import CreateView
from . forms import SignupForm , LoginForm
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import authenticate, login
from django.contrib import messages
import random

# Create your views here.

def home(request):
    return render(request,"base.html")

class SignupView(SuccessMessageMixin,CreateView):
    form_class = SignupForm
    template_name = "signup.html"
    success_url = reverse_lazy('user_app:signup')

    def form_valid(self,form):
        account_number = random.randrange(100000000000,999999999999)
        form.instance.account_number = account_number
        success_message = f"Successfully signed up!  Your Account Number is {account_number}"
        messages.success(self.request, success_message)
        return super().form_valid(form)

class LoginView(CreateView):
    form_class = LoginForm
    template_name = "login.html"

    def post(self,request):
        email =  request.POST.get("email")
        password = request.POST.get("password")
        
        user = authenticate(email=email,password=password)
        if user:
            login(request, user)
            return redirect("/bank_app/")
        return HttpResponse("You have not signup ! please signup first")

