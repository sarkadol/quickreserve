import pulp

# Example data: reservation times
reservations = {
    1: (6, 10),
    2: (12, 15),
    3: (7, 14),
    4: (7, 14),
    5: (2, 6),
    6: (2, 6)
}

# Create the LP problem
prob = pulp.LpProblem("Reservation_Optimization", pulp.LpMinimize)
# The goal it so minimize the use of units (maximize units that are fully available)


# Create variables
x = pulp.LpVariable.dicts("x", ((i, j) for i in reservations for j in range(1, len(reservations)+1)), cat='Binary')
y = pulp.LpVariable.dicts("y", range(1, len(reservations)+1), cat='Binary')

# Objective function
prob += pulp.lpSum(y[j] for j in range(1, len(reservations)+1))

# Constraints
for i in reservations:
    prob += pulp.lpSum(x[i, j] for j in range(1, len(reservations)+1)) == 1  # Each reservation in one unit

for j in range(1, len(reservations)+1):
    for i in reservations:
        for k in reservations:
            if i != k and not(reservations[i][1] <= reservations[k][0] or reservations[i][0] >= reservations[k][1]):
                prob += x[i, j] + x[k, j] <= 1  # No overlap in same unit

    prob += pulp.lpSum(x[i, j] for i in reservations) <= 1000 * y[j]  # Link x and y

# Solve the problem
prob.solve()

# Collect and print the results
unit_assignments = {}
for j in range(1, len(reservations)+1):
    assigned_reservations = []
    for i in reservations:
        if pulp.value(x[(i, j)]) == 1:
            assigned_reservations.append(reservations[i])
    if assigned_reservations:
        unit_assignments[y[j].name] = assigned_reservations
        
# Print the results
for unit, res in unit_assignments.items():
    print(f"{unit} = {', '.join(str(r) for r in res)}")


#odložený
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
