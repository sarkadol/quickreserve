import pulp
from datetime import datetime, timedelta
from django.utils import timezone

from base.views import create_slots_for_unit, delete_available_slots_for_category
from .models import Category, Unit, ReservationSlot, Reservation

def optimize_category(category, day=None):  # day = today as default value
    print("Starting optimization")

    if day is None:
        day = timezone.now().date()  # Use today's date if no date is provided

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
        print(f"{slot.unit.id} - {slot.start_time.strftime('%H:%M:%S')} - {slot.status} ")
        
    #optimize   
    optimize_category_max_units_free(units, slots, reservations)

    delete_available_slots_for_category(category)

    print(f"OPTIMIZED Slots for day {day}:")
    for slot in slots:
        print(f"{slot.unit.id} - {slot.start_time.strftime('%H:%M:%S')} - {slot.status} ")

import pulp

def optimize_category_max_units_free(units, slots, reservations):
    # Filter out slots that are not available
    available_slots = [slot for slot in slots if slot.status == 'available']
    
    # Create the optimization problem
    prob = pulp.LpProblem("Minimize_Units_Used", pulp.LpMinimize)
    
    # Variables: x[(slot_id, unit_id)] = 1 if slot is assigned to unit, else 0
    x = pulp.LpVariable.dicts("slot_to_unit", 
                              ((slot.id, unit.id) for slot in available_slots for unit in units if slot.unit == unit),
                              cat='Binary')

    # Variable: y[unit_id] = 1 if unit is used at all, else 0
    y = pulp.LpVariable.dicts("unit_used", 
                              (unit.id for unit in units), 
                              cat='Binary')

    # Objective: Minimize the number of units used
    prob += pulp.lpSum(y[unit.id] for unit in units)

    # Constraints: Each slot is assigned to exactly one unit
    for slot in available_slots:
        prob += pulp.lpSum(x[(slot.id, unit.id)] for unit in units if (slot.id, unit.id) in x) == 1

    # Constraints: Unit is used if any slot is assigned to it
    for unit in units:
        prob += pulp.lpSum(x[(slot.id, unit.id)] for slot in available_slots if (slot.id, unit.id) in x) <= 1000 * y[unit.id]

    # Solve the problem
    prob.solve()

    # Output results
    for slot in available_slots:
        for unit in units:
            if (slot.id, unit.id) in x and pulp.value(x[(slot.id, unit.id)]) == 1:
                slot.status = "HAHA"
                #print(f"Slot {slot.id} is assigned to unit {unit.id}")

# Note: You should add actual DB update logic where needed after testing


    

def optimize_category_equally_distributed(category, day=None):
    if day is None:
        day = datetime.now().date()  # Use today's date if no date is provided

    # Fetch all units in the given category
    units = Unit.objects.filter(belongs_to_category=category)

    # Fetch all reservation slots for the specified day and category
    day_start = datetime.combine(day, datetime.min.time())
    day_end = datetime.combine(day, datetime.max.time())
    slots = ReservationSlot.objects.filter(
        unit__belongs_to_category=category,
        start_time__gte=day_start,
        start_time__lt=day_end,
        status="available"
    ).select_related('unit').distinct()

    # Create the LP problem
    prob = pulp.LpProblem("Category_Optimization_Equal_Distribution", pulp.LpMinimize)
    
    # Create variables
    x = pulp.LpVariable.dicts(
        "x",
        ((slot.id, unit.id) for slot in slots for unit in units if slot.unit == unit),
        cat='Binary'
    )
    # y variables to count the reservations per unit
    y = pulp.LpVariable.dicts("y", [unit.id for unit in units], lowBound=0, cat='Continuous')

    # Objective function: Minimize the variance of reservations
    avg_reservations = pulp.lpSum(y[unit.id] for unit in units) / len(units)
    prob += pulp.lpSum((y[unit.id] - avg_reservations)**2 for unit in units)

    # Constraints
    for slot in slots:
        prob += pulp.lpSum(x[slot.id, unit.id] for unit in units if slot.unit == unit) == 1  # Each slot is assigned to exactly one unit

    for unit in units:
        # Link y to the sum of x for each unit
        prob += y[unit.id] == pulp.lpSum(x[slot.id, unit.id] for slot in slots if slot.unit == unit)

        # Ensure non-overlapping reservations for each unit
        for slot_i in slots:
            for slot_k in slots:
                if slot_i != slot_k and slot_i.unit == slot_k.unit:
                    overlap = not (
                        slot_i.end_time <= slot_k.start_time or
                        slot_i.start_time >= slot_k.end_time
                    )
                    if overlap:
                        prob += x[slot_i.id, unit.id] + x[slot_k.id, unit.id] <= 1

    # Solve the problem
    prob.solve()

    # Collect and print the results
    unit_assignments = {}
    for unit in units:
        assigned_slots = []
        for slot in slots:
            if slot.unit == unit and pulp.value(x[(slot.id, unit.id)]) == 1:
                assigned_slots.append(slot)
        if assigned_slots:
            unit_assignments[unit.id] = assigned_slots

    # Print the results
    for unit, slts in unit_assignments.items():
        print(f"{unit} = {', '.join(f'Slot at {sl.start_time.strftime('%Y-%m-%d %H:%M:%S')} for {sl.duration}' for sl in slts)}")
