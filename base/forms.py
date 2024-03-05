from django.forms import ModelForm
from . import models

class ReservationForm(ModelForm):
    class Meta: 
        model=models.Reservation
        exclude = [] #omezení polí, jestli se zobrzí všechny

#class ReservationUpdateForm        
