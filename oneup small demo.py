import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage
from tkinter import messagebox



#from tkinter import font

##inputs
#myfont = font.Font(size=20)
#grid size
gsize = 9
cells = 50
#timer (keep 0 unless for testing)
secs = 0
mins = 0
hours = 0
is_paused = False
#starting grid
#starter_grid = [
#    [None, 2, None, None, 5, None, None, None , None], 
#    [1, None, None, 4, None, None, None, None , None], 
#    [None, None, 3, None, None, 6, None, None , None],
#    [None]*10,
#    [None]*10,
#    [None]*10,
#    [None]*10,
#    [None]*10,
#    [None]*10
#]
starter_grid = [
    [5, 3, None, 6, 7, 8, 9, 1, 2],
    [6, None, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, None, 7],
    
    [8, 5, 9, 7, 6, 1, None, 2, 3],
    [4, 2, 6, 8, None, 3, 7, 9, 1],
    [7, None, 3, 9, 2, 4, 8, 5, 6],
    
    [9, 6, 1, 5, 3, 7, 2, 8, None],
    [2, 8, 7, 4, 1, 9, None, 3, 5],
    [3, 4, 5, None, 8, 6, 1, 7, 9]
]

#walls = [('row', 0, [2]), 
#         ('col', 1, [4])]
walls = []
row_walls = {}
col_walls = {}
conflicts = []


for direction, index, breaks in walls:
    if direction == 'row':
        row_walls[index] = breaks
    elif direction == 'col':
        col_walls[index] = breaks


def load(starter_grid):
    for i, row in enumerate(starter_grid):
        for j, value in enumerate(row):
            if i < gsize**2 and j < gsize:
                entry = grid[i][j]
                entry.delete(0, tk.END)
                if value is not None and value != 0:
                    entry.insert(0, str(value))
                    entry.config(state='readonly', fg='blue', disabledforeground="blue")

#grid
def creategrid(root):
    grid = []

    wall_right = {r: set() for r in range(gsize)}
    wall_below = {c: set() for c in range(gsize)}

    for direction, idx, breaks in walls:
        if direction == 'row':
            wall_right[idx] = set(breaks)
        elif direction == 'col':
            wall_below[idx] = set(breaks)

    for i in range(gsize):
        row = []
        for j in range(gsize):
            top = 2 if i == 0 else (2 if i in wall_below.get(j, set()) else 1)
            left = 2 if j == 0 else (2 if j in wall_right.get(i, set()) else 1)
            bottom = 2 if (i + 1) in wall_below.get(j, set()) else 0
            right = 2 if (j + 1) in wall_right.get(i, set()) else 0

            border_frame = tk.Frame(root, bg="black", highlightthickness=0, width=cells, height = cells)
            border_frame.grid_propagate(False)
            border_frame.grid(row=i+1, column=j, padx=(0, 0), pady=(0, 0))

            inner = tk.Frame(border_frame, bg="black", bd=0, height = cells, width = cells)
            inner.pack(padx=(left, right), pady=(top, bottom))

            validate_command = root.register(validate)
            entry = tk.Entry(inner, width = 3, font=('Arial', 27), justify='center', bd=0,
                             fg="black", bg='white', insertwidth=3, highlightthickness=0,
                             insertbackground="lightyellow", selectbackground="lightyellow",
                             validate='key', validatecommand=(validate_command, '%P'))
            entry.pack()
            entry.bind("<Button-1>", lambda event, e=entry: (cellselect(e), "break"))
            entry.bind('<KeyRelease>', lambda event: check_conflicts())
            entry.bind('<KeyPress>', lambda e, en=entry: on_key_press(e, en))

            row.append(entry)
        grid.append(row)

    return grid

def segment_line(size, breaks):
    sections = []
    last = 0
    for b in breaks:
        sections.append(list(range(last, b)))
        last = b
    sections.append(list(range(last, size)))
    return sections

#clear button
def clear_grid():
    for row in grid:
        for entry in row:
            if entry.cget('state') != 'readonly':
                entry.delete(0, tk.END)
    hlreset()
    check_conflicts()

#entry validation
def validate(input):
    if input == "" or (input.isdigit() and 1<= int(input) <= gsize):
        return True
    elif input == "0" and gsize == 10:
        return True
    else:
        return False

def rowseg(row_index):
    breaks = row_walls.get(row_index)
    if breaks:
        return segment_line(gsize, breaks)
    return [list(range(gsize))]

def colseg(col_index):
    breaks = col_walls.get(col_index)
    if breaks:
        return segment_line(gsize, breaks)
    return [list(range(gsize))]

