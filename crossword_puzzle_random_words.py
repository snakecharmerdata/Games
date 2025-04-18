import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import random
import requests
import json
import time

class CrosswordPuzzle:
    def __init__(self, root):
        self.root = root
        self.root.title("Crossword Puzzle")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Category topics for word generation
        self.categories = {
            'Science': ['science', 'biology', 'chemistry', 'physics', 'astronomy'],
            'History': ['history', 'ancient', 'medieval', 'revolution', 'civilization'],
            'Politics': ['politics', 'government', 'democracy', 'election', 'parliament'],
            'Geography': ['geography', 'mountain', 'river', 'ocean', 'climate']
        }
        
        # Current subject
        self.current_subject = 'Science'  # Default subject
        
        # Crossword data will be generated
        self.crossword_data = {
            'words': [],
            'size': 12  # 12x12 grid (smaller for 6-word puzzles)
        }
        
        # Number of words to include in the puzzle
        self.word_count = 6  # Default to 6 words for quick games
        
        # Status label for feedback
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        self.create_widgets()
        self.fetch_words_and_generate()
        
    def fetch_words_for_category(self, category):
        """Fetch random words related to a category using Datamuse API"""
        words_with_clues = []
        topics = self.categories[category]
        
        # Update status
        self.status_var.set(f"Fetching words for {category}...")
        self.root.update()
        
        # Try each topic until we get enough words
        for topic in topics:
            try:
                # Get words related to the topic
                response = requests.get(
                    f"https://api.datamuse.com/words?ml={topic}&md=d&max=40"
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for item in data:
                        # Check if the word has a definition and is appropriate length
                        if ('defs' in item and 
                            len(item['word']) >= 3 and 
                            len(item['word']) <= 10 and
                            ' ' not in item['word'] and  # No spaces
                            "'" not in item['word']):    # No apostrophes
                            
                            word = item['word'].upper()
                            # Get the first definition
                            definition = item['defs'][0].split('\t')[1] if item['defs'] else f"Related to {topic}"
                            
                            # Capitalize first letter of definition
                            definition = definition[0].upper() + definition[1:]
                            
                            words_with_clues.append({
                                'word': word,
                                'clue': definition
                            })
                
                # If we have enough words, break
                if len(words_with_clues) >= 20:
                    break
                    
            except Exception as e:
                print(f"Error fetching words: {e}")
        
        # If we couldn't get enough words, add some fallback words
        if len(words_with_clues) < 10:
            fallback_words = self.get_fallback_words(category)
            words_with_clues.extend(fallback_words)
        
        # Shuffle and return
        random.shuffle(words_with_clues)
        return words_with_clues
    
    def get_fallback_words(self, category):
        """Provide fallback words in case the API fails"""
        fallback = {
            'Science': [
                {'word': 'ATOM', 'clue': 'Smallest unit of an element'},
                {'word': 'CELL', 'clue': 'Basic unit of life'},
                {'word': 'DNA', 'clue': 'Molecule containing genetic instructions'},
                {'word': 'ENERGY', 'clue': 'Capacity to do work'},
                {'word': 'GRAVITY', 'clue': 'Force that attracts objects toward Earth'},
                {'word': 'MOLECULE', 'clue': 'Group of atoms bonded together'},
                {'word': 'NEWTON', 'clue': 'Unit of force named after a physicist'},
                {'word': 'OXYGEN', 'clue': 'Element essential for respiration'},
                {'word': 'PHOTON', 'clue': 'Particle of light'},
                {'word': 'QUANTUM', 'clue': 'Discrete packet of energy'}
            ],
            'History': [
                {'word': 'ANCIENT', 'clue': 'Belonging to the very distant past'},
                {'word': 'ARTIFACT', 'clue': 'Object made by humans of historical interest'},
                {'word': 'CENTURY', 'clue': 'Period of 100 years'},
                {'word': 'DYNASTY', 'clue': 'Line of hereditary rulers'},
                {'word': 'EMPIRE', 'clue': 'Group of countries under a single authority'},
                {'word': 'FEUDAL', 'clue': 'Relating to the Middle Ages social system'},
                {'word': 'MEDIEVAL', 'clue': 'Relating to the Middle Ages'},
                {'word': 'MONARCHY', 'clue': 'Form of government with a king or queen'},
                {'word': 'REVOLUTION', 'clue': 'Forcible overthrow of a government'},
                {'word': 'TREATY', 'clue': 'Formal agreement between states'}
            ],
            'Politics': [
                {'word': 'BALLOT', 'clue': 'Paper used to cast a vote'},
                {'word': 'CAMPAIGN', 'clue': 'Organized effort to win an election'},
                {'word': 'CONGRESS', 'clue': 'Legislative body in the US'},
                {'word': 'DEMOCRACY', 'clue': 'Government by the people'},
                {'word': 'ELECTION', 'clue': 'Formal process of selecting a person for office'},
                {'word': 'GOVERNMENT', 'clue': 'Group that controls and makes decisions for a country'},
                {'word': 'IDEOLOGY', 'clue': 'System of ideas and ideals'},
                {'word': 'JUSTICE', 'clue': 'Fair treatment or behavior'},
                {'word': 'LAW', 'clue': 'System of rules enforced by a society'},
                {'word': 'LOBBY', 'clue': 'Group that tries to influence legislation'}
            ],
            'Geography': [
                {'word': 'ATLAS', 'clue': 'Book of maps'},
                {'word': 'CANYON', 'clue': 'Deep gorge between cliffs'},
                {'word': 'CLIMATE', 'clue': 'Weather conditions of an area'},
                {'word': 'CONTINENT', 'clue': 'Large landmass on Earth'},
                {'word': 'DESERT', 'clue': 'Arid land with little rainfall'},
                {'word': 'EQUATOR', 'clue': 'Imaginary line dividing Earth into Northern and Southern Hemispheres'},
                {'word': 'GLACIER', 'clue': 'Slowly moving mass of ice'},
                {'word': 'HEMISPHERE', 'clue': 'Half of the Earth'},
                {'word': 'ISLAND', 'clue': 'Land surrounded by water'},
                {'word': 'JUNGLE', 'clue': 'Dense tropical forest'}
            ]
        }
        
        return fallback.get(category, [])
    
    def fetch_words_and_generate(self):
        """Fetch words and generate the crossword"""
        try:
            # Fetch words for the current subject
            words = self.fetch_words_for_category(self.current_subject)
            
            # Generate the crossword
            self.generate_crossword(words)
            
            # Create the grid and clues
            self.create_crossword_grid()
            self.create_clues_panel()
            
            # Update status
            self.status_var.set(f"Ready - {self.current_subject} puzzle with 6 words")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate puzzle: {str(e)}")
            self.status_var.set("Error generating puzzle")
    
    def generate_crossword(self, word_list):
        """Generate a random crossword puzzle based on the provided word list"""
        grid_size = self.crossword_data['size']
        grid = [[None for _ in range(grid_size)] for _ in range(grid_size)]
        
        # Shuffle the word list to get random words
        random.shuffle(word_list)
        selected_words = []
        
        # Place the first word in the middle horizontally
        first_word = word_list[0]['word']
        first_word_row = grid_size // 2
        first_word_col = (grid_size - len(first_word)) // 2
        
        # Add the first word
        for i, char in enumerate(first_word):
            grid[first_word_row][first_word_col + i] = char
        
        selected_words.append({
            'word': first_word,
            'clue': word_list[0]['clue'],
            'row': first_word_row,
            'col': first_word_col,
            'direction': 'across'
        })
        
        # Try to place more words
        for word_data in word_list[1:]:
            if len(selected_words) >= self.word_count:  # Limit to specified word count
                break
                
            word = word_data['word']
            placed = False
            
            # Try to place the word vertically first
            for existing_word in selected_words:
                if existing_word['direction'] == 'across':
                    for i, char in enumerate(existing_word['word']):
                        for j, new_char in enumerate(word):
                            if char == new_char:
                                # Try to place the word vertically through this intersection
                                row = existing_word['row']
                                col = existing_word['col'] + i
                                start_row = row - j
                                
                                # Check if the word fits
                                if start_row >= 0 and start_row + len(word) <= grid_size:
                                    can_place = True
                                    
                                    # Check if the placement is valid
                                    for k, c in enumerate(word):
                                        r = start_row + k
                                        # Skip the intersection point
                                        if r == row:
                                            continue
                                        # Check if the cell is empty or has the same character
                                        if grid[r][col] is not None and grid[r][col] != c:
                                            can_place = False
                                            break
                                    
                                    if can_place:
                                        # Place the word
                                        for k, c in enumerate(word):
                                            r = start_row + k
                                            grid[r][col] = c
                                        
                                        selected_words.append({
                                            'word': word,
                                            'clue': word_data['clue'],
                                            'row': start_row,
                                            'col': col,
                                            'direction': 'down'
                                        })
                                        placed = True
                                        break
                            if placed:
                                break
                        if placed:
                            break
                
                # Try to place the word horizontally
                elif existing_word['direction'] == 'down' and not placed:
                    for i, char in enumerate(existing_word['word']):
                        for j, new_char in enumerate(word):
                            if char == new_char:
                                # Try to place the word horizontally through this intersection
                                row = existing_word['row'] + i
                                col = existing_word['col']
                                start_col = col - j
                                
                                # Check if the word fits
                                if start_col >= 0 and start_col + len(word) <= grid_size:
                                    can_place = True
                                    
                                    # Check if the placement is valid
                                    for k, c in enumerate(word):
                                        c_col = start_col + k
                                        # Skip the intersection point
                                        if c_col == col:
                                            continue
                                        # Check if the cell is empty or has the same character
                                        if grid[row][c_col] is not None and grid[row][c_col] != c:
                                            can_place = False
                                            break
                                    
                                    if can_place:
                                        # Place the word
                                        for k, c in enumerate(word):
                                            c_col = start_col + k
                                            grid[row][c_col] = c
                                        
                                        selected_words.append({
                                            'word': word,
                                            'clue': word_data['clue'],
                                            'row': row,
                                            'col': start_col,
                                            'direction': 'across'
                                        })
                                        placed = True
                                        break
                            if placed:
                                break
                        if placed:
                            break
                
                if placed:
                    break
        
        # Update the crossword data
        self.crossword_data['words'] = selected_words
    
    def create_widgets(self):
        # Main frame to hold everything
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top control panel
        self.control_panel = tk.Frame(self.main_frame)
        self.control_panel.pack(fill=tk.X, pady=5)
        
        # Subject selection dropdown
        subject_label = tk.Label(self.control_panel, text="Current Subject:", font=('Arial', 12))
        subject_label.pack(side=tk.LEFT, padx=10)
        
        self.subject_var = tk.StringVar(value=self.current_subject)
        self.subject_label = tk.Label(self.control_panel, textvariable=self.subject_var, 
                                     font=('Arial', 12, 'bold'), fg='blue')
        self.subject_label.pack(side=tk.LEFT, padx=5)
        
        # Status label
        status_label = tk.Label(self.control_panel, textvariable=self.status_var, 
                               font=('Arial', 10), fg='gray')
        status_label.pack(side=tk.LEFT, padx=20)
        
        # New Game button
        self.new_game_button = tk.Button(self.control_panel, text="New Game", 
                                        command=self.new_game, bg='green', fg='blue',
                                        font=('Arial', 11, 'bold'), padx=10)
        self.new_game_button.pack(side=tk.RIGHT, padx=10)
        
        # Frame for the crossword grid
        self.grid_frame = tk.Frame(self.main_frame, bd=2, relief=tk.RIDGE)
        self.grid_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame for clues and controls
        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)
        
        # Buttons
        self.button_frame = tk.Frame(self.right_frame)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        self.check_button = tk.Button(self.button_frame, text="Check Answers", command=self.check_answers)
        self.check_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = tk.Button(self.button_frame, text="Clear All", command=self.clear_all)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        self.hint_button = tk.Button(self.button_frame, text="Get Hint", command=self.get_hint)
        self.hint_button.pack(side=tk.LEFT, padx=5)
    
    def new_game(self):
        """Start a new game with category selection"""
        # Create a category selection dialog
        category_window = tk.Toplevel(self.root)
        category_window.title("Select Category")
        category_window.geometry("300x200")
        category_window.transient(self.root)  # Make it a modal dialog
        category_window.grab_set()  # Make it modal
        
        # Center the window
        category_window.update_idletasks()
        width = category_window.winfo_width()
        height = category_window.winfo_height()
        x = (category_window.winfo_screenwidth() // 2) - (width // 2)
        y = (category_window.winfo_screenheight() // 2) - (height // 2)
        category_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Title
        title_label = tk.Label(category_window, text="Choose a Category", font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)
        
        # Category buttons
        def select_category(category):
            self.current_subject = category
            self.subject_var.set(category)
            category_window.destroy()
            self.fetch_words_and_generate()
        
        categories = list(self.categories.keys())
        for category in categories:
            btn = tk.Button(category_window, text=category, width=20, 
                           command=lambda cat=category: select_category(cat))
            btn.pack(pady=5)
    
    def create_crossword_grid(self):
        # Clear existing grid if any
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
            
        # Create the grid of entry widgets
        self.grid_size = self.crossword_data['size']
        self.cells = []
        
        # Determine which cells need numbers
        self.cell_numbers = {}
        number = 1
        
        # Sort words to ensure consistent numbering
        sorted_words = sorted(self.crossword_data['words'], key=lambda w: (w['row'], w['col']))
        
        for word_data in sorted_words:
            row, col = word_data['row'], word_data['col']
            if (row, col) not in self.cell_numbers:
                self.cell_numbers[(row, col)] = number
                number += 1
        
        # Create the grid cells
        for i in range(self.grid_size):
            row_cells = []
            for j in range(self.grid_size):
                # Create a frame for each cell
                cell_frame = tk.Frame(self.grid_frame, width=45, height=45, bd=1, relief=tk.SOLID)
                cell_frame.grid(row=i, column=j, padx=1, pady=1)
                cell_frame.grid_propagate(False)  # Maintain the size
                
                # Check if this cell is part of a word
                is_part_of_word = False
                for word_data in self.crossword_data['words']:
                    word = word_data['word']
                    start_row, start_col = word_data['row'], word_data['col']
                    direction = word_data['direction']
                    
                    if direction == 'across':
                        if i == start_row and start_col <= j < start_col + len(word):
                            is_part_of_word = True
                            break
                    else:  # direction == 'down'
                        if j == start_col and start_row <= i < start_row + len(word):
                            is_part_of_word = True
                            break
                
                if is_part_of_word:
                    # Add number label if needed - IMPROVED VISIBILITY
                    if (i, j) in self.cell_numbers:
                        number_label = tk.Label(cell_frame, text=str(self.cell_numbers[(i, j)]), 
                                              font=('Arial', 10, 'bold'), fg='blue', anchor='nw')
                        number_label.place(x=2, y=1)
                    
                    entry = tk.Entry(cell_frame, font=('Arial', 16), width=2, justify='center')
                    entry.place(relx=0.5, rely=0.5, anchor='center')
                    
                    # Configure entry to accept only one uppercase letter
                    vcmd = (self.root.register(self.validate_input), '%P', '%W')
                    entry.configure(validate="key", validatecommand=vcmd)
                    
                    row_cells.append(entry)
                else:
                    # Black cell (not part of any word)
                    cell_frame.configure(bg='grey')
                    row_cells.append(None)
            
            self.cells.append(row_cells)
        
        # Add row and column labels
        for i in range(self.grid_size):
            # Row labels (numbers)
            row_label = tk.Label(self.grid_frame, text=str(i+1), width=2, font=('Arial', 8))
            row_label.grid(row=i, column=self.grid_size, sticky='w')
            
            # Column labels (letters)
            col_label = tk.Label(self.grid_frame, text=chr(65+i), width=2, font=('Arial', 8))
            col_label.grid(row=self.grid_size, column=i, sticky='n')
    
    def validate_input(self, new_text, widget_name):
        # Allow only a single uppercase letter
        if len(new_text) > 1:
            return False
        if new_text and not new_text.isalpha():
            return False
        
        # Convert to uppercase
        if new_text and new_text.islower():
            widget = self.root.nametowidget(widget_name)
            widget.delete(0, tk.END)
            widget.insert(0, new_text.upper())
            return False
            
        return True
    
    def create_clues_panel(self):
        # Clear existing clues if any
        for widget in self.right_frame.winfo_children():
            if widget != self.button_frame:
                widget.destroy()
        
        # Create scrollable frame for clues
        self.clues_canvas = tk.Canvas(self.right_frame, width=300)
        self.clues_scrollbar = tk.Scrollbar(self.right_frame, orient="vertical", command=self.clues_canvas.yview)
        self.clues_canvas.configure(yscrollcommand=self.clues_scrollbar.set)
        
        self.clues_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.clues_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.clues_frame = tk.Frame(self.clues_canvas)
        self.clues_canvas.create_window((0, 0), window=self.clues_frame, anchor="nw")
        
        # Title with subject
        title_label = tk.Label(self.clues_frame, text=f"{self.current_subject} Crossword", 
                              font=('Arial', 14, 'bold'))
        title_label.pack(anchor='center', pady=5)
        
        # Word count info
        word_count_label = tk.Label(self.clues_frame, 
                                   text=f"6-Word Quick Puzzle", 
                                   font=('Arial', 10, 'italic'))
        word_count_label.pack(anchor='center', pady=2)
        
        instructions = "Fill in the puzzle using the clues below.\nNumbers in the grid correspond to the clue numbers."
        instructions_label = tk.Label(self.clues_frame, text=instructions, justify='center')
        instructions_label.pack(anchor='center', pady=5)
        
        # Across clues
        across_label = tk.Label(self.clues_frame, text="Across", font=('Arial', 12, 'bold'), fg='blue')
        across_label.pack(anchor='w', padx=5, pady=5)
        
        across_clues = [word for word in self.crossword_data['words'] if word['direction'] == 'across']
        across_clues.sort(key=lambda w: self.cell_numbers.get((w['row'], w['col']), 999))
        
        for word in across_clues:
            number = self.cell_numbers.get((word['row'], word['col']), "?")
            # Add grid reference
            grid_ref = f"({word['row']+1},{chr(65+word['col'])})"
            clue_text = f"{number}. {word['clue']} {grid_ref}"
            clue_label = tk.Label(self.clues_frame, text=clue_text, wraplength=280, justify='left')
            clue_label.pack(anchor='w', padx=10, pady=2)
        
        # Down clues
        down_label = tk.Label(self.clues_frame, text="Down", font=('Arial', 12, 'bold'), fg='blue')
        down_label.pack(anchor='w', padx=5, pady=5)
        
        down_clues = [word for word in self.crossword_data['words'] if word['direction'] == 'down']
        down_clues.sort(key=lambda w: self.cell_numbers.get((w['row'], w['col']), 999))
        
        for word in down_clues:
            number = self.cell_numbers.get((word['row'], word['col']), "?")
            # Add grid reference
            grid_ref = f"({word['row']+1},{chr(65+word['col'])})"
            clue_text = f"{number}. {word['clue']} {grid_ref}"
            clue_label = tk.Label(self.clues_frame, text=clue_text, wraplength=280, justify='left')
            clue_label.pack(anchor='w', padx=10, pady=2)
        
        # Legend explaining the numbering system
        legend_frame = tk.Frame(self.clues_frame, bd=1, relief=tk.RIDGE)
        legend_frame.pack(fill=tk.X, padx=5, pady=10)
        
        legend_title = tk.Label(legend_frame, text="How to Read the Grid", font=('Arial', 10, 'bold'))
        legend_title.pack(anchor='w', padx=5, pady=2)
        
        legend_text = "• Blue numbers in cells correspond to clue numbers\n"
        legend_text += "• (Row,Column) coordinates are shown after each clue\n"
        legend_text += "• Rows are numbered 1-12 from top to bottom\n"
        legend_text += "• Columns are labeled A-L from left to right"
        
        legend_label = tk.Label(legend_frame, text=legend_text, justify='left')
        legend_label.pack(anchor='w', padx=5, pady=2)
        
        # Update the canvas scroll region
        self.clues_frame.update_idletasks()
        self.clues_canvas.config(scrollregion=self.clues_canvas.bbox("all"))
    
    def check_answers(self):
        correct_count = 0
        total_cells = 0
        
        for word_data in self.crossword_data['words']:
            word = word_data['word']
            start_row, start_col = word_data['row'], word_data['col']
            direction = word_data['direction']
            
            for i, char in enumerate(word):
                if direction == 'across':
                    row, col = start_row, start_col + i
                else:  # direction == 'down'
                    row, col = start_row + i, start_col
                
                cell = self.cells[row][col]
                if cell:
                    total_cells += 1
                    user_char = cell.get().upper()
                    if user_char == char:
                        correct_count += 1
                        cell.configure(bg='lightgreen')  # Mark correct answers
                    else:
                        cell.configure(bg='pink')  # Mark incorrect answers
        
        # Show result message
        if total_cells == correct_count:
            messagebox.showinfo("Congratulations!", "All answers are correct!")
        else:
            messagebox.showinfo("Result", f"You got {correct_count} out of {total_cells} correct.")
    
    def clear_all(self):
        for row in self.cells:
            for cell in row:
                if cell:
                    cell.delete(0, tk.END)
                    cell.configure(bg='white')
    
    def get_hint(self):
        # Find empty or incorrect cells
        hint_candidates = []
        
        for word_data in self.crossword_data['words']:
            word = word_data['word']
            start_row, start_col = word_data['row'], word_data['col']
            direction = word_data['direction']
            
            for i, char in enumerate(word):
                if direction == 'across':
                    row, col = start_row, start_col + i
                else:  # direction == 'down'
                    row, col = start_row + i, start_col
                
                cell = self.cells[row][col]
                if cell and (not cell.get() or cell.get().upper() != char):
                    hint_candidates.append((row, col, char))
        
        if hint_candidates:
            # Choose a random cell to give a hint for
            row, col, char = random.choice(hint_candidates)
            cell = self.cells[row][col]
            cell.delete(0, tk.END)
            cell.insert(0, char)
            cell.configure(bg='lightyellow')  # Mark as a hint
            messagebox.showinfo("Hint", f"Added letter '{char}' as a hint.")
        else:
            messagebox.showinfo("Hint", "No hints needed - all answers are correct!")

if __name__ == "__main__":
    # Make sure requests is installed
    try:
        import requests
    except ImportError:
        print("The 'requests' library is required. Please install it using:")
        print("pip install requests")
        exit(1)
        
    root = tk.Tk()
    app = CrosswordPuzzle(root)
    root.mainloop()