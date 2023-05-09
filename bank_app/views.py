from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.edit import CreateView
from . forms import DepositForm

# Create your views here.

def home(request):
    return render(request,"b_base.html")

class DepositView(CreateView):
    form_class = DepositForm
    template_name = "deposit.html"

        
    def form_valid(self,form):
        form.instance.user = self.request.user
        return super().form_valid(form)
