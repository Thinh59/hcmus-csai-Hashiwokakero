import heapq
import sys
import time
from pysat.formula import CNF

def count_unsatisfied_clauses(cnf, assignment, var_index_map):
    unsatisfied_count = 0
    for clause in cnf.clauses:
        is_satisfied = False
        for lit in clause:
            var = abs(lit)
            if var not in var_index_map: continue # Safe check
            
            idx = var_index_map[var]
            val = assignment[idx]
            
            # Nếu literal đúng với assignment hiện tại
            if (lit > 0 and val is True) or (lit < 0 and val is False):
                is_satisfied = True
                break
        
        if not is_satisfied:
            unsatisfied_count += 1
            
    return unsatisfied_count

def unit_propagate(assignment, cnf, var_index_map):
    changed = True
    while changed:
        changed = False
        for clause in cnf.clauses:
            unassigned = []
            status = "unresolved"
            
            for lit in clause:
                var = abs(lit)
                if var not in var_index_map: continue
                
                idx = var_index_map[var]
                val = assignment[idx]

                if val is None:
                    unassigned.append((var, lit))
                elif (lit > 0 and val) or (lit < 0 and not val):
                    status = "satisfied"
                    break
            
            if status == "satisfied": continue
            if not unassigned: return None # Conflict
            
            # Unit clause -> Bắt buộc gán
            if len(unassigned) == 1:
                var, lit = unassigned[0]
                idx = var_index_map[var]
                forced_value = (lit > 0)

                if assignment[idx] is None:
                    assignment[idx] = forced_value
                    changed = True
                elif assignment[idx] != forced_value:
                    return None # Conflict
                    
    return assignment

def is_complete_assignment(assignment):
    return all(val is not None for val in assignment)


def expand_state(cnf, assignment, variables, var_index_map):
    next_states = []

    next_var_idx = -1
    for i, var in enumerate(variables):
        # Kiểm tra biên an toàn
        if i < len(assignment) and assignment[var_index_map[var]] is None:
            next_var_idx = i
            break
            
    if next_var_idx == -1:
        return next_states

    current_var = variables[next_var_idx]
    idx = var_index_map[current_var]

    # Thử gán True và False
    for val in [True, False]: 
        try:
            new_assign = list(assignment) # Copy
            new_assign[idx] = val

            propagated = unit_propagate(new_assign, cnf, var_index_map)
            
            if propagated is not None:
                num_assigned = sum(1 for x in propagated if x is not None)
                next_states.append((num_assigned, propagated))
        except Exception:
            continue

    return next_states

def solve_cnf_astar(cnf: CNF, time_limit=30):
    start_time = time.time()

    all_vars = set()
    for clause in cnf.clauses:
        for lit in clause:
            all_vars.add(abs(lit))
            
    if not all_vars: return [], {}, []

    var_freq = {v: 0 for v in all_vars}
    for clause in cnf.clauses:
        for lit in clause: var_freq[abs(lit)] += 1

    variables = sorted(all_vars, key=lambda v: -var_freq[v])
    var_index_map = {var: i for i, var in enumerate(variables)}
    
    n_vars = len(variables)
    assignment = [None] * n_vars
    
    # Khởi tạo
    assignment = unit_propagate(assignment, cnf, var_index_map)
    if assignment is None: return None

    h = count_unsatisfied_clauses(cnf, assignment, var_index_map)
    num_assigned = sum(1 for x in assignment if x is not None)
    
    counter = 0
    open_list = []
    heapq.heappush(open_list, (h, -num_assigned, counter, assignment))

    iterations = 0
    while open_list:
        iterations += 1
        
        if iterations % 1000 == 0:
            if time.time() - start_time > time_limit:
                return None # Timeout

        h_score, neg_depth, _, current_assign = heapq.heappop(open_list)

        if h_score == 0 and is_complete_assignment(current_assign):
            model = []
            for var in variables:
                idx = var_index_map[var]
                val = current_assign[idx]
                model.append(var if val else -var)
            return model, var_index_map, variables

        try:
            next_nodes = expand_state(cnf, current_assign, variables, var_index_map)
            
            for new_num, new_assign in next_nodes:
                new_h = count_unsatisfied_clauses(cnf, new_assign, var_index_map)
                counter += 1
                heapq.heappush(open_list, (new_h, -new_num, counter, new_assign))
                
        except Exception:
            continue

    return None