from itertools import combinations

def at_least_k(lits, k):

    cnf = []
    n = len(lits)

    if k <= 0:
        return cnf
    if k > n:
        print(f"Warning: at_least_k({n} lits, k={k}) is impossible!")
        return [[]]  

    subset_size = n - k + 1
    if subset_size > 0:
        for subset in combinations(lits, subset_size):
            cnf.append(list(subset))
    
    return cnf


def at_most_k(lits, k):
    cnf = []
    n = len(lits)

    if k < 0:
        print(f"Warning: at_most_k({n} lits, k={k}) - negative k!")
        return [[]]  
    if k >= n:
        return cnf

    for subset in combinations(lits, k + 1):
        cnf.append([-x for x in subset])
    
    return cnf


def validate_input(islands, aligned_pairs):
    island_positions = {(r, c): (idx, val) for idx, (r, c, val) in enumerate(islands)}
    
    max_bridges = [0] * len(islands)
    
    for (r1, c1, r2, c2, orientation) in aligned_pairs:
        pos1 = (r1, c1)
        pos2 = (r2, c2)
        
        if pos1 in island_positions:
            idx1, _ = island_positions[pos1]
            max_bridges[idx1] += 2 
        
        if pos2 in island_positions:
            idx2, _ = island_positions[pos2]
            max_bridges[idx2] += 2

    for idx, (r, c, required) in enumerate(islands):
        available = max_bridges[idx]
        if required > available:
            return False, f"Island at ({r},{c}) needs {required} bridges but only {available} possible"
    
    return True, ""


def generate_cnf_total_bridges(var_map, islands):
    cnf = []
    
    for (r, c, val) in islands:
        lits = []

        for (x1, y1, x2, y2), (e1, e2) in var_map.items():
            if (x1, y1) == (r, c) or (x2, y2) == (r, c):
                lits.append(e1)
                lits.append(e2)
        
        if not lits:
            if val > 0:
                print(f"Island at ({r},{c}) needs {val} bridges but has no possible connections!")
                return [[]]  
            continue
        
        n = len(lits)

        if val > n:
            print(f"Island at ({r},{c}) needs {val} bridges but only {n} literals available!")
            return [[]]  

        cnf += at_least_k(lits, val)
        cnf += at_most_k(lits, val)
    
    return cnf


def generate_cnf_double_bridges(var_map):
    cnf = []
    for (edge, (e1, e2)) in var_map.items():
        cnf.append([-e2, e1])  
    return cnf


def generate_cnf_no_cross(var_map, aligned_pairs):
    cnf = []

    for i in range(len(aligned_pairs)):
        r1a, c1a, r2a, c2a, oa = aligned_pairs[i]
        
        for j in range(i + 1, len(aligned_pairs)):
            r1b, c1b, r2b, c2b, ob = aligned_pairs[j]

            crosses = False
            
            if oa == "H" and ob == "V":
                if (min(c1a, c2a) < c1b < max(c1a, c2a)) and \
                   (min(r1b, r2b) < r1a < max(r1b, r2b)):
                    crosses = True
            
            elif oa == "V" and ob == "H":
                if (min(c1b, c2b) < c1a < max(c1b, c2b)) and \
                   (min(r1a, r2a) < r1b < max(r1a, r2a)):
                    crosses = True
            
            if crosses:
                eA = (r1a, c1a, r2a, c2a)
                eB = (r1b, c1b, r2b, c2b)

                if eA in var_map and eB in var_map:
                    a1, a2 = var_map[eA]
                    b1, b2 = var_map[eB]
                    
                    cnf.append([-a1, -b1]) 
                    cnf.append([-a1, -b2])  
                    cnf.append([-a2, -b1])  
                    cnf.append([-a2, -b2])  
    
    return cnf


def export_cnf(clauses, OUTPUT_PATH="clauses.txt"):
    print(f"Total CNF clauses = {len(clauses)}")

    empty_clauses = [c for c in clauses if len(c) == 0]
    if empty_clauses:
        print(f"Warning: {len(empty_clauses)} empty clause(s) found - formula is UNSAT!")

    with open(OUTPUT_PATH, "w") as f:
        for clause in clauses:
            line = " ".join(str(x) for x in clause)
            f.write(line + "\n")
    
    print(f"CNF exported to: {OUTPUT_PATH}")