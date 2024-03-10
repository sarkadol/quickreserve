from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse
from . import models, forms
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Offer, Unit

@login_required # If a user is not logged in, Django will redirect them to the login page.
def manager_home(request):
    if request.POST: #lze to napsat i třídami s medotou post a get, ne funkcemi, mozna jiny atribut nez method
        print("POSLANO")
    users = models.User.objects.all()
    offers = Offer.objects.filter(manager_of_this_offer=request.user)
    form = forms.ReservationForm()
    units = Unit.objects.all()
    return render(request,'manager_home.html',context={'Users':users,'form':form, 'offers':offers,'units':units})
# v templatu je promenna Users, která má data z users

@login_required 
def create_offer(request,offer_id=None):
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
                return redirect(request, 'create_offer.html', context={'form': form})
            
            offer.save() # Save the offer to the database
            offer_id=offer.id

            success_message = f"Offer '{offer.offer_name}' successfully created."
            messages.success(request, success_message)

            return render(request,'offer_detail.html',context={'offer_id':offer_id,'form':form})  # Redirect to a success page after saving
        
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

@login_required 
def create_unit(request, offer_id=None):
    form = forms.UnitForm()
    offer = get_object_or_404(Offer, pk=offer_id)
    offer_name = offer.offer_name

    if request.method == 'POST':
        form = forms.UnitForm(request.POST)
        if form.is_valid():
            unit = form.save(commit=False) # should not be saved to the database immediately
            unit.belongs_to_offer = offer
            
            unit.save() # Save the offer to the database
            success_message = f"Unit '{unit.unit_name}' successfully created in '{offer.offer_name}'"
            messages.success(request, success_message)

            return redirect('/manager_home')  # Redirect to a success page after saving
        else:
            error_message = "Something went wrong."
            messages.error(request, error_message) 

    return render(request,'create_unit.html',context={'form':form,'offer_id': offer_id,'offer_name': offer_name}) 

@login_required
def edit_unit(request, offer_id=None, unit_id=None):
    current_offer = get_object_or_404(Offer, pk=offer_id)
    current_offer_name = current_offer.offer_name
    unit = get_object_or_404(Unit, pk=unit_id)
    form = forms.UnitForm(instance=unit)
    offer=unit.belongs_to_offer
    units = Unit.objects.filter(belongs_to_offer=offer)
    offer_name=offer.offer_name

    if request.method == 'POST':
        form = forms.UnitForm(request.POST, instance=unit)
        if form.is_valid():
            unit = form.save(commit=False)
            unit.belongs_to_offer = current_offer
            unit.save()
            success_message = f"Unit '{unit.unit_name}' successfully edited."
            messages.success(request, success_message)

            return render(request,'offer_detail.html',context={'form':form, 'offer_id': offer.id,'units':units,'offer_name':offer_name})
  # Redirect to a success page after saving
        else:
            error_message = "Something went wrong."
            messages.error(request, error_message) 

    return render(request,'edit_unit.html',context={'form':form,'offer_id': offer_id,'offer_name': current_offer_name,'unit_name':unit.unit_name}) 
        
@login_required # If a user is not logged in, Django will redirect them to the login page.
def offer_detail(request,offer_id=None):
    offer = get_object_or_404(Offer, pk=offer_id)
    offer_name = offer.offer_name
    form = forms.OfferForm(instance=offer)
    if request.method == 'POST':
        form = forms.OfferForm(request.POST, instance=offer)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.save()
            success_message = f"Offer '{offer.offer_name}' successfully edited."
            messages.success(request, success_message)

            #return redirect('/manager_home')  # Redirect to a success page after saving
        else:
            error_message = "Something went wrong."
            messages.error(request, error_message) 

    #users = models.User.objects.all()
    offers = Offer.objects.filter(manager_of_this_offer=request.user)
    offer = get_object_or_404(Offer, pk=offer_id)

    form = forms.OfferForm(instance=offer)
    units = Unit.objects.filter(belongs_to_offer=offer)

    return render(request,'offer_detail.html',context={'form':form, 'offer_id': offer.id,'units':units,'offer_name':offer_name})
