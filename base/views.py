from django.shortcuts import render, redirect
from django.http import HttpResponse
from . import models, forms
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Offer

@login_required # If a user is not logged in, Django will redirect them to the login page.
def manager_home(request):
    if request.POST: #lze to napsat i třídami s medotou post a get, ne funkcemi, mozna jiny atribut nez method
        print("POSLANO")
    users = models.User.objects.all()
    offers = Offer.objects.filter(manager_of_this_offer=request.user)
    form = forms.ReservationForm()
    return render(request,'manager_home.html',context={'Users':users,'form':form, 'offers':offers})
# v templatu je promenna Users, která má data z users

@login_required 
def create_offer(request):
    form = forms.OfferForm()
    if request.method == 'POST':
        form = forms.OfferForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False) # should not be saved to the database immediately
            offer.manager_of_this_offer = request.user # Set the manager_of_this_offer to the currently signed-in user

            # Custom validation to check if available_from is before available_to
            available_from = form.cleaned_data['available_from']
            available_to = form.cleaned_data['available_to']

            if available_from and available_to and available_from >= available_to:
                error_message = "Available from date must be before available to date."
                messages.error(request, error_message)
                return render(request, 'create_offer.html', context={'form': form})
            
            offer.save() # Save the offer to the database
            success_message = "Offer successfully created."
            messages.success(request, success_message)

            return redirect('manager_home')  # Redirect to a success page after saving
        else:
            error_message = "Something went wrong."
            messages.error(request, error_message) 

    return render(request,'create_offer.html',context={'form':form}) 

def new_reservation(request):
    users = models.User.objects.all()
    form = forms.ReservationForm()
    if request.POST: #lze to napsat i třídami s medotou post a get, ne funkcemi, mozna jiny atribut nez method
        print("POSLANO")
        
        success_message = "Reservation successfully created."
        error_message = "Something went wrong."
        messages.success(request, success_message)
        messages.error(request, error_message) 

        if form.is_valid():
            print("JE VALIDNI")
            
        else:
            print("FORM IS NOT VALID. Errors:")
            for field, errors in form.errors.items():
                print(f"Field: {field}, Errors: {', '.join(errors)}")
        #form.save() #tady to hodilo chybu NOT NULL constraint failed: base_reservation.reservation_to
        print("JE ULOZENY BEZ KONTROLY")

    return render(request,'new_reservation.html',context={'Users':users,'form':form})

@login_required
def my_schedule(request):
    return render(request,'my_schedule.html') 

