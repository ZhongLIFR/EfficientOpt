def build_model(instance):
    import gurobipy as gp
    from gurobipy import GRB

    model = gp.Model()
    clinic_count = instance['clinic_count']
    hub_count = instance['hub_count']
    clinic_demand = instance['clinic_demand']
    hub_capacity = instance['hub_capacity']
    hub_open_cost = instance['hub_open_cost']
    eligibility = instance['eligibility']
    assignment_cost = instance['assignment_cost']

    # binary variables for opening hubs
    y = model.addVars(hub_count, vtype=GRB.BINARY, obj=hub_open_cost, name='y')

    # build list of eligible (i,j) pairs and corresponding costs
    x_tuples = []
    x_obj = []
    hub_to_clinics = [[] for _ in range(hub_count)]
    for i in range(clinic_count):
        for j in eligibility[i]:
            x_tuples.append((i, j))
            x_obj.append(assignment_cost[i][j])
            hub_to_clinics[j].append(i)

    # assignment variables
    x = model.addVars(x_tuples, vtype=GRB.BINARY, obj=x_obj, name='x')

    # each clinic assigned to exactly one hub
    for i in range(clinic_count):
        model.addConstr(gp.quicksum(x[i, j] for j in eligibility[i]) == 1, name='assign_%d' % i)

    # capacity constraints per hub
    for j in range(hub_count):
        model.addConstr(gp.quicksum(clinic_demand[i] * x[i, j] for i in hub_to_clinics[j]) <= hub_capacity[j] * y[j], name='cap_%d' % j)

    model.update()
    return model
