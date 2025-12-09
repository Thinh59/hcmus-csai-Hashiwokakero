import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
import ast

def draw_hashi(grid_data, save_path, draw_bridges=True):
    rows = len(grid_data)
    cols = len(grid_data[0])

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.invert_yaxis()
    ax.set_aspect('equal')
    ax.axis('off')

    ISLAND_RADIUS = 0.4
    BRIDGE_COLOR = '#4F81BD'
    BRIDGE_WIDTH = 4
    DOUBLE_BRIDGE_OFFSET = 0.15

    for r in range(rows):
        for c in range(cols):
            cell = str(grid_data[r][c])
            x, y = c, r

            if draw_bridges:
                if cell in ['-', '=']: 
                    x_start, x_end = x - 0.55, x + 0.55
                    if cell == '-':
                        ax.plot([x_start, x_end], [y, y], color=BRIDGE_COLOR, linewidth=BRIDGE_WIDTH, zorder=5)
                    elif cell == '=':
                        ax.plot([x_start, x_end], [y - DOUBLE_BRIDGE_OFFSET, y - DOUBLE_BRIDGE_OFFSET], color=BRIDGE_COLOR, linewidth=BRIDGE_WIDTH, zorder=5)
                        ax.plot([x_start, x_end], [y + DOUBLE_BRIDGE_OFFSET, y + DOUBLE_BRIDGE_OFFSET], color=BRIDGE_COLOR, linewidth=BRIDGE_WIDTH, zorder=5)
                elif cell in ['|', '#', '"', 'H']: 
                    y_start, y_end = y - 0.55, y + 0.55
                    if cell == '|':
                        ax.plot([x, x], [y_start, y_end], color=BRIDGE_COLOR, linewidth=BRIDGE_WIDTH, zorder=5)
                    else:
                        ax.plot([x - DOUBLE_BRIDGE_OFFSET, x - DOUBLE_BRIDGE_OFFSET], [y_start, y_end], color=BRIDGE_COLOR, linewidth=BRIDGE_WIDTH, zorder=5)
                        ax.plot([x + DOUBLE_BRIDGE_OFFSET, x + DOUBLE_BRIDGE_OFFSET], [y_start, y_end], color=BRIDGE_COLOR, linewidth=BRIDGE_WIDTH, zorder=5)

            if cell.isdigit() and cell != "0":
                circle = patches.Circle((x, y), ISLAND_RADIUS, edgecolor='black', facecolor='white', linewidth=1.5, zorder=10)
                ax.add_patch(circle)
                ax.text(x, y, cell, ha='center', va='center', fontsize=14, fontfamily='sans-serif', fontweight='normal', zorder=11)

    ax.set_xticks([x - 0.5 for x in range(cols + 1)])
    ax.set_yticks([y - 0.5 for y in range(rows + 1)])
    ax.grid(True, color='lightgray', linestyle='-', linewidth=1)
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

    plt.tight_layout()
    plt.savefig(save_path, dpi=100, bbox_inches='tight')
    plt.close(fig)

def process_all_files():
    input_folder = 'Outputs'
    output_folder = 'visualize'

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    if not os.path.exists(input_folder):
        print(f"Lỗi: Không tìm thấy thư mục '{input_folder}'")
        return

    files = os.listdir(input_folder)
    print(f"Tìm thấy {len(files)} files...")

    for filename in files:
        file_path = os.path.join(input_folder, filename)
        if os.path.isdir(file_path): continue

        try:
            grid_data = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line: 
                        try:
                            row_data = ast.literal_eval(line)
                            grid_data.append(row_data)
                        except:
                            pass 

            if not grid_data:
                print(f"File {filename} rỗng hoặc định dạng sai hoàn toàn.")
                continue

            base_name = os.path.splitext(filename)[0]
            
            output_img_path = os.path.join(output_folder, f"{base_name}.png")
            draw_hashi(grid_data, output_img_path, draw_bridges=True)

            print(f"Đã xử lý: {filename}")

        except Exception as e:
            print(f"Lỗi khi xử lý file {filename}: {e}")

if __name__ == "__main__":
    process_all_files()