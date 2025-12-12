def read_input(file_path):
    grid = []
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = [int(x.strip()) for x in line.split(",")]
            grid.append(row)

    islands = identify_island(grid)
    # for r in range(len(grid)):
    #     for c in range(len(grid[0])):
    #         if grid[r][c] != 0:
    #             islands.append((r, c, grid[r][c]))

    return grid, islands


def identify_island(grid):
    islands = []
    rows, cols = len(grid), len(grid[0])

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0:
                islands.append((r, c, grid[r][c]))

    return islands


def find_aligned_pairs(islands):
    aligned = []
    n = len(islands)

    for i in range(n):
        r1, c1, _ = islands[i]
        for j in range(i + 1, n):
            r2, c2, _ = islands[j]

            if r1 == r2:
                between = []
                for k in range(n):
                    if k == i or k == j:
                        continue
                    rk, ck, _ = islands[k]
                    if rk == r1 and min(c1, c2) < ck < max(c1, c2):
                        between.append(k)

                if len(between) == 0:
                    aligned.append((r1, c1, r2, c2, "H"))

            elif c1 == c2:
                between = []
                for k in range(n):
                    if k == i or k == j:
                        continue
                    rk, ck, _ = islands[k]
                    if ck == c1 and min(r1, r2) < rk < max(r1, r2):
                        between.append(k)

                if len(between) == 0:
                    aligned.append((r1, c1, r2, c2, "V"))

    return aligned


def create_logic_vars(islands, aligned_pairs):
    var_map = {}
    var_counter = 1

    for (r1, c1, r2, c2, orientation) in aligned_pairs:
        # Store edge without orientation for var_map key
        edge_key = (r1, c1, r2, c2)
        var_map[edge_key] = (var_counter, var_counter + 1)
        var_counter += 2

    return var_map


def print_input_info(grid, islands, aligned_pairs):
    print("INPUT PUZZLE INFORMATION")
    print(f"Grid Size: {len(grid)}x{len(grid[0])}")
    print(f"Number of Islands: {len(islands)}")
    print(f"Possible Connections: {len(aligned_pairs)}")
    
    print("\nIslands:")
    for r, c, val in islands:
        print(f"  ({r},{c}): {val}")
    
    print("\nPossible Connections:")
    for r1, c1, r2, c2, orientation in aligned_pairs:
        direction = "Horizontal" if orientation == "H" else "Vertical"
        print(f"  ({r1},{c1}) <-> ({r2},{c2}) [{direction}]")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        grid, islands = read_input(file_path)
        islands = identify_island(grid)
        aligned_pairs = find_aligned_pairs(islands)
        
        print_input_info(grid, islands, aligned_pairs)
        
        # Create variables
        var_map = create_logic_vars(islands, aligned_pairs)
        print(f"\nTotal Variables: {len(var_map) * 2}")
    else:
        print("Usage: python input_reader.py <input_file.txt>")