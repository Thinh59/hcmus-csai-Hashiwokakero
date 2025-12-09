from pysat.solvers import Glucose3

def solve_cnf(cnf):
    with Glucose3(bootstrap_with=cnf) as solver:
        if solver.solve():
            return solver.get_model()
    return None


def model_to_connections(model, var_map):
    true_vars = set(v for v in model if v > 0)
    connections = {}

    for edge, (v1, v2) in var_map.items():

        count = 0
        if v2 in true_vars:
            count = 2
        elif v1 in true_vars:
            count = 1

        if count > 0:
            connections[edge] = count

    return connections
