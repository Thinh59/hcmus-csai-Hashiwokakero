import os
import sys
import time
import json
from datetime import datetime
from pysat.formula import CNF

TIMEOUT_CONFIG = {
    "pysat": 30,        
    "astar": 30,        
    "backtracking": 30, 
    "bruteforce": 60    
}

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from helper_01 import read_input, identify_island, find_aligned_pairs, create_logic_vars
from helper_02 import (
    generate_cnf_total_bridges,
    generate_cnf_double_bridges,
    generate_cnf_no_cross,
    export_cnf,
    validate_input
)
from solver_pySAT import solve_cnf, model_to_connections
from solver_astar import solve_cnf_astar
from solver_backtracking import solve_cnf_backtracking
from solver_brute_force import solve_brute_force
from utils import build_output_grid, validate_solution, write_grid_to_file, print_grid, is_connected
from visual import process_all_files

def print_separator(title=""):
    print("\n" + "=" * 70)
    if title:
        print(f"  {title}")
        print("=" * 70)


def solve_with_pysat(cnf_clauses, var_map, islands, grid):
    print_separator("SOLVING WITH PYSAT (Iterative Mode)")
    
    start_time = time.time()
    from pysat.solvers import Glucose3
    solver = Glucose3()
    for clause in cnf_clauses:
        solver.add_clause(clause)
    
    attempts = 0
    best_model_conns = None
    TIME_LIMIT_LOOP = 30 
    
    while time.time() - start_time < TIME_LIMIT_LOOP:
        attempts += 1
        
        if not solver.solve():
            if attempts == 1:
                print("UNSAT - No solution found")
                return None, time.time() - start_time, False
            else:
                break 
        
        model = solver.get_model()
        
        connections = model_to_connections(model, var_map)
        converted_connections = {}
        for (r1, c1, r2, c2), count in connections.items():
            idx1 = next(i for i, (r, c, _) in enumerate(islands) if (r, c) == (r1, c1))
            idx2 = next(i for i, (r, c, _) in enumerate(islands) if (r, c) == (r2, c2))
            converted_connections[(idx1, idx2)] = count
        
        best_model_conns = converted_connections
        
        if is_connected(islands, converted_connections):
            elapsed = time.time() - start_time
            print(f"SAT - Found Connected Solution (Attempt {attempts})")
            output_grid = build_output_grid((len(grid), len(grid[0])), islands, converted_connections)
            print(f"Time: {elapsed:.4f}s")
            return output_grid, elapsed, True

        blocking_clause = [-lit for lit in model]
        solver.add_clause(blocking_clause)

    # print(f"Warning: Could not find connected solution in time. Returning disconnected result.")
    elapsed = time.time() - start_time
    # if best_model_conns:
    #     output_grid = build_output_grid((len(grid), len(grid[0])), islands, best_model_conns)
    #     return output_grid, elapsed, True
    
    return None, elapsed, False


def solve_with_astar(cnf_clauses, var_map, islands, grid, timeout=60):
    print_separator(f"SOLVING WITH A* (Timeout: {timeout}s)")
    
    start_time = time.time()

    current_clauses = list(cnf_clauses)
    best_model_conns = None
    attempts = 0
    
    while time.time() - start_time < timeout:
        attempts += 1
        remaining_time = timeout - (time.time() - start_time)
        if remaining_time < 1: break 
        
        cnf = CNF()
        cnf.clauses = current_clauses
        
        try:
            result = solve_cnf_astar(cnf, time_limit=remaining_time)
        except Exception as e:
            print(f"Error in A* solver: {e}")
            return None, time.time() - start_time, False
        
        if result is None:
            if attempts == 1:
                print("UNSAT or Timeout")
                return None, time.time() - start_time, False
            break
            
        model, _, _ = result
        
        connections = model_to_connections(model, var_map)
        converted_connections = {}
        for (r1, c1, r2, c2), count in connections.items():
            idx1 = next(i for i, (r, c, _) in enumerate(islands) if (r, c) == (r1, c1))
            idx2 = next(i for i, (r, c, _) in enumerate(islands) if (r, c) == (r2, c2))
            converted_connections[(idx1, idx2)] = count
            
        best_model_conns = converted_connections

        if is_connected(islands, converted_connections):
            elapsed = time.time() - start_time
            print(f"SAT - Found Connected Solution (Attempt {attempts})")
            output_grid = build_output_grid((len(grid), len(grid[0])), islands, converted_connections)
            print(f"Time: {elapsed:.4f}s")
            return output_grid, elapsed, True

        blocking_clause = [-lit for lit in model]
        current_clauses.append(blocking_clause)

    # print(f"A*: Returning best effort (disconnected) solution due to timeout.")
    elapsed = time.time() - start_time
    # if best_model_conns:
    #     output_grid = build_output_grid((len(grid), len(grid[0])), islands, best_model_conns)
    #     return output_grid, elapsed, True

    return None, elapsed, False


