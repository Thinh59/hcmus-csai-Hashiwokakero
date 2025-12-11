import heapq
import time
from pysat.formula import CNF

def count_unsatisfied_clauses(cnf, assignment, var_index_map):
    """Heuristic: số mệnh đề chưa thỏa."""
    unsatisfied = 0
    for clause in cnf.clauses:
        satisfied = False
        undecided = False

        for lit in clause:
            var = abs(lit)
            if var not in var_index_map:
                continue

            idx = var_index_map[var]
            val = assignment[idx]

            if val is None:
                undecided = True
                continue
            
            if (lit > 0 and val) or (lit < 0 and not val):
                satisfied = True
                break

        if not satisfied:
            unsatisfied += 1
    return unsatisfied


def unit_propagate(assignment, cnf, var_index_map):
    """Lan truyền đơn vị. Trả về assignment mới hoặc None nếu conflict."""
    changed = True
    while changed:
        changed = False

        for clause in cnf.clauses:
            unassigned = []
            clause_satisfied = False

            for lit in clause:
                var = abs(lit)
                if var not in var_index_map:
                    continue

                idx = var_index_map[var]
                val = assignment[idx]

                if val is None:
                    unassigned.append((var, lit))
                elif (lit > 0 and val) or (lit < 0 and not val):
                    clause_satisfied = True
                    break

            if clause_satisfied:
                continue

            # không literal nào thỏa và không unassigned -> conflict
            if not unassigned:
                return None
            
            # clause đơn -> gán bắt buộc
            if len(unassigned) == 1:
                var, lit = unassigned[0]
                idx = var_index_map[var]
                forced_value = (lit > 0)

                if assignment[idx] is None:
                    assignment[idx] = forced_value
                    changed = True
                elif assignment[idx] != forced_value:
                    return None  # conflict
    return assignment


def is_complete_assignment(assignment):
    return all(v is not None for v in assignment)


def expand_state(cnf, assignment, variables, var_index_map):
    """Tìm biến chưa gán đầu tiên, thử True/False."""
    for var in variables:
        idx = var_index_map[var]
        if assignment[idx] is None:
            next_var = var
            break
    else:
        return []  # full assignment

    idx = var_index_map[next_var]
    children = []

    for val in [True, False]:
        new_assign = assignment.copy()
        new_assign[idx] = val
        propagated = unit_propagate(new_assign, cnf, var_index_map)
        if propagated is not None:
            children.append(propagated)

    return children


def solve_cnf_astar(cnf: CNF, time_limit=60):
    start_time = time.time()

    # Tập biến
    all_vars = {abs(lit) for clause in cnf.clauses for lit in clause}
    if not all_vars:
        return [], {}, []

    # Sắp xếp biến theo tần suất xuất hiện
    var_freq = {v: 0 for v in all_vars}
    for clause in cnf.clauses:
        for lit in clause:
            var_freq[abs(lit)] += 1

    variables = sorted(all_vars, key=lambda v: -var_freq[v])
    var_index_map = {v: i for i, v in enumerate(variables)}

    n_vars = len(variables)
    assignment = [None] * n_vars

    # Unit propagate ban đầu
    assignment = unit_propagate(assignment, cnf, var_index_map)
    if assignment is None:
        return None  # UNSAT

    # g = số lần mở rộng (ban đầu = 0)
    g = 0
    h = count_unsatisfied_clauses(cnf, assignment, var_index_map)
    f = g + h

    # Heap entry: (f, g, counter, assignment, h)
    pq = []
    counter = 0
    heapq.heappush(pq, (f, g, counter, assignment, h))

    iterations = 0

    while pq:
        iterations += 1

        if time.time() - start_time > time_limit:
            return None  # Timeout

        f_cur, g_cur, _, current_assign, h_cur = heapq.heappop(pq)

        # Nếu tất cả clause thỏa và assignment đầy đủ -> tìm được nghiệm SAT
        if h_cur == 0 and is_complete_assignment(current_assign):
            model = []
            for var in variables:
                idx = var_index_map[var]
                val = current_assign[idx]
                model.append(var if val else -var)
            return model, var_index_map, variables

        # Mở rộng trạng thái -> mỗi lần expand = tăng g lên 1 (đúng A*)
        next_g = g_cur + 1

        # Sinh các trạng thái con
        children = expand_state(cnf, current_assign, variables, var_index_map)

        for child_assign in children:
            child_h = count_unsatisfied_clauses(cnf, child_assign, var_index_map)
            child_f = next_g + child_h
            counter += 1
            heapq.heappush(pq, (child_f, next_g, counter, child_assign, child_h))

    return None
