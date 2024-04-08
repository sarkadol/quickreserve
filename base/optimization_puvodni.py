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