def solve_with_backtracking(cnf_clauses, var_map, islands, grid, timeout=60):
    print_separator(f"SOLVING WITH BACKTRACKING (Timeout: {timeout}s)")
    
    start_time = time.time()
    
    current_clauses = list(cnf_clauses)
    best_model_conns = None
    attempts = 0
    
    while time.time() - start_time < timeout:
        attempts += 1
        remaining_time = timeout - (time.time() - start_time)
        if remaining_time < 1: break
        
        cnf = CNF()
        cnf.clauses = current_clauses
        
        try:
            result = solve_cnf_backtracking(cnf, time_limit=remaining_time)
        except Exception as e:
            print(f"Error in Backtracking solver: {e}")
            return None, time.time() - start_time, False
            
        if result is None:
            if attempts == 1:
                print("UNSAT or Timeout")
                return None, time.time() - start_time, False
            break
            
        model, _, _ = result
        
        connections = model_to_connections(model, var_map)
        converted_connections = {}
        for (r1, c1, r2, c2), count in connections.items():
            idx1 = next(i for i, (r, c, _) in enumerate(islands) if (r, c) == (r1, c1))
            idx2 = next(i for i, (r, c, _) in enumerate(islands) if (r, c) == (r2, c2))
            converted_connections[(idx1, idx2)] = count
            
        best_model_conns = converted_connections
        
        if is_connected(islands, converted_connections):
            elapsed = time.time() - start_time
            print(f"SAT - Found Connected Solution (Attempt {attempts})")
            output_grid = build_output_grid((len(grid), len(grid[0])), islands, converted_connections)
            print(f"Time: {elapsed:.4f}s")
            return output_grid, elapsed, True
            
        blocking_clause = [-lit for lit in model]
        current_clauses.append(blocking_clause)

    # print(f"Backtracking: Returning best effort (disconnected) solution.")
    elapsed = time.time() - start_time
    # if best_model_conns:
    #     output_grid = build_output_grid((len(grid), len(grid[0])), islands, best_model_conns)
    #     return output_grid, elapsed, True

    return None, elapsed, False


def solve_with_bruteforce(grid, islands, timeout=30):
    print_separator(f"SOLVING WITH BRUTE FORCE (Timeout: {timeout}s)")
    
    start_time = time.time()
    connections = solve_brute_force(grid, islands, timeout=timeout)
    elapsed = time.time() - start_time
    
    if connections is None:
        print(f"No solution found (Timeout or Impossible) after {elapsed:.2f}s")
        return None, elapsed, False
    
    print("Solution found!")
    
    converted_connections = {}
    for (i, j), count in connections.items():
        converted_connections[(i, j)] = count
    
    output_grid = build_output_grid((len(grid), len(grid[0])), islands, converted_connections)
    print(f"Time: {elapsed:.4f}s")
    
    return output_grid, elapsed, True


