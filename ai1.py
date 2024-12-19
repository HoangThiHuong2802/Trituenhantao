import tkinter as tk
import heapq
import random
from tkinter import messagebox
import time

# Định nghĩa các hướng di chuyển (trái, phải, lên, xuống)
directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Các hướng di chuyển trong mê cung (trái, phải, lên, xuống)

# Hàm tính khoảng cách Manhattan
def manhattan_distance(start, end):
    return abs(start[0] - end[0]) + abs(start[1] - end[1])

# Thuật toán A*
def astar(maze, start, end):
    rows, cols = len(maze), len(maze[0])
    open_list = []
    closed_list = set()
    
    came_from = {}
    
    g_score = {start: 0}
    f_score = {start: manhattan_distance(start, end)}
    
    heapq.heappush(open_list, (f_score[start], start))
    
    while open_list:
        _, current = heapq.heappop(open_list)
        
        if current == end:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]
        
        closed_list.add(current)
        
        for direction in directions:
            neighbor = (current[0] + direction[0], current[1] + direction[1])
            
            if 0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols and maze[neighbor[0]][neighbor[1]] != 1:
                if neighbor in closed_list:
                    continue
                
                tentative_g_score = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + manhattan_distance(neighbor, end)
                    heapq.heappush(open_list, (f_score[neighbor], neighbor))
    
    return None  # Nếu không có đường đi

