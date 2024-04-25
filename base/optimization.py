# Standard library imports
from collections import defaultdict
from datetime import date, datetime, timedelta

# External libraries
import pulp

# Django utilities
from django.utils import timezone

# Imports from my project's modules
from .models import Category, Unit, ReservationSlot, Reservation


def optimize_category(category,day=None):  # day = today as default value
    from base.views import create_slots_for_unit, delete_available_slots_for_category
    print("Starting optimization")

    day_start, day_end = get_day_start_end(day)
    strategy = category.belongs_to_offer.manager_of_this_offer.managerprofile.optimization_strategy 

    # Fetch all units in the given category
    units = Unit.objects.filter(belongs_to_category=category)
    print(f"> Initial units in category '{category}': {[unit.id for unit in units]}")

    # fetch all reservations
    reservations = fetch_reservations(category, day_start, day_end)
    print(
        "> Reservations for the day:\n"
        + "\n".join(
            [
                f"Reservation from {reservation.reservation_from.strftime('%H:%M')} to {reservation.reservation_to.strftime('%H:%M')} by {reservation.customer_name} ({reservation.status})"
                for reservation in reservations
            ]
        )
    )

    # Fetch all reservation slots for the specified day and category
    slots = fetch_reservation_slots_op(category, day_start, day_end)

    for unit in units:
        create_slots_for_unit(unit, day, category.opening_time, category.closing_time)
    
    #select a strategy
    if strategy == "min_units":
        optimized_reservations_to_units = optimize_category_min_units(units, slots, reservations)
    elif strategy == "equally_distributed":
        optimized_reservations_to_units = optimize_category_equally_distributed_by_time(units, slots, reservations)

        print("equally_distributed OPT_STRATEGY")

    #print_results(units,reservations, optimized_reservations_to_units)
    #print_assignment_summary(units, reservations, optimized_reservations_to_units)
    print_assignment_summary_sorted(units, reservations, optimized_reservations_to_units)

    # optimized_reservations_to_units =optimize_category_free_time(units, slots, reservations) #not working yet
    # optimized_reservations_to_units =optimize_category_equally_distributed(units, slots, reservations)

    #print_assignment(optimized_reservations_to_units, units, reservations)
    assign_optimized_reservations_to_slots(
        units, reservations, optimized_reservations_to_units, slots
    )

    delete_available_slots_for_category(category)

    # print(f"OPTIMIZED Slots for day {day}:")
    # for slot in slots:
    #    print(f"{slot.unit.id} - {slot.start_time.strftime('%H:%M')} - {slot.status} ")


def fetch_reservations(category, day_start, day_end):
    """Fetch all reservations for the given day and category."""
    print("fetch_reservations",day_start,day_end)
    print("category ",category)
    return Reservation.objects.filter(
        belongs_to_category=category,
        reservation_to__gte=day_start,
        reservation_from__lte=day_end,
        status__in=[
            "confirmed",
            "pending",
        ],  # Only include confirmed and pending reservations
    ).distinct()


def fetch_reservation_slots_op(category, day_start, day_end):
    """Fetch all reservation slots for the specified day and category."""
    return ReservationSlot.objects.filter(
        unit__belongs_to_category=category,
        start_time__gte=day_start,
        start_time__lt=day_end,
    )


def get_day_start_end(day=None):
    """Returns the start and end time for a given day."""
    if day is None:
        day = timezone.now().date()
    day_start = timezone.make_aware(datetime.combine(day, datetime.min.time()))
    day_end = timezone.make_aware(datetime.combine(day, datetime.max.time()))
    return day_start, day_end


