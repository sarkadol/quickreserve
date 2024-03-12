from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from . import models, forms
from datetime import datetime, time, timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Offer, Category, Unit

# https://www.pythontutorial.net/django-tutorial/django-password-reset/ to be done


@login_required  # If a user is not logged in, Django will redirect them to the login page.
def manager_home(request):
    # if request.POST: #lze to napsat i třídami s medotou post a get, ne funkcemi, mozna jiny atribut nez method
    # print("POSLANO")
    users = models.User.objects.all()
    offers = Offer.objects.filter(
        manager_of_this_offer=request.user
    )  # only offers of this user
    form = forms.ReservationForm()

    category_ids = offers.values_list(
        "category", flat=True
    ).distinct()  # only categories of this user
    categories = models.Category.objects.filter(id__in=category_ids)

    return render(
        request,
        "manager_home.html",
        context={
            "Users": users,
            "form": form,
            "offers": offers,
            "categories": categories,
        },
    )


# v templatu je promenna Users, která má data z users


@login_required
def create_offer(request, offer_id=None):
    form = forms.OfferForm()
    if request.method == "POST":
        form = forms.OfferForm(request.POST)
        if form.is_valid():
            offer = form.save(
                commit=False
            )  # should not be saved to the database immediately
            offer.manager_of_this_offer = (
                request.user
            )  # Set the manager_of_this_offer to the currently signed-in user
            # Custom validation to check if available_from is before available_to
            available_from = form.cleaned_data["available_from"]
            available_to = form.cleaned_data["available_to"]

            if available_from and available_to and available_from >= available_to:
                error_message = "Available from date must be before available to date."
                messages.error(request, error_message)
                return redirect(request, "create_offer.html", context={"form": form})

            offer.save()  # Save the offer to the database
            offer_id = offer.id

            success_message = f"Offer '{offer.offer_name}' successfully created."
            messages.success(request, success_message)

            return render(
                request,
                "offer_detail.html",
                context={"offer_id": offer_id, "form": form},
            )  # Redirect to a success page after saving

        else:
            error_message = "Something went wrong."
            messages.error(request, error_message)

    return render(request, "create_offer.html", context={"form": form})


def new_reservation(request, offer_id=None, category_id=None):
    # users = models.User.objects.all()
    form = forms.ReservationForm()
    category_name = get_object_or_404(Category, pk=category_id).category_name

    if request.POST:
        form = forms.ReservationForm(request.POST)

        reservation = form.save(commit=False)
        reservation.belongs_to_category = get_object_or_404(Category, pk=category_id)
        reservation.belongs_to_offer = get_object_or_404(Offer, pk=offer_id)
        #category_name = reservation.belongs_to_category.category_name

        if form.is_valid():

            # and then create a reservation slot
            success_message = "Reservation successfully created."
            messages.success(request, success_message)
        else:
            error_message = "Something went wrong."
            messages.error(request, error_message)

    return render(request, "new_reservation.html", context={"form": form, "category_name":category_name})


@login_required
def my_schedule(request):
    return render(request, "my_schedule.html")


@login_required
def create_category(request, offer_id=None):
    form = forms.CategoryForm()
    offer = get_object_or_404(Offer, pk=offer_id)
    offer_name = offer.offer_name

    if request.method == "POST":
        form = forms.CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(
                commit=False
            )  # should not be saved to the database immediately
            category.belongs_to_offer = offer

            category.save()  # Save the offer to the database
            success_message = f"Category '{category.category_name}' successfully created in '{offer.offer_name}'"
            messages.success(request, success_message)

            return redirect(
                "/manager_home"
            )  # Redirect to a success page after saving - to do offerdetail
        else:
            error_message = "Something went wrong."
            messages.error(request, error_message)

    return render(
        request,
        "create_category.html",
        context={"form": form, "offer_id": offer_id, "offer_name": offer_name},
    )


