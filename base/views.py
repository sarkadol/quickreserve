# VIEWS.PY
# Python standard library imports
from datetime import datetime, time, timedelta
import uuid

# External libraries
import pytz

# Imports from my project's modules
from . import forms, models
from .models import Category, Offer, Reservation, ReservationSlot, Unit
from base.optimization import *

# Django messaging and contributions
from django.contrib import messages

# Django decorators for views, CSRF, and authentication
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

# Django utilities and timezone
from django.utils import timezone

# Django views, shortcuts, and URL utilities
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse
from django.views.defaults import page_not_found

# Django HTTP utilities and response handling
from django.http import (
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseRedirect,
    JsonResponse,
)
from django.template.loader import render_to_string


# Django database operations
from django.db import IntegrityError, transaction
from django.db.models import Count, ExpressionWrapper, F, DateTimeField

# Django configuration and exceptions
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail


@login_required  # If a user is not logged in, Django will redirect them to the login page.
def manager_home(request):
    """
    Render the homepage for a manager showing available offers, categories, and a form for creating reservations.
    """
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
            # "Users": users,
            "form": form,
            "offers": offers,
            "categories": categories,
        },
    )


# v templatu je promenna Users, která má data z users


@login_required
def create_offer(request, offer_id=None):
    """
    Create a new offer or edit an existing one based on whether an offer_id is provided.
    """
    form = forms.OfferForm()
    if request.method == "POST":
        form = forms.OfferForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.manager_of_this_offer = request.user

            # Custom validation to check if available_from is before available_to
            available_from = form.cleaned_data["available_from"]
            available_to = form.cleaned_data["available_to"]
            if available_from and available_to and available_from >= available_to:
                error_message = "Available from date must be before available to date."
                messages.error(request, error_message)
                return render(request, "create_offer.html", context={"form": form})

            try:
                offer.save()  # Attempt to save the offer to the database
                offer_id = offer.id
                success_message = f"Offer '{offer.offer_name}' successfully created."
                messages.success(request, success_message)
                return render(
                    request,
                    "offer_detail.html",
                    context={"offer_id": offer_id, "form": form},
                )
            except IntegrityError:
                error_message = f"Offer with the name '{offer.offer_name}' already exists for your account. Please choose a different name."
                messages.error(request, error_message)
                return render(request, "create_offer.html", context={"form": form})
        else:
            error_message = "Something went wrong."
            messages.error(request, error_message)

    return render(request, "create_offer.html", context={"form": form})


@login_required
def my_schedule(request):
    """
    Display the schedule for the logged-in manager, showing categories and reservation slots.
    """
    return render(request, "my_schedule.html")