# Hàm tạo giao diện
class MazeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Giải Mê Cung A*")

        self.rows = 10
        self.cols = 10
        self.cell_size = 40
        self.canvas = tk.Canvas(root, width=self.cols * self.cell_size, height=self.rows * self.cell_size, bg="#f0f0f0")
        self.canvas.pack(padx=20, pady=20)

        self.maze = [[0 for _ in range(self.cols)] for _ in range(self.rows)]  # 0: Trống, 1: Tường
        self.start = None
        self.end = None
        self.path = []
        self.steps = 0
        self.time_taken = 0
        self.current_position = None  # Để lưu vị trí người chơi
        self.create_controls()

        self.canvas.bind("<Button-1>", self.on_click)
        self.root.bind("<Key>", self.on_key_press)  # Bắt sự kiện bàn phím

    def create_controls(self):
        """Tạo các điều khiển và giao diện đẹp hơn"""
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        self.solve_button = tk.Button(control_frame, text="Giải Mê Cung", command=self.solve_maze, width=20, height=2, bg="#4CAF50", fg="white", font=("Arial", 12))
        self.solve_button.grid(row=0, column=0, padx=10)

        self.reset_button = tk.Button(control_frame, text="Reset", command=self.reset_game, width=20, height=2, bg="#2196F3", fg="white", font=("Arial", 12))
        self.reset_button.grid(row=0, column=1, padx=10)

        self.random_button = tk.Button(control_frame, text="Tạo Mê Cung Ngẫu Nhiên", command=self.generate_random_maze, width=20, height=2, bg="#FF9800", fg="white", font=("Arial", 12))
        self.random_button.grid(row=0, column=2, padx=10)

        self.time_label = tk.Label(control_frame, text="Thời gian: 0s", font=("Arial", 12))
        self.time_label.grid(row=1, column=0, columnspan=3, pady=5)

        self.steps_label = tk.Label(control_frame, text="Số bước: 0", font=("Arial", 12))
        self.steps_label.grid(row=2, column=0, columnspan=3)

        self.help_button = tk.Button(control_frame, text="Hướng Dẫn", command=self.show_help, width=20, height=2, bg="#00BCD4", fg="white", font=("Arial", 12))
        self.help_button.grid(row=3, column=0, columnspan=3, pady=5)

    def draw_grid(self):
        """Vẽ lưới mê cung với hiệu ứng đẹp hơn"""
        self.canvas.delete("all")
        for i in range(self.rows):
            for j in range(self.cols):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="white", width=2, tags=f"{i},{j}")
                
                if self.maze[i][j] == 1:
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="gray", width=2)
                
                if (i, j) == self.start:
                    self.canvas.create_oval(x1 + 10, y1 + 10, x2 - 10, y2 - 10, outline="green", width=3)
                elif (i, j) == self.end:
                    self.canvas.create_oval(x1 + 10, y1 + 10, x2 - 10, y2 - 10, outline="red", width=3)

        # Vẽ người chơi (chú ý là hình tròn màu xanh dương)
        if self.current_position:
            x1 = self.current_position[1] * self.cell_size + self.cell_size // 4
            y1 = self.current_position[0] * self.cell_size + self.cell_size // 4
            x2 = x1 + self.cell_size // 2
            y2 = y1 + self.cell_size // 2
            self.canvas.create_oval(x1, y1, x2, y2, outline="blue", width=3)

    def on_click(self, event):
        """Xử lý nhấp chuột để thiết lập điểm bắt đầu, điểm kết thúc và tường"""
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        if self.start is None:
            self.start = (row, col)
        elif self.end is None:
            self.end = (row, col)
        else:
            if self.maze[row][col] == 0:
                self.maze[row][col] = 1
            else:
                self.maze[row][col] = 0
        self.draw_grid()

    def on_key_press(self, event):
        """Xử lý các phím điều hướng của người chơi"""
        if self.current_position is None:
            self.current_position = self.start  # Bắt đầu từ điểm khởi đầu

        row, col = self.current_position
        if event.keysym == "Up":
            new_pos = (row - 1, col)
        elif event.keysym == "Down":
            new_pos = (row + 1, col)
        elif event.keysym == "Left":
            new_pos = (row, col - 1)
        elif event.keysym == "Right":
            new_pos = (row, col + 1)
        elif event.keysym == "w":  # W
            new_pos = (row - 1, col)
        elif event.keysym == "s":  # S
            new_pos = (row + 1, col)
        elif event.keysym == "a":  # A
            new_pos = (row, col - 1)
        elif event.keysym == "d":  # D
            new_pos = (row, col + 1)
        else:
            return  # Nếu phím không hợp lệ, không làm gì

        # Kiểm tra xem người chơi có di chuyển ra ngoài mê cung hay không và có chạm vào tường không
        if 0 <= new_pos[0] < self.rows and 0 <= new_pos[1] < self.cols and self.maze[new_pos[0]][new_pos[1]] == 0:
            self.current_position = new_pos
            self.draw_grid()

            # Kiểm tra nếu người chơi đến đích
            if self.current_position == self.end:
                messagebox.showinfo("Kết quả", "Chúc mừng! Bạn đã đến đích!")
                self.reset_game()

    def solve_maze(self):
        """Giải mê cung và vẽ đường đi"""
        if self.start is None or self.end is None:
            return
        
        start_time = time.time()
        self.path = astar(self.maze, self.start, self.end)
        end_time = time.time()
        
        self.time_taken = round(end_time - start_time, 2)
        self.time_label.config(text=f"Thời gian: {self.time_taken}s")

        if self.path:
            # Cập nhật số bước và thông báo
            self.steps = len(self.path)
            self.steps_label.config(text=f"Số bước: {self.steps}")
            messagebox.showinfo("Kết quả", f"Đã tìm thấy đường đi trong {self.steps} bước!")
            
            # Hiệu ứng chuyển động mượt mà
            for i, (row, col) in enumerate(self.path):
                x1 = col * self.cell_size + self.cell_size // 4
                y1 = row * self.cell_size + self.cell_size // 4
                x2 = x1 + self.cell_size // 2
                y2 = y1 + self.cell_size // 2
                color = "yellow" if i != 0 and i != len(self.path)-1 else "blue"
                self.canvas.create_oval(x1, y1, x2, y2, outline=color, width=3)
                self.canvas.update()
                time.sleep(0.1)
        else:
            messagebox.showerror("Kết quả", "Không tìm thấy đường đi!")

    def reset_game(self):
        """Reset mê cung và các điểm"""
        self.maze = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.start = None
        self.end = None
        self.path = []
        self.steps = 0
        self.time_taken = 0
        self.current_position = None  # Đặt lại vị trí người chơi
        self.steps_label.config(text="Số bước: 0")
        self.time_label.config(text="Thời gian: 0s")
        self.draw_grid()

    def generate_random_maze(self):
        """Tạo mê cung ngẫu nhiên với các tường"""
        self.maze = [[random.choice([0, 1]) for _ in range(self.cols)] for _ in range(self.rows)]
        self.start = None
        self.end = None
        self.path = []
        self.steps = 0
        self.time_taken = 0
        self.steps_label.config(text="Số bước: 0")
        self.time_label.config(text="Thời gian: 0s")
        self.draw_grid()

    def show_help(self):
        """Hiển thị hướng dẫn chơi"""
        messagebox.showinfo("Hướng Dẫn", "Click vào lưới để thiết lập điểm bắt đầu, kết thúc và tường.\n"
                                         "Sử dụng các phím mũi tên hoặc WASD để di chuyển người chơi trong mê cung.\n"
                                         "Điểm bắt đầu là ô xanh, điểm kết thúc là ô đỏ, người chơi là ô xanh dương.")

# Khởi tạo ứng dụng
root = tk.Tk()
game = MazeGame(root)
root.mainloop()
