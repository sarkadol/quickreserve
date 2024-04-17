from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from base.models import ManagerProfile


class LoginForm(forms.Form):
    username = forms.CharField(max_length=65)
    password = forms.CharField(max_length=65, widget=forms.PasswordInput)


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True, widget=forms.EmailInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "password1": forms.PasswordInput(attrs={"class": "form-control"}),
            "password2": forms.PasswordInput(attrs={"class": "form-control"}),
        }
    def __init__(self, *args, **kwargs):
        self.base_url = kwargs.pop('base_url', None)  # Get base_url if provided
        super(RegisterForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        user = super().save(commit=False)
        #if commit:
        user.save()
        ManagerProfile.objects.create(
            user=user,
            optimization_strategy="min_units",
            manager_link=(
                f"{self.base_url}/customer_home/{user.id}"
                if self.base_url
                else ""
            ),
        )
        return user