@login_required
def create_category(request, offer_id=None):
    """
    Create a new category under an offer specified by offer_id, handling form submission and validation.
    """
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

            # Process unit_names_input here
            unit_names_input = form.cleaned_data.get("unit_names_input")
            # Parse the unit_names_input according to your chosen format
            # For example, if input is CSV:
            unit_names_list = (
                [name.strip() for name in unit_names_input.split(",")]
                if unit_names_input
                else []
            )
            # Check if the length of unit names list matches count_of_units
            if len(unit_names_list) != category.count_of_units:
                # If not, send an error message back to the form
                messages.error(
                    request,
                    f"Number of unit names provided ({len(unit_names_list)}) does not match the count of units specified ({category.count_of_units}). Please correct and try again.",
                )
                return render(
                    request,
                    "create_category.html",
                    context={
                        "form": form,
                        "offer_id": offer_id,
                        "offer_name": offer_name,
                    },
                )

            category.unit_names = unit_names_list

            category.save()  # Save the offer to the database
            success_message = f"Category '{category.category_name}' successfully created in '{offer.offer_name}'"
            messages.success(request, success_message)

            return redirect(reverse("offer_detail", kwargs={"offer_id": offer_id}))
        # Redirect to a success page after saving - to do offerdetail
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
    """
    Edit an existing category specified by category_id, under an offer specified by offer_id.
    """
    current_offer = get_object_or_404(Offer, pk=offer_id)
    current_offer_name = current_offer.offer_name
    category = get_object_or_404(Category, pk=category_id)
    form = forms.CategoryForm(instance=category)
    offer = category.belongs_to_offer
    categories = Category.objects.filter(belongs_to_offer=offer)
    offer_name = offer.offer_name

    units = Unit.objects.filter(belongs_to_category=category)

    # Get existing times from the category instance
    old_opening_time = category.opening_time
    old_closing_time = category.closing_time

    # Ensure the current user is the manager
    if category.belongs_to_offer.manager_of_this_offer != request.user:
        messages.error(request, "You are not authorized to edit this category.")
        return redirect("manager_home")  # Redirect to a safe page
    

    # Assuming you want slots from 00:00 to 23:00, one hour intervals
    hours = [time(hour=h) for h in range(24)]

    if request.method == "POST":
        form = forms.CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save(commit=False)
            category.belongs_to_offer = current_offer

            # Check if opening or closing times have changed
            new_opening_time = form.cleaned_data["opening_time"]
            new_closing_time = form.cleaned_data["closing_time"]
            time_changed = (new_opening_time != old_opening_time) or (
                new_closing_time != old_closing_time
            )  # TODO what if I change time?

            # Before saving the category, check if there are existing units already
            desired_unit_count = form.cleaned_data.get(
                "count_of_units"
            )  # Assuming 'unit_count' is a field in your form

            existing_unit_count = units.count()
            units_to_add = desired_unit_count - existing_unit_count

            if units_to_add > 0:
                # Here, add logic to create additional units for the category.
                for _ in range(units_to_add):
                    Unit.objects.create(
                        belongs_to_category=category,
                    )

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

    # Handling the AJAX request for date selection
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        selected_date = request.GET.get("selected_date")
        # Here, adjust your query to filter units or reservations based on the selected date
        # ...reservation_slots = ReservationSlot.objects.filter()

        # Render only the table part using a separate template or a dynamically built HTML string
        html = render_to_string(
            "reservations_table.html",
            {
                "units": units,
                "hours": hours,
            },
            request=request,
        )

        return JsonResponse({"html": html})

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


def new_reservation_timetable(request, offer_id=None, category_id=None):
    """
    Render a new reservation timetable for a specific offer and category, handling date selections and slot updates via AJAX.
    """
    offer = get_object_or_404(Offer, pk=offer_id)
    category = get_object_or_404(Category, pk=category_id)
    opening_hour = category.opening_time.hour
    closing_hour = category.closing_time.hour
    hours = [time(hour=h) for h in range(24)]

    units = Unit.objects.filter(belongs_to_category=category)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        selected_date_str = request.GET.get("selected_date")
        # Make sure to parse the selected_date_str to a datetime.date object correctly
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()

        # Call ensure_availability_for_day with the selected date
        ensure_availability_for_day(selected_date, category_id)
        print("ensure availability ", selected_date)

        units_with_slots = fetch_reservation_slots(selected_date, category)

        for unit_with_slots in units_with_slots:
            for slot in unit_with_slots["reservation_slots"]:
                print(
                    f"Unit: {unit_with_slots['unit'].id}, Slot: {slot.start_time}, Status: {slot.status}"
                )

        html = render_to_string(
            "reservations_table.html",
            {
                "units_with_slots": units_with_slots,
                "hours": hours,
                "category_name": category.category_name,
                "category_id": category_id,
                # "unit_id": 2,
            },
            request=request,
        )
        return JsonResponse({"html": html})
    return render(
        request,
        "new_reservation_timetable.html",
        context={"category_name": category.category_name},
    )