def process_input_file(input_path, output_dir="Outputs", solver_type="all", verbose=False):
    
    print(f"\n# Processing: {os.path.basename(input_path)}")
    
    try:
        grid, islands = read_input(input_path)
    except FileNotFoundError:
        print(f"Error: File not found: {input_path}")
        return {"input_file": input_path, "error": "File not found", "valid": False}

    islands = identify_island(grid)
    aligned_pairs = find_aligned_pairs(islands)
    
    print(f"\nGrid Size: {len(grid)}x{len(grid[0])}")
    print(f"Islands: {len(islands)}")
    print(f"Possible Edges: {len(aligned_pairs)}")
    
    is_valid, error_msg = validate_input(islands, aligned_pairs)
    if not is_valid:
        print(f"\nInvalid input: {error_msg}")
        return {
            "input_file": input_path,
            "error": error_msg,
            "valid": False
        }
    
    var_map = create_logic_vars(islands, aligned_pairs)
    cnf_clauses = []
    cnf_clauses += generate_cnf_total_bridges(var_map, islands)
    cnf_clauses += generate_cnf_double_bridges(var_map)
    cnf_clauses += generate_cnf_no_cross(var_map, aligned_pairs)
    
    results = {
        "input_file": input_path,
        "grid_size": f"{len(grid)}x{len(grid[0])}",
        "islands": len(islands),
        "solvers": {}
    }
    
    if solver_type in ["all", "pysat"]:
        output, time_taken, success = solve_with_pysat(cnf_clauses, var_map, islands, grid)
        results["solvers"]["pysat"] = {"success": success, "time": time_taken}
        if success and output is not None:
            output_path = os.path.join(output_dir, f"pysat_{os.path.basename(input_path)}")
            write_grid_to_file(output, output_path)
            if verbose: 
                print("\n[PySAT Result Grid]:")
                print_grid(output)
    
    if solver_type in ["all", "astar"]:
        output, time_taken, success = solve_with_astar(
            cnf_clauses, var_map, islands, grid, timeout=TIMEOUT_CONFIG["astar"]
        )
        results["solvers"]["astar"] = {"success": success, "time": time_taken}
        if success and output is not None:
            output_path = os.path.join(output_dir, f"astar_{os.path.basename(input_path)}")
            write_grid_to_file(output, output_path)
            if verbose:
                print("\n[A* Result Grid]:")
                print_grid(output)
    
    if solver_type in ["all", "backtracking"]:
        output, time_taken, success = solve_with_backtracking(
            cnf_clauses, var_map, islands, grid, timeout=TIMEOUT_CONFIG["backtracking"]
        )
        results["solvers"]["backtracking"] = {"success": success, "time": time_taken}
        if success and output is not None:
            output_path = os.path.join(output_dir, f"backtrack_{os.path.basename(input_path)}")
            write_grid_to_file(output, output_path)
            if verbose:
                print("\n[Backtracking Result Grid]:")
                print_grid(output)
    
    if solver_type in ["all", "bruteforce"]:
        if len(grid) <= 7 or solver_type == "bruteforce":
            output, time_taken, success = solve_with_bruteforce(
                grid, islands, timeout=TIMEOUT_CONFIG["bruteforce"]
            )
            results["solvers"]["bruteforce"] = {"success": success, "time": time_taken}
            if success and output is not None:
                output_path = os.path.join(output_dir, f"brute_{os.path.basename(input_path)}")
                write_grid_to_file(output, output_path)
                if verbose:
                    print("\n[BruteForce Result Grid]:")
                    print_grid(output)
        else:
            print_separator("BRUTE FORCE")
            print(f"Skipped - Grid {len(grid)}x{len(grid[0])} too large (>7x7)")
            results["solvers"]["bruteforce"] = {"success": False, "time": 0, "note": "Skipped (Too Large)"}
    
    return results