@login_required
def edit_category(request, offer_id=None, category_id=None):
    current_offer = get_object_or_404(Offer, pk=offer_id)
    current_offer_name = current_offer.offer_name
    category = get_object_or_404(Category, pk=category_id)
    form = forms.CategoryForm(instance=category)
    offer = category.belongs_to_offer
    categories = Category.objects.filter(belongs_to_offer=offer)
    offer_name = offer.offer_name

    units = Unit.objects.filter(belongs_to_category=category)

    # Assuming you want slots from 00:00 to 23:00, one hour intervals
    hours = [time(hour=h) for h in range(24)]

    if request.method == "POST":
        form = forms.CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save(commit=False)
            category.belongs_to_offer = current_offer
            category.save()
            success_message = (
                f"Category '{category.category_name}' successfully edited."
            )
            messages.success(request, success_message)

            return render(
                request,
                "offer_detail.html",
                context={
                    "form": form,
                    "offer_id": offer.id,
                    "categories": categories,
                    "offer_name": offer_name,
                },
            )
        # Redirect to a success page after saving
        else:
            error_message = "Something went wrong."
            messages.error(request, error_message)

    return render(
        request,
        "edit_category.html",
        context={
            "form": form,
            "offer_id": offer_id,
            "offer_name": current_offer_name,
            "category_name": category.category_name,
            "category_id": category.id,
            "units": units,
            "hours": hours,
        },
    )


@login_required  # If a user is not logged in, Django will redirect them to the login page.
def offer_detail(request, offer_id=None):
    offer = get_object_or_404(Offer, pk=offer_id)
    offer_name = offer.offer_name
    form = forms.OfferForm(instance=offer)
    if request.method == "POST":
        form = forms.OfferForm(request.POST, instance=offer)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.save()
            success_message = f"Offer '{offer.offer_name}' successfully edited."
            messages.success(request, success_message)

            # return redirect('/manager_home')  # Redirect to a success page after saving
        else:
            error_message = "Something went wrong."
            messages.error(request, error_message)

    # users = models.User.objects.all()
    offers = Offer.objects.filter(manager_of_this_offer=request.user)
    offer = get_object_or_404(Offer, pk=offer_id)

    form = forms.OfferForm(instance=offer)
    categories = Category.objects.filter(belongs_to_offer=offer)

    return render(
        request,
        "offer_detail.html",
        context={
            "form": form,
            "offer_id": offer.id,
            "categories": categories,
            "offer_name": offer_name,
        },
    )


@login_required
def delete_category(request, offer_id=None, category_id=None):
    category = get_object_or_404(Category, pk=category_id)
    offer = get_object_or_404(Offer, pk=category.belongs_to_offer.id)
    offer_id = offer.id
    category_id = category.id
    context = {
        "category_id": category_id,
        "offer_id": offer_id,
        "offer_name": offer.offer_name,
        "category_name": category.category_name,
    }

    if request.method == "GET":
        return render(request, "category_confirm_delete.html", context)
    elif request.method == "POST":
        category.delete()
        success_message = f"Category '{category.category_name}' successfully deleted."
        messages.success(request, success_message)
        return redirect("/manager_home")


def category_detail(request, category_id=None):
    category = get_object_or_404(Category, pk=category_id)
    category_name = category.category_name
    form = forms.CategoryForm(instance=category)
    if request.method == "POST":
        form = forms.CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save(commit=False)
            category.save()
            success_message = f"Offer '{category.category_name}' successfully edited."
            messages.success(request, success_message)

            # return redirect('/manager_home')  # Redirect to a success page after saving
        else:
            error_message = "Something went wrong."
            messages.error(request, error_message)

    # users = models.User.objects.all()
    # offers = Offer.objects.filter(manager_of_this_offer=request.user)
    # offer = get_object_or_404(Offer, pk=offer_id)

    form = forms.CategoryForm(instance=category)
    # categories = Category.objects.filter(belongs_to_offer=offer)
    # units = Unit.objects.filter(belongs_to_category = category)

    return render(
        request,
        "category_detail.html",
        context={
            "form": form,
            "category_id": category.id,
            "units": units,
            "category_name": category_name,
        },
    )


@login_required
def delete_offer(request, offer_id=None):
    offer = get_object_or_404(Offer, pk=offer_id)
    categories = Category.objects.filter(belongs_to_offer=offer)
    categories_names = ", ".join([category.category_name for category in categories])
    context = {
        "offer_id": offer_id,
        "offer_name": offer.offer_name,
        "categories": categories,
    }

    if request.method == "GET":
        return render(request, "offer_confirm_delete.html", context)
    elif request.method == "POST":
        offer.delete()

        success_message = f"Offer '{offer.offer_name}' and categories '{categories_names}' successfully deleted."
        messages.success(request, success_message)
        return redirect("/manager_home")