def optimize_category_min_units(units, slots, reservations):
    # Create a linear programming problem
    prob = pulp.LpProblem("Unit_Minimization", pulp.LpMinimize)

    # Create a binary variable for each unit to indicate if it's used
    y = pulp.LpVariable.dicts("unit_used", [unit.id for unit in units], cat="Binary")

    # Create a variable for each unit-reservation pair, where variable is 1 if the reservation is in the unit
    x = pulp.LpVariable.dicts(
        "unit_reservation",
        ((unit.id, reservation.id) for unit in units for reservation in reservations),
        cat="Binary",
    )

    # Objective function: Minimize the number of units used
    # prob += pulp.lpSum(x[unit.id, reservation.id] for unit in units for reservation in reservations)

    # Objective Function: Minimize the number of units used
    #prob += pulp.lpSum(y[unit.id] for unit in units)

    # Define the objective function as a summation of decision variables
    objective = pulp.lpSum(y[unit.id] for unit in units)

    # Explicitly set the objective function
    prob.setObjective(objective)

    # Constraint: Each reservation must be in exactly one unit
    for reservation in reservations:
        prob += (
            pulp.lpSum(x[unit.id, reservation.id] for unit in units) == 1,
            f"One_Unit_Per_Reservation_{reservation.id}",
        )

    # Constraint: No overlapping reservations in any unit
    for unit in units:
        for r1 in reservations:
            for r2 in reservations:
                if r1.id != r2.id and not (
                    r1.reservation_to <= r2.reservation_from
                    or r1.reservation_from >= r2.reservation_to
                ):
                    prob += (
                        x[unit.id, r1.id] + x[unit.id, r2.id] <= 1,
                        f"No_Overlap_{unit.id}_{r1.id}_{r2.id}",
                    )

    # Ensure the unit_used variable reflects whether any reservation is assigned to the unit
    for unit in units:
        for reservation in reservations:
            prob += (
                x[unit.id, reservation.id] <= y[unit.id],
                f"Link_Unit_{unit.id}_Reservation_{reservation.id}",
            )

    # Solve the problem
    #prob.solve()
    # Solve the problem
    status = prob.solve()

    # Check if no solution was found
    if status == pulp.LpStatusInfeasible:
        print("NO FEASIBLE SOLUTION FOUND")
        assignment_dict = {}
        return assignment_dict
    else:
        # Retrieving and returning Xij values
        assignment_dict = {
            (unit.id, reservation.id): pulp.value(x[unit.id, reservation.id])
            for unit in units
            for reservation in reservations
        }

        print("Optimization complete. PRINTING ASSIGMENT")
        return assignment_dict


# Remember to handle exceptions and edge cases in your actual implementation.
def assign_optimized_reservations_to_slots(units, reservations, assignment_dict, slots):
    """
    Updates the slots based on optimized assignment of reservations to units.

    :param units: QuerySet of Unit objects
    :param reservations: QuerySet of Reservation objects
    :param assignment_dict: Dict with keys as (unit_id, reservation_id) and values as 1 or 0, indicating assignment.
    :param slots: QuerySet of ReservationSlot objects for the day
    """
    slots.update(status="available", reservation=None)

    for (unit_id, reservation_id), assigned in assignment_dict.items():
        if assigned == 1:  # If the reservation is assigned to the unit
            reservation = next(
                (r for r in reservations if r.id == reservation_id), None
            )
            unit = next((u for u in units if u.id == unit_id), None)

            if reservation and unit:
                # Find slots that overlap with the reservation time in the specified unit
                overlapping_slots = slots.filter(
                    unit_id=unit.id,
                    start_time__lt=reservation.reservation_to,
                    end_time__gt=reservation.reservation_from,
                )
                for slot in overlapping_slots:
                    slot.status = "reserved"  # Update slot status
                    slot.reservation = reservation  # Assign the reservation to the slot
                    slot.save()  # Don't forget to save the slot object!
            else:
                print(
                    f"Skipping assignment for non-existing unit ({unit_id}) or reservation ({reservation_id})."
                )
        # You can extend this block to handle cases where assigned == 0 if necessary


def print_assignment(assignment_dict, units, reservations):
    print("-------------Reservation Assignments:\n")
    for unit in units:
        print(f"Unit {unit.id}:")
        assigned = False  # Track if any reservations are assigned to this unit
        for reservation in reservations:
            if assignment_dict.get((unit.id, reservation.id)) == 1:
                print(
                    f"  - Reservation {reservation.id} assigned. (Customer: {reservation.customer_name}, Time: {reservation.reservation_from.strftime('%H:%M')} to {reservation.reservation_to.strftime('%H:%M')})"
                )
                assigned = True
        if not assigned:
            print("  No reservations assigned.")
        print("")  # Add an empty line for better readability between units


# This approach focuses on minimizing the maximum load on any unit, which helps distribute the wear more evenly across all units.

