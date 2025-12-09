import numpy as np
from typing import List, Tuple, Dict, Set
from collections import deque


def print_grid(grid: np.ndarray) -> None:
    if isinstance(grid, np.ndarray):
        grid = grid.tolist()
    
    for row in grid:
        print('[', end='')
        for i, cell in enumerate(row):
            if i > 0:
                print(', ', end='')
            print(f'"{cell}"', end='')
        print(']')


def write_grid_to_file(grid: np.ndarray, file_path: str) -> None:
    try:
        # Use UTF-8 encoding to support special Unicode characters
        with open(file_path, 'w', encoding='utf-8') as f:
            if isinstance(grid, np.ndarray):
                grid = grid.tolist()
            
            for row in grid:
                f.write('[')
                for i, cell in enumerate(row):
                    if i > 0:
                        f.write(', ')
                    f.write(f'"{cell}"')
                f.write(']\n')
        
        print(f"Output written to: {file_path}")
    except Exception as e:
        print(f"Error writing to {file_path}: {e}")
        # Try fallback with ASCII-safe characters
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if isinstance(grid, np.ndarray):
                    grid = grid.tolist()
                
                for row in grid:
                    f.write('[')
                    for i, cell in enumerate(row):
                        if i > 0:
                            f.write(', ')
                        # Convert special characters to ASCII
                        cell_str = str(cell)
                        cell_str = cell_str.replace('−', '-')  # Unicode minus to ASCII hyphen
                        cell_str = cell_str.replace('∣', '|')  # Unicode vertical line to ASCII pipe
                        cell_str = cell_str.replace('$', 'II') # Double vertical to II
                        f.write(f'"{cell_str}"')
                    f.write(']\n')
            print(f"Output written with ASCII fallback to: {file_path}")
        except Exception as e2:
            print(f"Failed to write even with fallback: {e2}")


def cross_check(bridge1: Tuple[Tuple[int, int], Tuple[int, int]], 
                bridge2: Tuple[Tuple[int, int], Tuple[int, int]]) -> bool:
    (r1, c1), (r2, c2) = bridge1
    (r3, c3), (r4, c4) = bridge2
    
    # Check if one is horizontal and other is vertical
    bridge1_horizontal = (r1 == r2)
    bridge2_horizontal = (r3 == r4)
    
    if bridge1_horizontal == bridge2_horizontal:
        # Both horizontal or both vertical - they don't cross
        return False
    
    if bridge1_horizontal:
        # bridge1 is horizontal, bridge2 is vertical
        h_min_c, h_max_c = min(c1, c2), max(c1, c2)
        v_min_r, v_max_r = min(r3, r4), max(r3, r4)
        
        return (h_min_c < c3 < h_max_c) and (v_min_r < r1 < v_max_r)
    else:
        # bridge1 is vertical, bridge2 is horizontal
        v_min_r, v_max_r = min(r1, r2), max(r1, r2)
        h_min_c, h_max_c = min(c3, c4), max(c3, c4)
        
        return (h_min_c < c1 < h_max_c) and (v_min_r < r3 < v_max_r)


def is_connected(islands: List[Tuple[int, int, int]], 
                 connections: Dict[Tuple[int, int], int]) -> bool:

    if not islands:
        return True
    
    n = len(islands)

    adj = {i: [] for i in range(n)}
    
    for (i, j), num_bridges in connections.items():
        if num_bridges > 0:
            adj[i].append(j)
            adj[j].append(i)
    
    # BFS from island 0
    visited = set()
    queue = deque([0])
    visited.add(0)
    
    while queue:
        current = queue.popleft()
        for neighbor in adj[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return len(visited) == n


def build_output_grid(grid_shape: Tuple[int, int],
                     islands: List[Tuple[int, int, int]], 
                     connections: Dict[Tuple[int, int], int]) -> np.ndarray:
    rows, cols = grid_shape
    output = np.full((rows, cols), "0", dtype=object)
    
    for (idx1, idx2), num_bridges in connections.items():
        if num_bridges == 0:
            continue
        
        r1, c1, _ = islands[idx1]
        r2, c2, _ = islands[idx2]
        
        if r1 == r2:  
            symbol = "=" if num_bridges == 2 else "-"
            min_c, max_c = min(c1, c2), max(c1, c2)
            for c in range(min_c + 1, max_c):
                output[r1, c] = symbol
        else:  
            symbol = "$" if num_bridges == 2 else "|"
            min_r, max_r = min(r1, r2), max(r1, r2)
            for r in range(min_r + 1, max_r):
                output[r, c1] = symbol

    for r, c, value in islands:
        output[r, c] = str(value)
    
    return output


def compute_current_bridges(connections: Dict[Tuple[int, int], int]) -> int:
    return sum(connections.values())


def validate_solution(grid_shape: Tuple[int, int],
                     islands: List[Tuple[int, int, int]],
                     connections: Dict[Tuple[int, int], int]) -> Tuple[bool, str]:

    bridge_count = {i: 0 for i in range(len(islands))}
    for (i, j), num in connections.items():
        bridge_count[i] += num
        bridge_count[j] += num
    
    for i, (r, c, required) in enumerate(islands):
        if bridge_count[i] != required:
            return False, f"Island at ({r},{c}) has {bridge_count[i]} bridges, needs {required}"

    if not is_connected(islands, connections):
        return False, "Islands are not all connected"

    for (i, j), num in connections.items():
        if num > 2:
            return False, f"More than 2 bridges between islands {i} and {j}"
    
    edges = []
    for (i, j), num in connections.items():
        if num > 0:
            r1, c1, _ = islands[i]
            r2, c2, _ = islands[j]
            edges.append(((r1, c1), (r2, c2)))
    
    for a in range(len(edges)):
        for b in range(a + 1, len(edges)):
            if cross_check(edges[a], edges[b]):
                return False, f"Bridges cross: {edges[a]} and {edges[b]}"
    
    return True, "Solution is valid"


def print_solution_summary(islands: List[Tuple[int, int, int]],
                          connections: Dict[Tuple[int, int], int]) -> None:
    """
    Print a summary of the solution.
    """
    print("\n" + "="*60)
    print("SOLUTION SUMMARY")
    print("="*60)
    
    total_bridges = compute_current_bridges(connections)
    print(f"Total bridges: {total_bridges}")
    print(f"Total connections: {len([c for c in connections.values() if c > 0])}")
    
    print("\nBridge details:")
    for (i, j), num in sorted(connections.items()):
        if num > 0:
            r1, c1, _ = islands[i]
            r2, c2, _ = islands[j]
            direction = "Horizontal" if r1 == r2 else "Vertical"
            bridges = "Double" if num == 2 else "Single"
            print(f"  ({r1},{c1}) <-> ({r2},{c2}): {bridges} {direction}")


# Test utilities
if __name__ == "__main__":
    print("Testing utility functions...")
    
    bridge1 = ((1, 1), (1, 5))  
    bridge2 = ((0, 3), (4, 3)) 
    print(f"Bridges cross: {cross_check(bridge1, bridge2)}")

    test_islands = [(0, 0, 2), (0, 2, 2), (2, 0, 2), (2, 2, 2)]
    test_connections = {(0, 1): 1, (1, 3): 1, (0, 2): 1}
    print(f"Islands connected: {is_connected(test_islands, test_connections)}")
    
    test_grid = build_output_grid((5, 5), test_islands, test_connections)
    print("\nTest grid:")
    print_grid(test_grid)