@login_required  # If a user is not logged in, Django will redirect them to the login page.
def offer_detail(request, offer_id=None):
    """
    Display details of an offer specified by offer_id, allow editing if posted, and validate access by offer ownership.
    """
    offer = get_object_or_404(Offer, pk=offer_id)
    offer_name = offer.offer_name
    form = forms.OfferForm(instance=offer)

    # Check if the current user is the manager of this offer
    if offer.manager_of_this_offer != request.user:
        messages.error(request, "You are not authorized to delete this offer.")
        return redirect("manager_home")  # Redirect to a safe page

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
    """
    Handle the deletion of a category specified by category_id, after confirming the manager's permission.
    """
    category = get_object_or_404(Category, pk=category_id)
    offer = get_object_or_404(Offer, pk=category.belongs_to_offer.id)
    offer_id = offer.id
    category_id = category.id

    # Ensure the current user is the manager
    if category.belongs_to_offer.manager_of_this_offer != request.user:
        messages.error(request, "You are not authorized to delete this category.")
        return redirect("manager_home")  # Redirect to a safe page

    reservations = Reservation.objects.filter(belongs_to_category=category)
    # reservation_names = ", ".join([reservation.reservation_name for reservation in reservations])

    # categories = Category.objects.filter(belongs_to_offer=offer)
    # categories_names = ", ".join([category.category_name for category in categories])
    context = {
        "category_id": category_id,
        "offer_id": offer_id,
        "offer_name": offer.offer_name,
        "category_name": category.category_name,
        "reservations": reservations,
        # "reservation_names":reservation_names
    }

    if request.method == "GET":
        return render(request, "category_confirm_delete.html", context)
    elif request.method == "POST":
        category.delete()
        success_message = f"Category '{category.category_name}' successfully deleted."
        messages.success(request, success_message)
        return redirect("/manager_home")


@login_required
def category_detail(request, category_id=None):
    """
    Display details of a category specified by category_id, including associated units and allowing for updates.
    """
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
    units = Unit.objects.filter(belongs_to_category=category)

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
    """
    Handle the deletion of an offer and its associated categories specified by offer_id, after confirming the manager's permission.
    """
    offer = get_object_or_404(Offer, pk=offer_id)
    categories = Category.objects.filter(belongs_to_offer=offer)
    categories_names = ", ".join([category.category_name for category in categories])

    # Check if the current user is the manager of this offer
    if offer.manager_of_this_offer != request.user:
        messages.error(request, "You are not authorized to delete this offer.")
        return redirect("manager_home")  # Redirect to a safe page
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


@login_required
def managed_reservations(request):
    """
    Display all reservations managed by the current user, categorized and ordered by their details.
    """
    # Assuming the user's profile has a timezone attribute
    user_timezone = request.user.userprofile.timezone if hasattr(request.user, 'userprofile') else 'UTC'
    timezone.activate(user_timezone)

    # Fetch all categories that belong to offers managed by the current user
    categories = Category.objects.filter(
        belongs_to_offer__manager_of_this_offer=request.user
    )

    # Fetch reservations for those categories
    reservations = (
        Reservation.objects.filter(belongs_to_category__in=categories)
        .select_related("belongs_to_category", "belongs_to_category__belongs_to_offer")
        .order_by("-submission_time",
            "reservation_from", "belongs_to_category__belongs_to_offer__offer_name"
        )
    )

    return render(
        request,
        "managed_reservations.html",
        {
            "reservations": reservations,
        },
    )


def new_reservation(request, offer_id=None, category_id=None):
    category = get_object_or_404(Category, pk=category_id)
    offer = get_object_or_404(Offer, pk=offer_id)
    form = forms.ReservationForm()

    if request.method == "POST":
        form = forms.ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            date_from = form.cleaned_data["reservation_date_from"]
            time_from = form.cleaned_data["reservation_time_from"]
            date_to = form.cleaned_data.get("reservation_date_to")
            time_to = form.cleaned_data.get("reservation_time_to")

            reservation_from = timezone.make_aware(
                datetime.combine(date_from, time_from)
            )
            reservation_to = (
                timezone.make_aware(datetime.combine(date_to, time_to))
                if date_to and time_to
                else None
            )

            # Validate against category availability and existing reservations
            """if not (
                time(8, 0) <= reservation_from.time() <= time(18, 0)
                and (
                    reservation_to is None
                    or time(8, 0) <= reservation_to.time() <= time(18, 0)
                )
            ):
                messages.error(
                    request,
                    "Reservation time must be within the category's available hours (8 AM to 18 PM).",
                )
                return render(
                    request,
                    "new_reservation.html",
                    context={
                        "form": form,
                        "category_name": category.category_name,
                        "offer_id": offer_id,
                        "category_id": category_id,
                    },
                )
"""
            conflicting_reservations = Reservation.objects.filter(
                belongs_to_category=category,
                reservation_from__lt=reservation_to,
                reservation_to__gt=reservation_from,
            )
            if conflicting_reservations.exists():
                messages.error(
                    request,
                    "This slot is already booked. Please choose a different time.",
                )
                return render(
                    request,
                    "new_reservation.html",
                    context={
                        "form": form,
                        "category_name": category.category_name,
                        "offer_id": offer_id,
                        "category_id": category_id,
                    },
                )

            # Save the reservation if it passes the checks

            reservation.belongs_to_category = category
            reservation.belongs_to_offer = offer
            reservation.reservation_from = reservation_from
            reservation.reservation_to = reservation_to
            reservation.save()

            create_unit(reservation)
            create_reservation_slot(reservation)

            messages.success(request, "Reservation successfully created.")
            return redirect("/manager_home")
        else:
            messages.error(request, "Something went wrong.")

    context = {
        "form": form,
        "category_name": category.category_name,
        "offer_id": offer_id,
        "category_id": category_id,
    }
    return render(request, "new_reservation.html", context)


