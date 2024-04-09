import pulp
from datetime import date, datetime, timedelta
from django.utils import timezone

from base.views import create_slots_for_unit, delete_available_slots_for_category
from .models import Category, Unit, ReservationSlot, Reservation

def optimize_category(category, day=None):  # day = today as default value
    print("Starting optimization")

    if day is None:
        day = timezone.now().date()  # Use today's date if no date is provided
        #day = date(2024, 4, 8)

    day_start = timezone.make_aware(datetime.combine(day, datetime.min.time()))
    day_end = timezone.make_aware(datetime.combine(day, datetime.max.time()))


    # Fetch all units in the given category
    units = Unit.objects.filter(belongs_to_category=category)
    print(f"> Initial units in category '{category}': {[unit.id for unit in units]}")

    #fetch all reservations
    reservations = Reservation.objects.filter(
        belongs_to_category=category,
        reservation_to__gte=day_start,
        reservation_from__lte=day_end
        
    ).distinct()

    print("> Reservations for the day:\n" + "\n".join([
        f"Reservation from {reservation.reservation_from.strftime('%H:%M')} to {reservation.reservation_to.strftime('%H:%M')} by {reservation.customer_name} ({reservation.status})"
        for reservation in reservations
    ]))

    # Fetch all reservation slots for the specified day and category
    slots = ReservationSlot.objects.filter(
        unit__belongs_to_category=category,
        start_time__gte=day_start,
        start_time__lt=day_end
    )
    for unit in units:
        create_slots_for_unit(unit, day,category.opening_time, category.closing_time)

    print(f"> Slots for day {day}:")
    for slot in slots:
        print(f"{slot.unit.id} - {slot.start_time.strftime('%H:%M')} - {slot.status} ")
        
    #optimize   
    optimize_category_max_units_free(units, slots, reservations)
    #optimize_category_equally_distributed(units, slots, reservations)

    delete_available_slots_for_category(category)

    print(f"OPTIMIZED Slots for day {day}:")
    for slot in slots:
        print(f"{slot.unit.id} - {slot.start_time.strftime('%H:%M')} - {slot.status} ")

import pulp
from collections import defaultdict

import pulp

def optimize_category_max_units_free(units, slots, reservations):
    # Create a linear programming problem
    prob = pulp.LpProblem("Unit_Minimization", pulp.LpMinimize)
    
    # Create a variable for each unit-reservation pair, where variable is 1 if the reservation is in the unit
    x = pulp.LpVariable.dicts("unit_reservation", 
                              ((unit.id, reservation.id) for unit in units for reservation in reservations),
                              cat='Binary')
    
    # Objective function: Minimize the number of units used
    prob += pulp.lpSum(x[unit.id, reservation.id] for unit in units for reservation in reservations)

    # Constraint: Each reservation must be in exactly one unit
    for reservation in reservations:
        prob += pulp.lpSum(x[unit.id, reservation.id] for unit in units) == 1, f"One_Unit_Per_Reservation_{reservation.id}"
    
    # Constraint: No overlapping reservations in any unit
    for unit in units:
        for r1 in reservations:
            for r2 in reservations:
                if r1.id != r2.id and not (r1.reservation_to <= r2.reservation_from or r1.reservation_from >= r2.reservation_to):
                    prob += x[unit.id, r1.id] + x[unit.id, r2.id] <= 1, f"No_Overlap_{unit.id}_{r1.id}_{r2.id}"
    
    # Solve the problem
    prob.solve()
    
    # Prepare to print results
    unit_reservations = {}
    for unit in units:
        assigned_reservations = [reservation for reservation in reservations if pulp.value(x[unit.id, reservation.id]) == 1]
        unit_reservations[unit.id] = assigned_reservations

    # Print the results in a formatted table
    print("------------TABLE---------------")
    for unit_id, assigned_reservations in unit_reservations.items():
        reservation_details = ", ".join(
            f"Reservation from {reservation.reservation_from.strftime('%H:%M')} to {reservation.reservation_to.strftime('%H:%M')} by {reservation.customer_name} ({reservation.status})"
            for reservation in assigned_reservations
        )
        print(f"unit{unit_id}: {reservation_details}")
    print("------------TABLE END------------")    

    # Apply the results to the slots
    for slot in slots:
        for unit in units:
            if any(pulp.value(x[unit.id, reservation.id]) == 1 for reservation in reservations if slot.start_time >= reservation.reservation_from and slot.start_time < reservation.reservation_to):
                slot.status = 'reserved'  # Mark slot as reserved if any reservation is scheduled in this slot
                slot.reservation = reservation
    
    print("Optimization complete.")

# Remember to handle exceptions and edge cases in your actual implementation.


import pulp

def optimize_category_equally_distributed(units, slots, reservations):
    # Create a linear programming problem
    prob = pulp.LpProblem("Reservation_Distribution", pulp.LpMinimize)
    
    # Create a variable for each unit-reservation pair, where variable is 1 if the reservation is in the unit
    x = pulp.LpVariable.dicts("unit_reservation", 
                              ((unit.id, reservation.id) for unit in units for reservation in reservations),
                              cat='Binary')
    
    # Auxiliary variable to capture the maximum number of reservations on any unit
    max_reservations = pulp.LpVariable("max_reservations", lowBound=0, cat='Continuous')
    
    # Objective function: Minimize the maximum number of reservations assigned to any unit
    prob += max_reservations

    # Constraints to link the max_reservations variable to the number of reservations per unit
    for unit in units:
        prob += max_reservations >= pulp.lpSum(x[unit.id, reservation.id] for reservation in reservations), f"Max_Reservations_{unit.id}"

    # Constraint: Each reservation must be in exactly one unit
    for reservation in reservations:
        prob += pulp.lpSum(x[unit.id, reservation.id] for unit in units) == 1, f"One_Unit_Per_Reservation_{reservation.id}"
    
    # Constraint: No overlapping reservations in any unit
    for unit in units:
        for r1 in reservations:
            for r2 in reservations:
                if r1.id != r2.id and not (r1.reservation_to <= r2.reservation_from or r1.reservation_from >= r2.reservation_to):
                    prob += x[unit.id, r1.id] + x[unit.id, r2.id] <= 1, f"No_Overlap_{unit.id}_{r1.id}_{r2.id}"
    
    # Solve the problem
    prob.solve()
    
    # Prepare to print results
    unit_reservations = {}
    for unit in units:
        assigned_reservations = [reservation for reservation in reservations if pulp.value(x[unit.id, reservation.id]) == 1]
        unit_reservations[unit.id] = assigned_reservations

    # Print the results in a formatted table
    print("------------TABLE---------------")
    for unit_id, assigned_reservations in unit_reservations.items():
        reservation_details = ", ".join(
            f"Reservation from {reservation.reservation_from.strftime('%H:%M')} to {reservation.reservation_to.strftime('%H:%M')} by {reservation.customer_name} ({reservation.status})"
            for reservation in assigned_reservations
        )
        print(f"unit{unit_id}: {reservation_details}")
    print("------------TABLE END------------")    

    # Apply the results to the slots
    for slot in slots:
        for unit in units:
            if any(pulp.value(x[unit.id, reservation.id]) == 1 for reservation in reservations if slot.start_time >= reservation.reservation_from and slot.start_time < reservation.reservation_to):
                slot.status = 'reserved'  # Mark slot as reserved if any reservation is scheduled in this slot
                slot.reservation = reservation
    
    print("Optimization complete.")

# This approach focuses on minimizing the maximum load on any unit, which helps distribute the wear more evenly across all units.
