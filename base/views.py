from django.shortcuts import render
from django.http import HttpResponse
from . import models, forms

# Create your views here.

def home(request):
    if request.method=="post": #lze to napsat i třídami s medotou post a get, ne funkcemi
        print("POSLANO")
    users = models.User.objects.all()
    form = forms.ReservationForm()
    return render(request,'home.html',context={'Users':users,'form':form})
# v templatu je promenna Users, která má data z users


def create_offer(request):
    return render(request,'create_offer.html') 