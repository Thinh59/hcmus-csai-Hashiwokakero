import sys
import time
from typing import List, Tuple, Dict, Optional
from pysat.formula import CNF
from collections import defaultdict

sys.setrecursionlimit(20000)

def clause_status(clause: List[int], assignment: List[Optional[bool]], var_index_map: Dict[int,int]):
    unassigned = []
    for lit in clause:
        var = abs(lit)
        idx = var_index_map[var]
        val = assignment[idx]

        if val is None:
            unassigned.append((var, lit))
        else:
            if (lit > 0 and val) or (lit < 0 and not val):
                return "satisfied"

    if not unassigned:
        return "conflict"
    return unassigned


def unit_propagate(assignment: List[Optional[bool]], cnf: CNF, var_index_map: Dict[int,int]):
    changed = True
    iterations = 0
    max_iterations = len(assignment) + 100 # Safety buffer
    
    while changed and iterations < max_iterations:
        changed = False
        iterations += 1
        
        for clause in cnf.clauses:
            status = clause_status(clause, assignment, var_index_map)
            
            if status == "satisfied":
                continue
            if status == "conflict":
                return None
            
            if isinstance(status, list) and len(status) == 1:
                var, lit = status[0]
                idx = var_index_map[var]
                forced_val = (lit > 0)
                
                if assignment[idx] is None:
                    assignment[idx] = forced_val
                    changed = True
                else:
                    if assignment[idx] != forced_val:
                        return None
    
    return assignment


def is_complete_assignment(assignment: List[Optional[bool]]) -> bool:
    return all(val is not None for val in assignment)


def check_full_assignment(cnf: CNF, assignment: List[Optional[bool]], var_index_map: Dict[int,int]) -> bool:
    for clause in cnf.clauses:
        satisfied = False
        for lit in clause:
            var = abs(lit)
            idx = var_index_map[var]
            val = assignment[idx]
            
            if val is None: 
                satisfied = True
                break
            
            if (lit > 0 and val) or (lit < 0 and not val):
                satisfied = True
                break
        
        if not satisfied:
            return False
    
    return True


def select_most_constrained_variable(assignment: List[Optional[bool]], 
                                     cnf: CNF,
                                     var_index_map: Dict[int,int],
                                     variables: List[int]) -> Optional[int]:

    var_frequency = defaultdict(int)
    
    for clause in cnf.clauses:
        status = clause_status(clause, assignment, var_index_map)
        if status == "satisfied":
            continue
        
        if isinstance(status, list):
            for var, lit in status:
                var_frequency[var] += 1
    
    best_var_idx = None
    best_freq = -1
    
    # Tìm biến chưa gán có điểm cao nhất
    for i, val in enumerate(assignment):
        if val is None:
            var = variables[i]
            freq = var_frequency[var]
            if freq > best_freq:
                best_freq = freq
                best_var_idx = i
                
    return best_var_idx


def choose_value_order(var: int, cnf: CNF, assignment: List[Optional[bool]], 
                        var_index_map: Dict[int, int]) -> Tuple[bool, bool]:
    pos_benefit = 0
    neg_benefit = 0
    
    for clause in cnf.clauses:
        status = clause_status(clause, assignment, var_index_map)
        if status == "satisfied":
            continue
        
        if isinstance(status, list):
            for clause_var, lit in status:
                if clause_var == var:
                    if lit > 0:
                        pos_benefit += 1
                    else:
                        neg_benefit += 1
                    break

    if pos_benefit >= neg_benefit:
        return (True, False)
    else:
        return (False, True)


def solve_cnf_backtracking(cnf: CNF, time_limit=30):
    start_time = time.time()

    var_scores = defaultdict(float)
    for clause in cnf.clauses:
        weight = 10.0 / len(clause) if len(clause) > 0 else 0
        for lit in clause:
            var = abs(lit)
            var_scores[var] += weight

    variables = sorted(var_scores.keys(), key=lambda v: -var_scores[v])
    var_index_map = {var: i for i, var in enumerate(variables)}

    assignment = [None] * len(variables)

    assignment = unit_propagate(assignment, cnf, var_index_map)
    if assignment is None:
        return None

    nodes = 0

    def dfs(assign: List[Optional[bool]]):
        nonlocal nodes
        nodes += 1
        
        if nodes % 1000 == 0:
            if time.time() - start_time > time_limit:
                return "TIMEOUT"

        if is_complete_assignment(assign):
            if check_full_assignment(cnf, assign, var_index_map):
                model = [
                    var if assign[var_index_map[var]] else -var
                    for var in variables
                ]
                return model
            else:
                return None

        next_idx = select_most_constrained_variable(assign, cnf, var_index_map, variables)
        
        if next_idx is None:
            return None 

        var = variables[next_idx]
        
        value_order = choose_value_order(var, cnf, assign, var_index_map)

        for val in value_order:
            new_assign = assign[:]
            new_assign[next_idx] = val

            propagated = unit_propagate(new_assign, cnf, var_index_map)
            if propagated is None:
                continue

            result = dfs(propagated)
            
            if result == "TIMEOUT": return "TIMEOUT" # Bubble up timeout
            if result is not None: return result

        return None

    model = dfs(assignment)

    if model == "TIMEOUT":
        return None 
        
    if model is None:
        return None

    return model, var_index_map, variables