from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.http import HttpResponse
from . import models, forms
from datetime import datetime, time, timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Offer, Category, Unit, Reservation, ReservationSlot
from django.http import JsonResponse
from django.template.loader import render_to_string

# https://www.pythontutorial.net/django-tutorial/django-password-reset/ to be done


@login_required  # If a user is not logged in, Django will redirect them to the login page.
def manager_home(request):
    # if request.POST: #lze to napsat i třídami s medotou post a get, ne funkcemi, mozna jiny atribut nez method
    # print("POSLANO")
    # users = models.User.objects.all()
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
            print("je validni")
            if available_from and available_to and available_from >= available_to:
                error_message = "Available from date must be before available to date."
                messages.error(request, error_message)
                return render(request, "create_offer.html", context={"form": form})

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
    current_offer = get_object_or_404(Offer, pk=offer_id)
    current_offer_name = current_offer.offer_name
    category = get_object_or_404(Category, pk=category_id)
    form = forms.CategoryForm(instance=category)
    offer = category.belongs_to_offer
    categories = Category.objects.filter(belongs_to_offer=offer)
    offer_name = offer.offer_name

    units = Unit.objects.filter(belongs_to_category=category)

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
    offer = get_object_or_404(Offer, pk=offer_id)
    category = get_object_or_404(Category, pk=category_id)
    hours = [time(hour=h) for h in range(24)]
    units = Unit.objects.filter(belongs_to_category=category)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        selected_date_str = request.GET.get("selected_date")
        # Make sure to parse the selected_date_str to a datetime.date object correctly
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()

        # Find the start and end of the selected date using the correctly parsed selected_date
        start_of_day = datetime.combine(selected_date, time.min)
        end_of_day = datetime.combine(selected_date, time.max)
        
        # Adjust your query to include ReservationSlots based on the selected date
        # and their relationship to the filtered units
        units_with_slots = [
            {
                "unit": unit,
                "reservation_slots": unit.reservation_slots.filter(
                    start_time__gte=start_of_day, 
                    start_time__lte=end_of_day
                ).order_by('start_time')
            } 
            for unit in units
        ]

        html = render_to_string(
            "reservations_table.html",
            {
                "units_with_slots": units_with_slots,
                "hours": hours,
                "category_name":category.category_name,
                "category_id":category_id,
                "unit_id":2
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
    # Fetch all categories that belong to offers managed by the current user
    categories = Category.objects.filter(
        belongs_to_offer__manager_of_this_offer=request.user
    )

    # Fetch reservations for those categories
    reservations = (
        Reservation.objects.filter(belongs_to_category__in=categories)
        .select_related("belongs_to_category", "belongs_to_category__belongs_to_offer")
        .order_by(
            "belongs_to_category__belongs_to_offer__offer_name", "reservation_from"
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
                proposed_end_time = slot.start_time + timedelta(minutes=slot.duration)

                # Check if the reservation fits in the slot without overlapping with the next slot.
                next_slot = slots.filter(start_time__gt=slot.start_time).first()
                if next_slot:
                    if (
                        reservation.reservation_from >= slot.start_time
                        and reservation.reservation_to <= proposed_end_time
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
                        and reservation.reservation_to <= proposed_end_time
                    ):
                        # The reservation fits in this slot.
                        slot.status = "reserved"
                        slot.save()
                        print("B")
                    # return True
        # there are no slots yet
        else:
            # Calculate total required slots to cover the reservation
            slot_duration = timedelta(minutes=30)
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


def unit_exist(reservation):
    # if there is a unit this reservation and has slots in this day return true
    # so in another function it will be necessary to check if the times collide
    # else return false
    #
    pass


def assign_reservation():
    pass


def create_unit(reservation):
    category = reservation.belongs_to_category
    if category.get_unit_count() < category.count_of_units:
        unit = Unit.objects.create(
            unit_name="z23",  # Provide the unit name here - to be done
            belongs_to_category=category,  # Assign the category instance
        )
        unit.save()
        print("unit created")  # to be done - messages
    else:
        print("max units reached")  # to be done - messages


def check_category_availability():
    pass
    # return true/false?

def reservation_details(request):
     # Extract parameters from the query string
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    category_id = request.GET.get('category')

    # Use the category_id to get the Category object and its name
    category = None
    category_name = ''
    if category_id:
        try:
            category = Category.objects.get(pk=category_id)
            category_name = category.category_name
        except Category.DoesNotExist:
            pass  # Handle the case where the category doesn't exist if necessary

    # Prepare the context
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'category_name': category_name,
        'category_id': category_id,  # Assuming you want to pass the ID for form submission
    }

    return render(request, 'reservation_details.html', context)

def verify_reservation(request, token):
    try:
        reservation = Reservation.objects.get(verification_token=token, status='pending')
        reservation.status = 'confirmed'
        reservation.save()
        return HttpResponse('Your reservation is confirmed. Thank you!')
    except Reservation.DoesNotExist:
        return HttpResponse('Invalid or expired link.')
    
import uuid
from django.http import HttpResponse
from .models import Reservation
from django.core.mail import send_mail
from django.conf import settings

def submit_reservation(request):
    if request.method == 'POST':
        customer_name = request.POST.get('name')
        customer_email = request.POST.get('email')
        # Assuming you retrieve these from the form or as parameters
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        category_id = request.POST.get('category_id')
        print("cat id",category_id)
        category = get_object_or_404(Category, pk=category_id)
        token = uuid.uuid4().hex

        reservation = Reservation(
            customer_name=customer_name,
            customer_email=customer_email,
            reservation_from=start_date,
            reservation_to=end_date,
            verification_token=token,
            belongs_to_category=category,
            status='pending'
        )
        reservation.save()

        verification_link = request.build_absolute_uri(f'/verify_reservation/{token}/')
        send_mail(
            'Verify your reservation',
            f'Please click on the link to confirm your reservation: {verification_link}',
            settings.DEFAULT_FROM_EMAIL,
            [customer_email],
            fail_silently=False,
        )
        return HttpResponse('Please check your email to confirm the reservation.')
