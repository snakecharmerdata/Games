import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import random
import copy
import os

# Sudoku puzzle generator and solver
class Sudoku:
    def __init__(self, level='Easy'):
        self.level = level
        self.board = self.generate_puzzle(level)
        self.solution = copy.deepcopy(self.board)
        self.solve(self.solution)

    def generate_full_board(self):
        board = [[0]*9 for _ in range(9)]
        self.solve(board, randomize=True)
        return board

    def generate_puzzle(self, level):
        board = self.generate_full_board()
        if level == 'Easy':
            removals = 35
        elif level == 'Medium':
            removals = 45
        else:
            removals = 55
        positions = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(positions)
        for _ in range(removals):
            i, j = positions.pop()
            board[i][j] = 0
        return board

    def find_empty(self, board):
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    return i, j
        return None

    def valid(self, board, num, pos):
        row, col = pos
        for i in range(9):
            if board[row][i] == num and i != col:
                return False
        for i in range(9):
            if board[i][col] == num and i != row:
                return False
        box_x = col // 3
        box_y = row // 3
        for i in range(box_y*3, box_y*3 + 3):
            for j in range(box_x*3, box_x*3 + 3):
                if board[i][j] == num and (i, j) != pos:
                    return False
        return True

    def solve(self, board, randomize=False):
        empty = self.find_empty(board)
        if not empty:
            return True
        row, col = empty
        nums = list(range(1, 10))
        if randomize:
            random.shuffle(nums)
        for num in nums:
            if self.valid(board, num, (row, col)):
                board[row][col] = num
                if self.solve(board, randomize):
                    return True
                board[row][col] = 0
        return False

class SudokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title('Sudoku Game')
        self.bg_image = None
        self.bg_path = None
        self.sudoku = Sudoku('Easy')
        self.level_var = tk.StringVar(value='Easy')
        self.entries = [[None for _ in range(9)] for _ in range(9)]
        self.bg_files = self.get_jpg_files()
        self.bg_dropdown_var = tk.StringVar()
        if self.bg_files:
            self.bg_path = self.bg_files[0][0]
            self.bg_dropdown_var.set(self.bg_files[0][1])
        self.create_layout()
        self.draw_board()

    def get_jpg_files(self):
        name_map = {
            'pic3.jpg': 'Alien World',
            'pic2.jpg': 'Aquarium',
            'pic.jpg': 'Forest',
        }
        files = []
        for f in os.listdir('.'):
            if f.lower().endswith('.jpg'):
                display_name = name_map.get(f, f)
                files.append((os.path.abspath(f), display_name))
        return files

    def create_layout(self):
        self.main_frame = tk.Frame(self.root, bg='#f0f0f0')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.left_pane = tk.Frame(self.main_frame, width=200, bg='#f0f0f0')
        self.left_pane.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=20)
        tk.Label(self.left_pane, text='Sudoku', font=('Helvetica Neue', 22, 'bold'), bg='#f0f0f0').pack(pady=(0,20))
        tk.Label(self.left_pane, text='Difficulty:', font=('Arial', 13), bg='#f0f0f0').pack(pady=(0,5))
        level_menu = ttk.Combobox(self.left_pane, textvariable=self.level_var, values=['Easy', 'Medium', 'Challenging'], state='readonly', width=14)
        level_menu.pack(pady=5)
        tk.Button(self.left_pane, text='New Game', command=self.new_game, width=18, font=('Arial', 12)).pack(pady=8)
        tk.Button(self.left_pane, text='Hint', command=self.hint, width=18, font=('Arial', 12)).pack(pady=8)
        tk.Button(self.left_pane, text='Solve', command=self.solve, width=18, font=('Arial', 12)).pack(pady=8)
        tk.Label(self.left_pane, text='Background:', font=('Arial', 13), bg='#f0f0f0').pack(pady=(20,5))
        display_names = [f[1] for f in self.bg_files]
        self.bg_dropdown = ttk.Combobox(self.left_pane, textvariable=self.bg_dropdown_var, values=display_names, state='readonly', width=18)
        self.bg_dropdown.pack(pady=5)
        self.bg_dropdown.bind('<<ComboboxSelected>>', self.set_bg_from_dropdown)
        self.board_size = 900
        self.cell_size = self.board_size // 9
        self.board_frame = tk.Frame(self.main_frame, width=self.board_size, height=self.board_size, bg='#ffffff', highlightbackground='#cccccc', highlightthickness=2)
        self.board_frame.pack(side=tk.LEFT, padx=20, pady=20)
        self.canvas = tk.Canvas(self.board_frame, width=self.board_size, height=self.board_size, highlightthickness=0, bg='white')
        self.canvas.pack()
        self.canvas.bind('<Button-1>', self.focus_entry)

    def draw_board(self):
        self.canvas.delete('all')
        self.canvas.create_rectangle(0, 0, self.board_size, self.board_size, fill='white', outline='')
        if self.bg_path:
            try:
                img = Image.open(self.bg_path).resize((self.board_size, self.board_size), Image.LANCZOS)
                self.bg_image = ImageTk.PhotoImage(img)
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_image)
            except Exception as e:
                messagebox.showerror('Image Error', f'Could not load image: {e}')
                self.bg_image = None
        for i in range(10):
            if i % 3 == 0:
                self.canvas.create_line(0, i*self.cell_size, self.board_size, i*self.cell_size, width=8, fill='#888888')
                self.canvas.create_line(i*self.cell_size, 0, i*self.cell_size, self.board_size, width=8, fill='#888888')
            else:
                self.canvas.create_line(0, i*self.cell_size, self.board_size, i*self.cell_size, width=2, fill='#222')
                self.canvas.create_line(i*self.cell_size, 0, i*self.cell_size, self.board_size, width=2, fill='#222')
        for i in range(9):
            for j in range(9):
                if self.entries[i][j]:
                    self.entries[i][j].destroy()
                self.entries[i][j] = None
        for i in range(9):
            for j in range(9):
                val = self.sudoku.board[i][j]
                x, y = j*self.cell_size+self.cell_size//2, i*self.cell_size+self.cell_size//2
                if val != 0:
                    self.canvas.create_text(x, y, text=str(val), font=('Helvetica Neue', 36, 'bold'), fill='white')
                else:
                    entry = tk.Entry(self.board_frame, justify='center', font=('Helvetica Neue', 32), width=2, bd=0, bg='white', highlightthickness=1, highlightbackground='#bbb')
                    entry.place(x=j*self.cell_size+8, y=i*self.cell_size+8, width=self.cell_size-16, height=self.cell_size-16)
                    self.entries[i][j] = entry

    def new_game(self):
        self.sudoku = Sudoku(self.level_var.get())
        self.selected_cell = None
        self.draw_board()

    def get_board_from_entries(self):
        board = []
        for i in range(9):
            row = []
            for j in range(9):
                if self.sudoku.board[i][j] != 0:
                    row.append(self.sudoku.board[i][j])
                else:
                    entry = self.entries[i][j]
                    val = entry.get() if entry else ''
                    try:
                        num = int(val)
                    except ValueError:
                        num = 0
                    row.append(num)
            board.append(row)
        return board

    def check_victory(self):
        board = self.get_board_from_entries()
        for i in range(9):
            for j in range(9):
                if board[i][j] != self.sudoku.solution[i][j]:
                    return False
        self.show_victory()
        return True

    def show_victory(self):
        for _ in range(3):
            self.canvas.create_rectangle(0, 0, self.board_size, self.board_size, fill='#ffe066', outline='')
            self.root.update()
            self.root.after(150)
            self.canvas.create_rectangle(0, 0, self.board_size, self.board_size, fill='white', outline='')
            self.root.update()
            self.root.after(150)
        messagebox.showinfo('Congratulations!', 'You solved the puzzle!')

    def hint(self):
        # Highlight cells based on whether the entered value matches the solution
        for i in range(9):
            for j in range(9):
                if self.sudoku.board[i][j] != 0:
                    continue
                entry = self.entries[i][j]
                val = entry.get()
                if val == '':
                    entry.config(bg='white')
                    continue
                try:
                    num = int(val)
                except ValueError:
                    entry.config(bg='#ffb6b6')
                    continue
                if num == self.sudoku.solution[i][j]:
                    entry.config(bg='#b6fcb6')  # Green for correct
                else:
                    entry.config(bg='#ffb6b6')  # Red for incorrect
        self.check_victory()

    def solve(self):
        # Show the full solution, all numbers, and make all cells non-editable
        for i in range(9):
            for j in range(9):
                if self.entries[i][j]:
                    self.entries[i][j].destroy()
                self.entries[i][j] = None
        for i in range(9):
            for j in range(9):
                val = self.sudoku.solution[i][j]
                x, y = j*self.cell_size+self.cell_size//2, i*self.cell_size+self.cell_size//2
                self.canvas.create_text(x, y, text=str(val), font=('Helvetica Neue', 36, 'bold'), fill='white')
        self.check_victory()

    def set_bg_from_dropdown(self, event):
        selected_name = self.bg_dropdown_var.get()
        for abs_path, display_name in self.bg_files:
            if display_name == selected_name:
                self.bg_path = abs_path
                self.draw_board()
                break

    def focus_entry(self, event):
        x, y = event.x, event.y
        row, col = y // self.cell_size, x // self.cell_size
        if 0 <= row < 9 and 0 <= col < 9:
            entry = self.entries[row][col]
            if entry:
                entry.focus_set()
                self.root.after(100, self.check_victory)

if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('1200x1000')
    app = SudokuGUI(root)
    root.mainloop()