def solve_all_files(solver_type, input_dir="Inputs", output_dir="Outputs"):
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    input_files = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".txt"):
                input_files.append(os.path.join(root, file))
    input_files.sort()
    
    if not input_files:
        print(f"No input files found in '{input_dir}'!")
        return []
    
    print(f"\nFound {len(input_files)} input file(s) in '{input_dir}'")
    
    all_results = []
    for idx, input_path in enumerate(input_files, 1):
        try:
            results = process_input_file(input_path, output_dir, solver_type, verbose=False)
            all_results.append(results)
        except Exception as e:
            print(f"Error processing {input_path}: {e}")
            import traceback
            traceback.print_exc()

    summary_filename = f"summary_{solver_type}.json"
    summary_path = os.path.join(output_dir, summary_filename)
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2)
    
    print_separator("PERFORMANCE COMPARISON")
    print(f"{'File':<25} {'Solver':<15} {'Time (s)':<10} {'Status'}")
    print("-" * 70)
    
    for result in all_results:
        filename = os.path.basename(result["input_file"])
        
        if "error" in result and "solvers" not in result:
             print(f"{filename:<25} {'INVALID':<15} {'N/A':<10} ({result.get('error','Unknown')})")
             continue

        if "solvers" in result:
            for solver_name, solver_result in result["solvers"].items():
                status = "Unknown"
                time_str = "N/A"

                if solver_result.get("note"):
                    status = "Skip"
                elif solver_result.get("success"):
                    status = "Success"
                else:
                    status = "Fail/Timeout" 

                time_val = solver_result.get('time', 0)
                time_str = f"{time_val:.4f}"
                
                print(f"{filename:<25} {solver_name:<15} {time_str:<10} {status}")

    return all_results


def show_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("HASHIWOKAKERO SOLVER - MENU")
    print("1. PySAT Solver")
    print("2. A* Solver")
    print("3. Backtracking Solver")
    print("4. Brute Force Solver")
    print("5. COMPARE ALL (Run everything)")
    print("6. Solve Single File")
    print("7. Validate Inputs")
    print("8. Visualize outputs")
    print("0. Exit")


def main():
    INPUT_DIR = "Inputs"
    OUTPUT_DIR = "Outputs"
    
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    solver_map = {"1": "pysat", "2": "astar", "3": "backtracking", "4": "bruteforce", "5": "all"}
    
    while True:
        show_menu()
        choice = input("\nSelect option: ").strip()
        
        if choice == "0":
            print("\nExit!"); break
            
        elif choice in solver_map:
            solver_type = solver_map[choice]
            solve_all_files(solver_type, INPUT_DIR, OUTPUT_DIR)
            input("\nPress Enter to continue...")
            
        elif choice == "6":
            files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".txt")]
            files.sort()
            if not files:
                print(f"No files in {INPUT_DIR}"); input(); continue
                
            print("\nFiles:")
            for i, f in enumerate(files, 1): print(f"{i}. {f}")
            
            try:
                idx = int(input("Select file: ")) - 1
                if 0 <= idx < len(files):
                    path = os.path.join(INPUT_DIR, files[idx])
                    print("1.PySAT 2.A* 3.Backtrack 4.Brute 5.All")
                    sol_c = input("Solver: ").strip() or "1"
                    s_type = solver_map.get(sol_c, "pysat")
                    process_input_file(path, OUTPUT_DIR, s_type, verbose=True)
            except: pass
            input("\nPress Enter to continue...")

        elif choice == "7":
            from helper_02 import validate_input
            files = [os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR) if f.endswith(".txt")]
            files.sort()
            print_separator("VALIDATING")
            for path in files:
                try:
                    g, isl = read_input(path)
                    isl = identify_island(g)
                    aligned = find_aligned_pairs(isl)
                    valid, msg = validate_input(isl, aligned)
                    status = "VALID" if valid else f"INVALID ({msg})"
                    print(f"{os.path.basename(path):<20} {status}")
                except: print(f"{os.path.basename(path):<20} ERROR")
            input("\nPress Enter to continue...")
        elif choice == "8":
            process_all_files() #Visualize các file trong outputs

if __name__ == "__main__":
    main()