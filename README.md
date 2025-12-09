
PROJECT 02: HASHIWOKAKERO SOLVER (LOGIC)
Course: CSC14003 - Introduction to Artificial Intelligence
------------------------------------------------------------------------

1. TEAM MEMBERS


[23122009] - [Bàng Mỹ Linh]
[23122018] - [Lại Nguyễn Hồng Thanh]
[23122019] - [Phan Huỳnh Châu Thịnh]
[23122029] - [Nguyễn Trọng Hòa]

------------------------------------------------------------------------
2. SYSTEM REQUIREMENTS

- Python Version: 3.7 or higher
- Operating System: Windows, macOS, or Linux
- Required Libraries:
    + numpy
    + python-sat

------------------------------------------------------------------------
3. INSTALLATION
Step 1: Open a terminal/command prompt.
Step 2: Navigate to the 'Source' directory.
Step 3: Install the required dependencies using pip:

    pip install -r requirements.txt

    (Or install manually: pip install numpy python-sat)

------------------------------------------------------------------------
4. DIRECTORY STRUCTURE
```text
Source/
  ├── Inputs/               # Contains input test cases (.txt)
  ├── Outputs/              # Stores generated result grids and summary logs
  ├── visualize/            # Stores generated visualize outputs 
  ├── helper_01.py          # Reads input and parses island data
  ├── helper_02.py          # Generates CNF clauses (constraints)
  ├── solver_pySAT.py       # PySAT solver wrapper
  ├── solver_astar.py       # A* Search algorithm implementation
  ├── solver_backtracking.py# Backtracking algorithm implementation
  ├── solver_brute_force.py # Brute-force algorithm implementation
  ├── utils.py              # Utility functions (print grid, validate, etc.)
  ├── visualize.py          # Visualize outputs 
  ├── main.py               # Main entry point (Menu & Driver code)
  ├── requirements.txt      # List of dependencies
  └── README.txt            # This file
```


------------------------------------------------------------------------
5. HOW TO RUN
Step 1: Navigate to the 'Source' folder in your terminal.
Step 2: Run the main program:

    python main.py

Step 3: A menu will appear with the following options:

    [1] PySAT Solver:        Solves all files in 'Inputs' using the PySAT library.
    [2] A* Solver:           Solves all files using A* Search (Heuristic: Unsatisfied clauses).
    [3] Backtracking Solver: Solves all files using Optimized Backtracking (MCV & Unit Propagation).
    [4] Brute Force Solver:  Solves small files using Brute-force (only grids <= 7x7).
    [5] COMPARE ALL:         Runs ALL algorithms sequentially on all inputs to generate a performance report.
    [6] Solve Single File:   Select a specific input file and a specific algorithm to view the result grid immediately.
    [7] Validate Inputs:     Checks if input files are valid logic puzzles.
    [8] Visualize Outputs
    [0] Exit

Note:
- Results are saved in the 'Outputs' folder.
- Visualize results are saved in the "visualize" folder
- A summary JSON file is generated after running batch options (1-5).
- Timeout is set to 30 seconds per file by default (configurable in main.py).

------------------------------------------------------------------------
6. ALGORITHMS & IMPLEMENTATION NOTES
- PySAT: Uses Glucose3 solver. Extremely fast and efficient.
- A* Search: Uses 'Number of unsatisfied clauses' as heuristic. 
- Backtracking: Enhanced with Unit Propagation and Most Constrained Variable (MCV) heuristic for pruning.
- Brute-force: Exhaustive search. Note that it will TIMEOUT on complex grids (e.g., 7x7 dense or larger) due to combinatorial explosion (O(3^E)).

------------------------------------------------------------------------
7. INPUT/OUTPUT FORMAT
Input (.txt):
- 0 represents an empty cell.
- Numbers (1-8) represent islands.
- Comma-separated values.

Output:
- Visual grid representation.
- '-' / '=' : Horizontal bridges (single/double).
- '|' / '"' : Vertical bridges (single/double).
