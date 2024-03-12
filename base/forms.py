from django.forms import ModelForm, DateField, widgets
from . import models
from datetime import datetime, timedelta

class ReservationForm(ModelForm):
    class Meta: 
        model=models.Reservation
        widgets = {
            'reservation_from': widgets.DateInput(attrs={
                'type': 'date', 
                'min': datetime.now().date(),
                'value': datetime.now().date()}),
            'reservation_to': widgets.DateInput(attrs={
                'type': 'date', 
                'min': datetime.now().date(),
                'value': datetime.now().date()}),
            'customer': widgets.TextInput(attrs={ # here would be probably problems as customer is dromdown menu 
                'value':'novy_uzivatel'
            }),
            'reserved_unit': widgets.TextInput(attrs={ #same here
                'value':'Unit object (1)'
            })    
        }
        exclude = ['confirmed_by_manager'] #limiting the fields if that are displayed

#class ReservationUpdateForm - to be done       
        
class OfferForm(ModelForm):
    class Meta: 
        model=models.Offer
        exclude = ['manager_of_this_offer','created_at'] #limiting the fields if that are displayed
        widgets = {
            'available_from': widgets.DateInput(attrs={
                'type': 'date', 
                #'min': datetime.now().date(),
                'value': datetime.now().date()}),
            'available_to': widgets.DateInput(attrs={
                'type': 'date', 
                'min': datetime.now().date(),
                'value': (datetime.now() + timedelta(days=365)).date()})  # now + 1 year
        }

class UnitForm(ModelForm):
    class Meta: 
        model=models.Unit
        exclude = ['belongs_to_offer','created_at','unit_pricing'] #limiting the fields if that are displayed
        widgets = {
            'additional_time': widgets.DateInput(attrs={
                'type': 'time'}) # there must be time-duration picker, not time-picker
        }