def get_available_slots(date, category_id):
    """
    Calculate and return available time slots for reservations for a given date and category.
    """
    # Assuming each slot is 1 hour and category "tennis court" has daily availability from 8 AM to 18 PM
    start_time = time(8, 0)
    end_time = time(18, 0)
    slot_duration = timedelta(hours=1)

    # Fetch all reservations for the given date and category
    reservations = Reservation.objects.filter(
        reservation_from__date=date, belongs_to_category_id=category_id
    ).order_by("reservation_from")

    available_slots = []
    current_time = datetime.combine(date, start_time)
    end_of_day = datetime.combine(date, end_time)

    while current_time + slot_duration <= end_of_day:
        slot_end = current_time + slot_duration

        # Check if the slot overlaps with any reservation
        if not reservations.filter(
            reservation_from__lt=slot_end, reservation_to__gt=current_time
        ).exists():
            available_slots.append((current_time, slot_end))

        current_time += slot_duration

    return available_slots


def create_reservation_slot(reservation):
    """
    Create or update reservation slots based on the provided reservation details.
    """
    # Assuming each unit within a category has a similar schedule and can have overlapping reservations.
    category_units = reservation.belongs_to_category.unit_set.all()
    print("category units: ", category_units)
    # Find if there's a unit with an available slot for the reservation.
    for unit in category_units:
        slots = models.ReservationSlot.objects.filter(
            unit=unit, start_time__lte=reservation.reservation_from, status="available"
        ).order_by("start_time")
        print("slots: ", slots)
        if slots.exists():
            for slot in slots:
                # Calculate the proposed end time based on the slot's start time and duration.
                # proposed_end_time = slot.start_time + timedelta(minutes=slot.duration)

                # Check if the reservation fits in the slot without overlapping with the next slot.
                next_slot = slots.filter(start_time__gt=slot.start_time).first()
                if next_slot:
                    if (
                        reservation.reservation_from >= slot.start_time
                        and reservation.reservation_to <= slot.end_time
                        and reservation.reservation_to <= next_slot.start_time
                    ):
                        # The reservation fits within this slot.
                        # Update the slot status to "reserved" and associate it with the reservation.
                        slot.status = "reserved"
                        slot.save()
                        print("A")
                        # return True
                else:
                    # No next slot, just check if it fits within the current slot's duration.
                    if (
                        reservation.reservation_from >= slot.start_time
                        and reservation.reservation_to <= slot.end_time
                    ):
                        # The reservation fits in this slot.
                        slot.status = "reserved"
                        slot.save()
                        print("B")
                    # return True
        # there are no slots yet
        else:
            # Calculate total required slots to cover the reservation
            slot_duration = timedelta(minutes=60)
            reservation_duration = (
                reservation.reservation_to - reservation.reservation_from
            )
            total_required_slots = int(reservation_duration / slot_duration)
            # If there are no existing slots, start creating new slots
            start_time = reservation.reservation_from
            for _ in range(total_required_slots):
                end_time = start_time + slot_duration
                new_slot = models.ReservationSlot(
                    unit=unit,
                    start_time=start_time,
                    duration=timedelta(minutes=slot_duration.seconds // 60),
                    status="reserved",
                )
                new_slot.save()
                # Update start time for the next slot
                start_time = end_time

            print("Slots created to cover the reservation.")
        # create as many slots as needed to cover the reservation time

    # No suitable slot found or all slots are full/overlapping.
    # return False


def create_unit(category):
    """
    Create a new unit for the specified category if not exceeding the category's unit count.
    """
    # category = reservation.belongs_to_category
    print("unit count", category.get_unit_count())
    unit_count = category.get_unit_count()

    if unit_count < category.count_of_units:
        if len(category.unit_names) == 1 and category.count_of_units > 1:
            unit_name = category.unit_names[0]
        elif len(category.unit_names) > unit_count:
            unit_name = category.unit_names[unit_count]
        else:
            unit_name = ""

        unit = Unit.objects.create(
            # unit_name="z23",  # Provide the unit name here - to be done
            unit_name=unit_name,
            belongs_to_category=category,  # Assign the category instance
        )
        unit.save()
        print("unit created with name:", unit_name)  # to be done - messages
        return unit
    else:
        print("max units reached")  # to be done - messages
        return None


def reservation_details(request):
    """
    Display reservation details based on query parameters, providing a detailed view for specific reservations.
    """
    # Extract parameters from the query string
    start_date = request.GET.get("start")
    end_date = request.GET.get("end")
    category_id = request.GET.get("category")

    if start_date and end_date:
        start_datetime = datetime.fromisoformat(start_date)
        end_datetime = datetime.fromisoformat(end_date)

        # Format the datetime objects to a more readable format
        readable_start = start_datetime.strftime("%B %d, %Y at %H:%M")
        readable_end = end_datetime.strftime("%B %d, %Y at %H:%M")

    # Use the category_id to get the Category object and its name
    category = None
    category_name = ""
    if category_id:
        try:
            category = Category.objects.get(pk=category_id)
            category_name = category.category_name
        except Category.DoesNotExist:
            pass  # Handle the case where the category doesn't exist if necessary

    # Prepare the context
    context = {
        "start_date": start_date,
        "end_date": end_date,
        "category_name": category_name,
        "category_id": category_id,  # Assuming you want to pass the ID for form submission
        #'user_timezone': user_timezone
    }

    return render(request, "reservation_details.html", context)


@csrf_exempt
def reserve_slot(request):
    """
    Handle the reservation of a slot via POST, updating slot status and managing transaction integrity.
    """
    if request.method == "POST":
        start_time = request.GET.get("start")
        end_time = request.GET.get("end")
        category_id = request.GET.get("category")
        unit_id = request.GET.get("unit")

    try:
        with transaction.atomic():  # Use a transaction to ensure data integrity
            # Fetch and update the slots
            updated_count = ReservationSlot.objects.filter(
                unit_id=unit_id,
                start_time__gte=start_time,
                end_time__lte=end_time,
                status="available",  # Assuming you only want to update available slots
            ).update(
                # reservation_id=reservation_id,
                status="pending"
            )

            return JsonResponse(
                {
                    "status": "success",
                    "message": f"Updated {updated_count} slots to pending.",
                }
            )

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


def verify_reservation(request, token):
    """
    Verify a reservation using a token, handle its confirmation or cancellation based on the token validity.
    """
    reservation = get_object_or_404(Reservation, verification_token=token)
    start_date = reservation.reservation_from.strftime("%Y-%m-%d %H:%M")
    end_date = reservation.reservation_to.strftime("%Y-%m-%d %H:%M")
    category_name = reservation.belongs_to_category.category_name
    customer_email = reservation.customer_email
    status = reservation.status  # Retrieve the reservation status
    print("status je", status)

    context = {
        "start_date": start_date,
        "end_date": end_date,
        "category_name": category_name,
        "reservation": reservation,
        "token": token,
        "customer_email": customer_email,
        "status": status,
    }

    # Pass context to the template
    return render(request, "reservation_confirm_cancel.html", context)


@require_POST
def confirm_reservation(request, token):
    """
    Confirm a reservation by token, update slot statuses, and handle related category optimizations.
    """
    try:
        # Attempt to retrieve the reservation using the provided token
        reservation = Reservation.objects.get(
            verification_token=token, status="pending"
        )

        # Check if the link has expired (more than 1 hour since submission)
        if timezone.now() - reservation.submission_time > timedelta(
            hours=1
        ):  # 1 hour before the link expires
            # Link has expired
            with transaction.atomic():
                reservation.status = "cancelled"
                reservation.save()

                ReservationSlot.objects.filter(
                    reservation=reservation, status="pending"
                ).update(status="available")

            context = {
                "header": "Reservation expired",
                "message": "Your reservation link hase expired.",
            }

            return render(request, "reservation_status.html", context)
        else:
            # Link is still valid, confirm the reservation
            with transaction.atomic():
                # Confirm the reservation if the link is still valid
                reservation.status = "confirmed"
                reservation.save()
                print("reservation saved")
                #optimize_category(category, day_to_optimize)
                optimize_category(reservation.belongs_to_category, reservation.reservation_from.date())

                # Ensure availability and then process the slots
                day = reservation.reservation_from.date()
                category_id = reservation.belongs_to_category.id
                ensure_availability_for_day(day, category_id)

                # Identify and update pending slots to reserved
                available_slots = ReservationSlot.objects.filter(
                    unit__belongs_to_category=reservation.belongs_to_category,
                    start_time__gte=reservation.reservation_from,
                    end_time__lte=reservation.reservation_to,
                    status="pending",
                )

                if available_slots.exists():
                    unit_to_reserve = (
                        available_slots.values("unit")
                        .annotate(total=Count("unit"))
                        .order_by("total")
                        .first()
                    )

                    if unit_to_reserve:
                        available_slots.filter(unit_id=unit_to_reserve["unit"]).update(
                            reservation=reservation, status="reserved"
                        )

                        # Optional: Clear or adjust other slots
                        delete_available_slots_for_category(
                            reservation.belongs_to_category
                        )

                context = {
                    "header": "Reservation confirmed",
                    "message": "Your reservation has been successfully confirmed.",
                }
                return render(request, "reservation_status.html", context)

    except Reservation.DoesNotExist:
        return HttpResponse("Invalid or expired link.")


@require_POST
def cancel_reservation(request, token):
    """
    Cancel a reservation by token, update related slot statuses, and handle cleanup processes.
    """
    reservation = get_object_or_404(Reservation, verification_token=token)
    reservation.status = "cancelled"
    reservation.save()

    # Retrieve the slots that are about to be updated
    slots_to_update = ReservationSlot.objects.filter(
        reservation=reservation
    )
    print("mažu")
    # Print each slot detail before updating
    for slot in slots_to_update:
        print(f"Updating slot {slot.id} from {slot.status} to available")
    # z nějakého důvodu to funguje jen pro zrušení dříve potvrzených rezervací, ale ne těch co jsou pending
    # TODO

    ReservationSlot.objects.filter(
        reservation=reservation,
        # status="pending"
    ).update(status="available")
    delete_available_slots_for_category(reservation.belongs_to_category)

    context = {
        "header": "Reservation cancelled",
        "message": "Your reservation has been successfully cancelled.",
    }
    # Redirect to a cancellation confirmation page or similar
    return render(request, "reservation_status.html", context)


def submit_reservation(request):
    """
    Handle the submission of a reservation form, send verification email, and provide user feedback.
    """
    print("submitting reservation")
    if request.method == "POST":
        customer_name = request.POST.get("name")
        customer_email = request.POST.get("email")
        # Assuming you retrieve these from the form or as parameters
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        category_id = request.POST.get("category_id")
        print("cat id", category_id)
        category = get_object_or_404(Category, pk=category_id)
        token = uuid.uuid4().hex
        submission_time = timezone.now()

        """user_timezone = request.POST.get('user_timezone', 'UTC')  # Default to UTC if not provided
        submission_time = timezone.now()
        
        # Convert submission_time to the user's timezone
        user_tz = pytz.timezone(user_timezone)
        localized_submission_time = submission_time.astimezone(user_tz)"""

        reservation = Reservation(
            customer_name=customer_name,
            customer_email=customer_email,
            reservation_from=start_date,
            reservation_to=end_date,
            verification_token=token,
            belongs_to_category=category,
            status="pending",
            submission_time=submission_time,
        )
        reservation.save()

        verification_link = request.build_absolute_uri(f"/verify_reservation/{token}/")
        email_body = f"""
        Hello {customer_name},

        Thank you for your reservation. Here are the details:
        - Category: {category.category_name}
        - Start Date: {start_date}
        - End Date: {end_date}
        - Submission Time: {submission_time.strftime("%Y-%m-%d %H:%M:%S %Z")}
        Please follow the link below to confirm your reservation:
        {verification_link}

        If you did not make this reservation, please ignore this email.
        """

        send_mail(
            f"Verify your reservation for {category.category_name}",
            email_body,
            settings.DEFAULT_FROM_EMAIL,
            [customer_email],
            fail_silently=False,
            # fail_silently=False means your application wants to be informed of any problems during the email sending process
        )
        # success_message = (   f'Please check your email "{customer_email}" to confirm the reservation.' )
        # messages.success(request, success_message)
        context = {
            "header": "Reservation submitted",
            "message": f'Please check your email "{customer_email}" to confirm the reservation.',
        }
        return render(request, "reservation_status.html", context)


def create_slots_for_unit(unit, day, opening_time, closing_time):
    """
    Create reservation slots for a specific unit on a given day within specified opening hours.
    """
    # Define the start and end times for the day based on the provided opening and closing times
    start_of_day = timezone.make_aware(datetime.combine(day, opening_time))
    end_of_day = timezone.make_aware(datetime.combine(day, closing_time))

    # Define the absolute start and end of the day to check for "closed" slots creation
    absolute_start_of_day = timezone.make_aware(datetime.combine(day, time.min))
    absolute_end_of_day = timezone.make_aware(datetime.combine(day, time.max))

    current_time = absolute_start_of_day
    while current_time < absolute_end_of_day:
        slot_exists = ReservationSlot.objects.filter(
            unit=unit, start_time=current_time
        ).exists()

        # Check if current_time is within opening hours
        if start_of_day <= current_time < end_of_day:
            if not slot_exists:
                # Create an "available" slot if within opening hours and no slot exists
                ReservationSlot.objects.create(
                    unit=unit, start_time=current_time, status="available"
                )
        else:
            if not slot_exists:
                # Create a "closed" slot if outside opening hours and no slot exists
                ReservationSlot.objects.create(
                    unit=unit, start_time=current_time, status="closed"
                )

        # Move to the next hour
        current_time += timedelta(hours=1)


def ensure_availability_for_day(day, category_id):
    """
    Ensure there is at least one fully available unit for the given day and category.
    If not, create a new unit and slots for it within the specified category.
    """
    # Fetch the category
    print("cat ID", category_id)
    belongs_to_category = get_object_or_404(Category, pk=category_id)
    print(belongs_to_category)

    opening_time = belongs_to_category.opening_time
    closing_time = belongs_to_category.closing_time

    # Check for fully available units within the category for the given day
    fully_available_units = Unit.objects.filter(
        belongs_to_category=belongs_to_category
    ).exclude(
        reservation_slots__start_time__date=day,
        reservation_slots__status__in=["reserved", "maintenance", "pending"],
    )

    if not fully_available_units.exists():
        new_unit = create_unit(belongs_to_category)

        # Only attempt to create slots if a new unit was successfully created
        if new_unit:
            create_slots_for_unit(new_unit, day, opening_time, closing_time)
        else:
            # Log or handle the case where no new unit can be created, and no slots will be added
            print(
                "No new unit could be created. Maximum unit count reached or other error."
            )

    # Ensure slots are created for all units in the category which do not have slots on the given day
    for unit in Unit.objects.filter(belongs_to_category=belongs_to_category):
        create_slots_for_unit(unit, day, opening_time, closing_time)


def delete_available_slots_for_category(category):
    # Fetch all Unit objects associated with the target Category
    units_in_category = Unit.objects.filter(belongs_to_category=category)

    # Count the slots before deletion for logging or debugging purposes
    slots_before_deletion = ReservationSlot.objects.filter(
        unit__in=units_in_category, status="available"
    ).count()

    # Delete all available slots in these units
    deleted_slots_count = ReservationSlot.objects.filter(
        unit__in=units_in_category, status="available"
    ).delete()

    # Logging the result
    print(
        f"{deleted_slots_count[0]} slots deleted from {slots_before_deletion} available slots in category '{category}'."
    )


@login_required
def my_schedule(request):
    offers = Offer.objects.filter(manager_of_this_offer=request.user)
    offer_ids = offers.values_list("id", flat=True)
    categories = Category.objects.filter(belongs_to_offer__id__in=offer_ids)
    context = {
        "categories": categories,
    }

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        category_id = request.GET.get("category_id")
        selected_date_str = request.GET.get("selected_date")
        print("category ID: ", category_id)
        # If no category_id is provided, use the default category
        if not category_id:
            try:
                # Attempt to get the first category by ID as a default
                default_category = categories.order_by("id").first()
                if default_category:
                    category_id = default_category.id
                else:
                    # Handle the case where there are no categories
                    return JsonResponse(
                        {"error": "No categories available"}, status=400
                    )
            except ObjectDoesNotExist:
                return JsonResponse({"error": "Default category not found"}, status=400)

        if category_id and selected_date_str:
            selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
            category = get_object_or_404(Category, pk=category_id)
            ensure_availability_for_day(selected_date, category_id)
            units_with_slots = fetch_reservation_slots(selected_date, category)
            hours = [time(hour=h) for h in range(24)]

            # Render the reservations and units/slots data to the template
            html = render_to_string(
                "reservations_table.html",  # This template should be set up to handle both units and their reservations.
                {
                    "units_with_slots": units_with_slots,  # Each unit has 'slots' containing reservations for the selected date.
                    "selected_date": selected_date,
                    "hours": hours,
                },
                request=request,
            )
            return JsonResponse({"html": html})

    return render(request, "my_schedule.html", context)


def fetch_reservation_slots(selected_date, category):
    start_of_day = timezone.make_aware(datetime.combine(selected_date, time.min))
    end_of_day = timezone.make_aware(datetime.combine(selected_date, time.max))
    units = Unit.objects.filter(belongs_to_category=category)
    units_with_slots = [
        {
            "unit": unit,
            "reservation_slots": unit.reservation_slots.filter(
                start_time__gte=start_of_day, start_time__lte=end_of_day
            ).order_by("start_time"),
        }
        for unit in units
    ]
    return units_with_slots


@login_required
def customer_home(request, manager_id=None):
    # Fetch the manager and associated categories
    """user_id = request.user.id
    offers = Offer.objects.filter(
        manager_of_this_offer=request.user
    )"""
    categories = Category.objects.filter(
        belongs_to_offer__manager_of_this_offer=request.user
    ).distinct()

    # Render the categories in a template
    return render(request, "customer_home.html", {"categories": categories})


@login_required
def manager_link(request, manager_id=None):
    # Build the base part of the URL dynamically
    base_url = f"{request.scheme}://{request.get_host()}"
    # Construct the full path with the manager_id
    link = f"{base_url}/customer_home/{manager_id}"
    profile = request.user.managerprofile 
    return render(request, "manager_link.html", {'profile': profile})


# @login_required
def optimize(request):
    print("optimized clicked")
    current_user = request.user
    profile = request.user.managerprofile 

    print("current_user: ", current_user)
    categories = Category.objects.filter(
        belongs_to_offer__manager_of_this_offer=current_user, category_name="bazén"
    )

    start_day = timezone.now().date()  # + timezone.timedelta(days=1)
    start_day = date(2024,4,11)
    strategy="equally_distributed"
    # Assuming you have a function to optimize categories
    try:
        for i in range(1):  # Loop through the next 7 days from today
            day_to_optimize = start_day + timezone.timedelta(days=i)
            for category in categories:
                # Optimize each category for the current day in the loop
                print("OPTIMALIZUJI DEN", day_to_optimize)
                optimize_category(category, strategy,day_to_optimize)

        print("HOTOVO")
        success_message = "Categories successfully optimized."
        messages.success(request, success_message)

    except Exception as e:
        # If something goes wrong, send an error message
        error_message = f"Failed to optimize categories: {str(e)}"
        messages.error(request, error_message)

    # Redirect to a new URL where messages can be displayed or refresh the same page
    return render(
        request, "manager_link.html",{'profile':profile}
        
    )  # Replace 'some-view-name' with the actual view you want to redirect to

def save_optimization_strategy(request):
    print("save_optimization_strategy")
    if request.method == "POST":
        strategy = request.POST.get('optimizationStrategy')
        profile = request.user.managerprofile  # Adjusted to use managerprofile
        profile.optimization_strategy = strategy
        profile.save()
        message="Your optimization strategy has been updated to: " + profile.get_optimization_strategy_display()
        messages.success(request, message)
        #return redirect('manager_link',{'current_strategy': strategy})
        return render(request, 'manager_link.html',{'profile': profile})  # Redirect to the appropriate settings page or wherever suitable
    return render(request, 'manager_link.html',{'profile': profile})  # Render settings page on GET or if POST fails