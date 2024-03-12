from django.forms import ModelForm, DateField, widgets
from . import models
from datetime import datetime, timedelta


class ReservationForm(ModelForm):
    class Meta:
        model = models.Reservation
        widgets = {
            "reservation_from": widgets.DateInput(
                attrs={
                    "type": "date",
                    "min": datetime.now().date(),
                    "value": datetime.now().date(),
                }
            ),
            "reservation_to": widgets.DateInput(
                attrs={
                    "type": "date",
                    "min": datetime.now().date(),
                    "value": datetime.now().date(),
                }
            ),
        }
        exclude = [
            "confirmed_by_manager",
            "submission_time",
            "belongs_to_offer",
            "belongs_to_category",
            
        ]  # limiting the fields if that are displayed


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
            )
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
            "max_count_of_units": widgets.DateInput(
                attrs={
                    "type": "date",
                    "min": datetime.now().date(),
                    "value": (datetime.now() + timedelta(days=365)).date(),
                }
            ),
        }