def check_conflicts():
    row_conflicts = set()
    col_conflicts = set()
    global conflicts

    for i in range(gsize):
        segments = rowseg(i)
        for segment in segments:
            seen = {}
            for j in segment:
                val = grid[i][j].get()
                if val != "":
                    if val in seen:
                        row_conflicts.add((i, j))
                        row_conflicts.add((i, seen[val]))
                    else:
                        seen[val] = j

    for j in range(gsize):
        segments = colseg(j)
        for segment in segments:
            seen = {}
            for i in segment:
                val = grid[i][j].get()
                if val != "":
                    if val in seen:
                        col_conflicts.add((i, j))
                        col_conflicts.add((seen[val], j))
                    else:
                        seen[val] = i

    for i in range(gsize):
        for j in range(gsize):
            entry = grid[i][j]
            if (i, j) in row_conflicts or (i, j) in col_conflicts:
                entry.config(fg="red", selectforeground="red")
                conflicts.append((i,j))
            else:
                reset_fg(entry)

def reset_fg(entry):
    if entry.cget("state") == "readonly":
        entry.config(fg="blue", selectforeground="black")
    else:
        entry.config(fg="black", selectforeground="lightyellow")

#cell selecting
def cellselect(entry):
    global selected_entry
    selected_entry = entry
    hlreset()
    entry.config(bg="lightyellow")

def hlreset():
    for row in grid:
        for entry in row:
            entry.config(bg="white")

def setnum(number):
    if selected_entry:
        selected_entry.delete(0, tk.END)
        selected_entry.insert(tk.END, str(number))
        check_conflicts()
        check_win()

def on_key_press(event, entry):
    if event.char.isdigit():
        entry.delete(0, tk.END)
    check_conflicts()
    check_win()
    return None

root = tk.Tk()
root.title("oneup")
root.geometry("600x600")
root.configure(bg='white')


grid = creategrid(root)
load(starter_grid)

selected_entry = None

#buttons
button_frame = tk.Frame(root, bg="white")
button_frame.grid(row=gsize+1, column=0, columnspan=gsize, pady=10)

for num in range(1, gsize + 1):
    btn = tk.Button(button_frame, text=str(num), width=4, font=('Arial', 14), bg="white", command=lambda n=num: setnum(n))
    btn.pack(side=tk.LEFT, padx=5)

#timer
def timer_loop():
    global secs, mins, hours
    if not is_paused:
        if secs == 60:
            secs = 0
            mins += 1
        if mins == 60:
            mins = 0 
            hours += 1
        timer.config(text=f"{hours:02}:{mins:02}:{secs:02}")
        secs += 1
    timer.after(1000, timer_loop)
    
topbar = tk.Frame(root, bg='white')
topbar.grid(row=0, column=0, columnspan=gsize, sticky="e", padx=10, pady=10)

timer = tk.Label(topbar, bg="white")
timer.pack(side=tk.RIGHT, padx=(0, 5))
timer_loop() 

trash = tk.Button(root, text="bye bye", bg='white', command=clear_grid)
trash.grid(row=gsize+2,column=gsize-1)

#pause button
image = PhotoImage(file="pause.png")
smaller=image.subsample(10,10)

pause = tk.Button(root, image=smaller, bg="white", relief="flat", borderwidth=0, command=lambda: toggle_pause())
pause.place(x=485,y=7)

overlay = tk.Frame(root, bg="white")
overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
overlay.lower()
overlay_visible = False

paused = tk.Button(root, image=smaller, bg="white", relief="flat", borderwidth=0, command=lambda: toggle_pause())
paused.place(x=485,y=7)
paused.lower()

def toggle_pause():
    global is_paused
    if not is_paused:
        overlay.lift()
        paused.lift()
        pause.lower()
        is_paused = True
    else:
        overlay.lower()
        pause.lift()
        paused.lower()
        is_paused = False

def is_valid(grid, row, col, num):
    # Check row
    if num in grid[row]:
        return False
    # Check column
    for i in range(gsize):
        if grid[i][col] == num:
            return False
    return True

def find_empty(grid):
    for i in range(gsize):
        for j in range(gsize):
            if grid[i][j] is None:
                return (i, j)
    return None

def is_solvable(grid):
    empty = find_empty(grid)
    if not empty:
        return True  
    row, col = empty

    for num in range(1, gsize + 1):
        if is_valid(grid, row, col, num):
            grid[row][col] = num
            if is_solvable(grid):
                return True
            grid[row][col] = None  
    return False


def check_win():
    check_conflicts()
    for i in range(gsize):
        for j in range(gsize):
            val = grid[i][j].get()
            print("Checking cell:", i, j, "value:", val, "in conflict:", (i, j) in conflicts)
            if val == "" or (i,j) in conflicts:
                return False
    print("You win!")
    win_popup()
    return

def win_popup():
    messagebox.showinfo("Victory!", f"You completed the puzzle in {hours:02}:{mins:02}:{secs:02}!")

#run main loop

root.mainloop()
