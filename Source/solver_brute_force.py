# solver_brute_force.py
import itertools
import time
import numpy as np
from typing import List, Tuple, Dict, Optional
from helper_01 import find_aligned_pairs
from utils import is_connected, cross_check

class BruteForceSolver:
    def __init__(self, grid: np.ndarray, islands: List[Tuple[int, int, int]]):
        self.grid = np.array(grid)
        self.islands = islands
        
        self.island_map = {(r, c): i for i, (r, c, val) in enumerate(islands)}

        raw_pairs = find_aligned_pairs(islands)

        self.edges = []
        for r1, c1, r2, c2, orient in raw_pairs:
            idx1 = self.island_map[(r1, c1)]
            idx2 = self.island_map[(r2, c2)]
            self.edges.append((idx1, idx2)) 

        self.configs_checked = 0

    def solve(self, timeout: int = 60) -> Optional[Dict[Tuple[int, int], int]]:
        num_edges = len(self.edges)
        
        print(f"\n Brute Force Solver")
        print(f"   Grid: {self.grid.shape[0]}x{self.grid.shape[1]}")
        print(f"   Islands: {len(self.islands)}")
        print(f"   Potential Edges: {num_edges}")
        
        search_space = 3 ** num_edges
        print(f"Search space: 3^{num_edges} = {search_space:,}")
        
        if search_space > 5_000_000:
            print("Warning: Search space is huge. This will likely timeout.")

        start_time = time.time()

        for config in itertools.product([0, 1, 2], repeat=num_edges):
            self.configs_checked += 1

            if self.configs_checked % 1000 == 0:
                if time.time() - start_time > timeout:
                    return None

            if not self._check_degrees(config):
                continue

            sol = self._make_solution(config)

            if not self._check_no_cross(sol):
                continue

            if is_connected(self.islands, sol):
                return sol

        return None

    def _make_solution(self, config):
        sol = {}
        for k, count in enumerate(config):
            if count > 0:
                u, v = self.edges[k]
                sol[(u, v)] = count
        return sol

    def _check_degrees(self, config):
        """Kiểm tra nhanh tổng số cầu mỗi đảo"""
        current_degrees = [0] * len(self.islands)
        
        for k, count in enumerate(config):
            if count > 0:
                u, v = self.edges[k]
                current_degrees[u] += count
                current_degrees[v] += count

        for i, degree in enumerate(current_degrees):
            if degree != self.islands[i][2]:
                return False
        return True

    def _check_no_cross(self, sol):
        active_edges = []
        for (u, v), count in sol.items():
            if count > 0:
                p1 = (self.islands[u][0], self.islands[u][1])
                p2 = (self.islands[v][0], self.islands[v][1])
                active_edges.append((p1, p2))
        
        n = len(active_edges)
        for i in range(n):
            for j in range(i + 1, n):
                if cross_check(active_edges[i], active_edges[j]):
                    return False
        return True

def solve_brute_force(grid, islands, timeout=60):
    solver = BruteForceSolver(grid, islands)
    return solver.solve(timeout)