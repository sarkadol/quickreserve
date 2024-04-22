from django.test import TestCase
from base.factories import (
    CategoryFactory,
    OfferFactory,
    UnitFactory,
    ReservationFactory,
    ReservationSlotFactory,
    UserFactory,
    ManagerProfileFactory,
)


class ModelCreationTest(TestCase):
    def test_category_creation(self):
        category = CategoryFactory()
        self.assertIsNotNone(category.id, "Failed to create a category")

    def test_offer_creation(self):
        offer = OfferFactory()
        self.assertIsNotNone(offer.id, "Failed to create an offer")

    def test_unit_creation(self):
        unit = UnitFactory()
        self.assertIsNotNone(unit.id, "Failed to create a unit")

    def test_reservation_creation(self):
        reservation = ReservationFactory()
        self.assertIsNotNone(reservation.id, "Failed to create a reservation")

    def test_slot_creation(self):
        slot = ReservationSlotFactory()
        self.assertIsNotNone(slot.id, "Failed to create a reservation slot")

    def test_manager_profile_creation(self):
        profile = ManagerProfileFactory()
        self.assertIsNotNone(profile.id, "Failed to create a manager profile")

    def test_user_creation(self):
        user = UserFactory()
        self.assertIsNotNone(user.id, "Failed to create a user")
