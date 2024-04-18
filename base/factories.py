import datetime  # Import the datetime module
from django.utils import timezone  # Import timezone for making time aware

import factory
from .models import Category  # Ensure your model imports are correct
from base.models import Category, Offer, Reservation, ReservationSlot, Unit

from base import models


# Use datetime.datetime.combine correctly with datetime.date.today() and datetime.time
# opening_time = timezone.make_aware(datetime.datetime.combine(datetime.date.today(), datetime.time(8, 0)))
# closing_time = timezone.make_aware(datetime.datetime.combine(datetime.date.today(), datetime.time(23, 59, 59)))
class OfferFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Offer

    offer_name = factory.Sequence(lambda n: f"Offer {n}")
    available_from = factory.Faker("date_between", start_date="-1y", end_date="today")
    available_to = factory.Faker("date_between", start_date="today", end_date="+1y")
    created_at = factory.LazyFunction(timezone.now)
    """manager_of_this_offer = factory.Maybe(
        factory.Faker('boolean', chance_of_getting_true=75),
        yes_declaration=factory.SubFactory('base.UserFactory'),  # Correct path needed
        no_declaration=None
    )"""

    class Params:
        # Use a param to control whether an offer should have dates set or not.
        with_dates = factory.Trait(
            available_from=factory.Faker("past_date"),
            available_to=factory.Faker("future_date"),
        )


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    category_name = factory.Faker("word")
    category_description = factory.Faker("text")
    category_capacity = 20
    max_simultaneous_reservations = 5
    count_of_units = 5
    belongs_to_offer = factory.SubFactory(OfferFactory)


# Correct the import usage in other factories similarly if they use datetime


class UnitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Unit

    unit_name = factory.Sequence(lambda n: f"Unit {n}")
    belongs_to_category = factory.SubFactory(CategoryFactory)


class ReservationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Reservation

    reservation_from = timezone.make_aware(datetime.datetime.now())
    reservation_to = timezone.make_aware(
        datetime.datetime.now() + datetime.timedelta(hours=2)
    )
    submission_time = timezone.now()
    confirmed_by_manager = "A"
    customer_email = factory.Faker("email")
    customer_name = factory.Faker("name")
    verification_token = factory.Faker("sha256")
    belongs_to_category = factory.SubFactory(CategoryFactory)
    status = "confirmed"


class ReservationSlotFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReservationSlot

    unit = factory.SubFactory(UnitFactory)
    reservation = factory.SubFactory(ReservationFactory)
    start_time = factory.LazyAttribute(lambda _: round_to_next_hour(timezone.now()))
    end_time = factory.LazyAttribute(
        lambda o: o.start_time + datetime.timedelta(hours=1)
    )
    duration = factory.LazyAttribute(lambda _: datetime.timedelta(minutes=60))

    status = "available"


def round_to_next_hour(dt):
    """Rounds a datetime object to the next whole hour."""
    return (
        dt
        + datetime.timedelta(hours=1)
        - datetime.timedelta(
            minutes=dt.minute, seconds=dt.second, microseconds=dt.microsecond
        )
    )