def optimize_category_equally_distributed_by_time(units, slots,reservations):    

    # Initialize the linear programming problem
    prob = pulp.LpProblem("Equally_Distributed_Time", pulp.LpMinimize)

    # Create variables for each unit-reservation pair
    x = pulp.LpVariable.dicts(
        "unit_reservation",
        ((unit.id, reservation.id) for unit in units for reservation in reservations),
        cat="Binary"
    )

    # Objective function to minimize the maximum total reserved time on any unit
    max_time = pulp.LpVariable("max_time", lowBound=0, cat="Continuous")

    # Define the objective function to minimize the maximum total reserved time on any unit
    objective = max_time

    # Explicitly set the objective function using setObjective
    prob.setObjective(objective)
    
    # Constraint: Link the maximum time variable to the total reserved time per unit
    for unit in units:
        total_time_for_unit = pulp.lpSum(
            x[unit.id, reservation.id] * (reservation.reservation_to - reservation.reservation_from).total_seconds() / 3600
            for reservation in reservations
        )
        prob += max_time >= total_time_for_unit, \
               f"max_time_per_unit_{unit.id}"

    # Constraint: Each reservation must be in exactly one unit
    for reservation in reservations:
        prob += (
            pulp.lpSum(x[unit.id, reservation.id] for unit in units) == 1,
            f"One_Unit_Per_Reservation_{reservation.id}",
        )

    # Constraint: No overlapping reservations in any unit
    for unit in units:
        for r1 in reservations:
            for r2 in reservations:
                if r1.id != r2.id and not (
                    r1.reservation_to <= r2.reservation_from
                    or r1.reservation_from >= r2.reservation_to
                ):
                    prob += (
                        x[unit.id, r1.id] + x[unit.id, r2.id] <= 1,
                        f"No_Overlap_{unit.id}_{r1.id}_{r2.id}",
                    )
                    
    # Solve the problem
    status = prob.solve()

    # Check if no solution was found
    if status == pulp.LpStatusInfeasible:
        print("NO FEASIBLE SOLUTION FOUND")
        assignment_dict = {}
        return assignment_dict
    else:
        # Retrieving and returning Xij values
        assignment_dict = {
            (unit.id, reservation.id): pulp.value(x[unit.id, reservation.id])
            for unit in units
            for reservation in reservations
        }

        print("Optimization complete.")
        print("maximum time: ", max_time.value())
        return assignment_dict
    
# Utility Function: Print Detailed Assignment Results
# TODO not working by now
def print_results(units, reservations, assignment_dict):
    print("PRINTING FUNCTION")
    # Initialize a dictionary to hold reservation details by unit
    unit_reservations = defaultdict(list)
    for (unit_id, reservation_id), is_assigned in assignment_dict.items():
        if is_assigned == 1:
            reservation = next((r for r in reservations if r.id == reservation_id), None)
            if reservation:
                unit_reservations[unit_id].append(reservation)

    # Print the formatted results
    print("------------TABLE---------------")
    for unit_id in units:
        print(f"{unit_id}:")
        if unit_id in unit_reservations:
            for reservation in unit_reservations[unit_id]:
                print(f"  - Reservation from {reservation.reservation_from.strftime('%H:%M')} to {reservation.reservation_to.strftime('%H:%M')} by {reservation.customer_name} ({reservation.status})")
        else:
            print("  No reservations assigned.")
        print("")  # Add an empty line for better readability between units
    print("------------TABLE END------------")

# Function: Print Assignment Summary
def print_assignment_summary(units, reservations, assignment_dict):
    print("-------------Reservation Assignments summary:\n")
    for unit in units:
        print(f"Unit {unit.id}:")
        assigned = False  # Track if any reservations are assigned to this unit
        for reservation in reservations:
            if assignment_dict.get((unit.id, reservation.id)) == 1:
                print(
                    f"  - Reservation {reservation.id} assigned. (Time: {reservation.reservation_from.strftime('%H:%M')} to {reservation.reservation_to.strftime('%H:%M')}, Customer: {reservation.customer_name})"
                )
                assigned = True
        if not assigned:
            print("  No reservations assigned.")
        print("")  # Add an empty line for better readability between units

from datetime import datetime

def print_assignment_summary_sorted(units, reservations, assignment_dict):
    print("-------------Reservation Assignments Summary:\n")
    for unit in units:
        print(f"Unit {unit.id}:")

        # Collect reservations assigned to this unit
        unit_reservations = []
        for reservation in reservations:
            if assignment_dict.get((unit.id, reservation.id)) == 1:
                unit_reservations.append(reservation)

        # Sort reservations by the start time
        unit_reservations.sort(key=lambda x: x.reservation_from)

        # Print sorted reservations
        if unit_reservations:
            for reservation in unit_reservations:
                print(
                    f"  - Reservation {reservation.id:2} assigned. (Time: {reservation.reservation_from.strftime('%H:%M')} to {reservation.reservation_to.strftime('%H:%M')}, Customer: {reservation.customer_name})"
                )
        else:
            print("  No reservations assigned.")
        
        print("")  # Add an empty line for better readability between units

