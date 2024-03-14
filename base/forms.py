from django.forms import ModelForm, DateInput, widgets, DateTimeInput, Select
from . import models
from datetime import datetime, timedelta
from django.utils import timezone
from django import forms

#import datetime

TIME_CHOICES = [
    (
        timezone.now().replace(hour=h, minute=m, second=0).strftime("%H:%M"),
        timezone.now().replace(hour=h, minute=m, second=0).strftime("%H:%M"),
    )
    for h in range(24)
    for m in [0, 15, 30, 45]
]


class ReservationForm(forms.ModelForm):
    # Manually add non-model fields for separate date and time inputs
    reservation_date_from = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date","value": datetime.now().date()})
    )
    reservation_time_from = forms.TimeField(widget=forms.Select(choices=TIME_CHOICES))
    reservation_date_to = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date","value": datetime.now().date()}), required=False
    ) 
    reservation_time_to = forms.TimeField(
        widget=forms.Select(choices=TIME_CHOICES), required=False
    )

    class Meta:
        model = models.Reservation
        fields = [
            "reservation_from",
            "reservation_to",
            "customer_email",
            "belongs_to_category",
            "status",
        ]
        
        # Exclude the DateTime fields here, handle them separately in the view
        exclude = [
            "confirmed_by_manager",
            "submission_time",
            "belongs_to_offer",
            "belongs_to_category",
            "status",
            "reservation_from",
            "reservation_to",
        ]
    def __init__(self, *args, **kwargs):
        super(ReservationForm, self).__init__(*args, **kwargs)
        
        # Example hardcoded time choice, e.g., "15:00" for 3 PM
        hardcoded_time_from = "15:00"
        hardcoded_time_to = "16:00"  # Example, one hour later, e.g., "16:00" for 4 PM

        # Set initial date to today. This can be hardcoded as well if needed
        self.fields['reservation_date_from'].initial = timezone.localdate()
        self.fields['reservation_date_to'].initial = timezone.localdate()

        # Set the initial time fields to hardcoded values
        self.fields['reservation_time_from'].initial = hardcoded_time_from
        self.fields['reservation_time_to'].initial = hardcoded_time_to

# class ReservationUpdateForm - to be done


class OfferForm(ModelForm):
    class Meta:
        model = models.Offer
        exclude = [
            "manager_of_this_offer",
            "created_at",
        ]  # limiting the fields if that are displayed
        widgets = {
            "available_from": widgets.DateInput(
                attrs={
                    "type": "date",
                    #'min': datetime.now().date(),
                    "value": datetime.now().date(),
                }
            ),
            "available_to": widgets.DateInput(
                attrs={
                    "type": "date",
                    #'min': datetime.now().date(),
                    "value": datetime.now().date()+ timedelta(days=1),
                }
            ),
        }


class CategoryForm(ModelForm):
    class Meta:
        model = models.Category
        exclude = [
            "belongs_to_offer",
            "created_at",
            "category_pricing",
        ]  # limiting the fields if that are displayed
        widgets = {
            "additional_time": widgets.DateInput(
                attrs={"type": "time"}
            ),  # here must be time-duration picker, not time-picker
        }
