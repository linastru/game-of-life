import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from random import random
import ctypes
import os

# Define starting variables
board_h = 25
board_w = 50
life_probability = 0.3

# Define GUI variables
MARGIN = 50
CELL_H = 20
GAP = 3
BG_COLOR = "light gray"
ALIVE_COLOR = "#404040"
DEAD_COLOR = "white"
TICK_TIME = 250

BT_H = 72
LB_H = 65
MENU_W = 700
MENU_H = 480
MENU_GAP_Y = 10
MENU_COLOR = "light gray"

# Control variables
pause = True
wrap = True

# Boards directory path
BOARDS_DIR = os.getcwd() + "\\boards\\"

# Remove resolution scaling on high DPI screens.
ctypes.windll.user32.SetProcessDPIAware()

def random_board():
    board = []
    for i in range(board_h):
        board.append([])
        for j in range(board_w):
            if random() <= life_probability:
                board[i].append("0")
            else:
                board[i].append("-")
    return board

# This function assumes no wrap-around of the neighbour counting logic. I.e. neighbour checks end at board edges.
def count_neighbours_no_wrap(y, x):
    neighbours = 0

    # Initialise the corners of the 9 cell square for neighbour counting.
    area_TL_x = -1
    area_TL_y = -1
    area_BR_x = 1
    area_BR_y = 1

    # Check if the cell is on the edge/corner of the board:
    if x == 0:
        area_TL_x = 0
    if x == board_w - 1:
        area_BR_x = 0
    if y == 0:
        area_TL_y = 0
    if y == board_h - 1:
        area_BR_y = 0

    # Count alive cells in the 9 cell square.
    for i in range((y + area_TL_y), (y + area_BR_y + 1)):
        for j in range((x + area_TL_x), (x + area_BR_x + 1)):
            if game_board[i][j] == "0":
                neighbours += 1

    # Subtract 1 from neighbours if cell in question is alive itself.
    if game_board[y][x] == "0":
        neighbours -= 1

    return neighbours

# This function assumes wrap-around of the neighbour counting logic.
def count_neighbours_wrap(y, x):
    neighbours = 0

    # Count alive cells in the 9 cell square.
    for i in range((y-1), (y+2)):
        for j in range((x-1), (x+2)):
            # Negative indices will be taken care of by negative index notation.
            # The following takes care of [len] indices.
            if i == board_h:
                i = 0
            if j == board_w:
                j = 0

            if game_board[i][j] == "0":
                neighbours += 1

    # Remove 1 from neighbours if cell in question is alive itself.
    if game_board[y][x] == "0":
        neighbours -= 1

    return neighbours

def generate_neighbour_matrix():
    # Check if wrap is enabled outside of the loop to make sure it is not changed
    # halfway through generating the neighbour matrix.

    neighbour_matrix = []

    if wrap:
        for i in range(board_h):
            neighbour_matrix.append([])
            for j in range(board_w):
                neighbour_matrix[i].append(count_neighbours_wrap(i, j))
    else:
        for i in range(board_h):
            neighbour_matrix.append([])
            for j in range(board_w):
                neighbour_matrix[i].append(count_neighbours_no_wrap(i, j))

    return neighbour_matrix

def new_board_state(neighbour_matrix):
    # Apply game of life rules.
    new_board = game_board

    for i in range(board_h):
        for j in range(board_w):
            if game_board[i][j] == "0":
                if neighbour_matrix[i][j] <= 1:
                    new_board[i][j] = "-"
                elif neighbour_matrix[i][j] <= 3:
                    new_board[i][j] = "0"
                else:
                    new_board[i][j] = "-"
            if game_board[i][j] == "-":
                if neighbour_matrix[i][j] == 3:
                    new_board[i][j] = "0"

    return new_board

def board_tick():
    global game_board
    if not pause:
        game_board = new_board_state(generate_neighbour_matrix())
        redraw_board()
    root.after(TICK_TIME, board_tick)

def redraw_board():
    global game_board
    x0 = MARGIN
    y0 = MARGIN
    x1 = x0 + CELL_H
    y1 = y0 + CELL_H

    canvas.delete("all")

    for i in range(board_h):
        for j in range(board_w):
            fill_color = DEAD_COLOR
            if game_board[i][j] == "0":
                fill_color = ALIVE_COLOR
            canvas.create_rectangle(x0, y0, x1, y1, width=0, fill=fill_color)
            x0 += (CELL_H + GAP)
            x1 = x0 + CELL_H
        x0 = MARGIN
        y0 += (CELL_H + GAP)
        x1 = x0 + CELL_H
        y1 = y0 + CELL_H

def update_canvas_size():
    h = (board_h * CELL_H) + (GAP * (board_h - 1))
    if h < MENU_H:
        h = MENU_H
    w = (board_w * CELL_H) + (GAP * (board_w - 1)) + MENU_W + MARGIN
    canvas.config(width=w, height=h)

def update_specs():
    spec_lb["text"] = ("Height: " + str(board_h) + "     Width: " + str(board_w) + "     Probability: " +
                       str(life_probability))

def update_menu_pos():
    menu_frame.place_configure(x=(board_w * CELL_H) + (GAP * (board_w - 1)) + (MARGIN * 2))

def toggle_pause():
    global pause
    pause = not pause
    if pause:
        pause_bt["relief"] = "sunken"
        pause_bt["bg"] = "tomato"
        toggle_save_entry()
    else:
        pause_bt["relief"] = "raised"
        pause_bt["bg"] = "yellow green"
        toggle_save_entry()

def toggle_save_entry():
    if pause:
        f_name_entry["state"] = "normal"
        f_name_input.set("")
        f_name_entry["justify"] = tk.RIGHT
    else:
        f_name_entry["state"] = "disabled"
        f_name_entry["justify"] = tk.CENTER
        f_name_input.set("*Pause game to save*")

def toggle_wrap():
    global wrap
    wrap = not wrap
    if wrap:
        wrap_bt["relief"] = "sunken"
        wrap_bt["bg"] = "sky blue"
    else:
        wrap_bt["relief"] = "raised"
        wrap_bt["bg"] = "SystemButtonFace"

def reset_board():
    global game_board
    game_board = random_board()
    redraw_board()

def resize():
    global game_board
    global board_w
    global board_h
    correct_h_input = False
    correct_w_input = False

    try:
        new_h = int(h_input.get())
        if new_h == 0:
            raise Exception("")
    except:
        h_input.set("Error")
    else:
        correct_h_input = True

    try:
        new_w = int(w_input.get())
        if new_w == 0:
            raise Exception("")
    except:
        w_input.set("Error")
    else:
        correct_w_input = True

    if correct_h_input and correct_w_input:
        board_h = new_h
        board_w = new_w
        w_input.set("")
        h_input.set("")

        game_board = random_board()
        update_canvas_size()
        redraw_board()
        update_menu_pos()
        update_specs()

def change_probability():
    global life_probability

    try:
        prob = float(prob_input.get())
        if 0 <= prob <= 1.0:
            life_probability = prob
            reset_board()
            update_specs()
            prob_input.set("")
        else:
            prob_input.set("Error")
    except:
        prob_input.set("Error")

def get_board_file_names():
    file_list = []
    for f in os.listdir(BOARDS_DIR):
        if os.path.isfile(BOARDS_DIR + f):
            if os.path.splitext(BOARDS_DIR + f)[1] == ".txt":
                file_list.append(f)
    return file_list

def load_board():
    global game_board
    global board_h
    global board_w

    file_name = dd_selection.get()
    if file_name != "Select file":
        new_board = generate_board_from_file(file_name)
        dd_selection.set("Select file")
        if new_board != None:
            if not is_board_rectangular(new_board):
                tk.messagebox.showerror(title="Error", message="Error: Loaded board is not rectangular.")
            else:
                if not pause:
                    toggle_pause()
                if not wrap:
                    toggle_wrap()

                board_h = len(new_board)
                board_w = len(new_board[0])
                game_board = new_board
                update_canvas_size()
                redraw_board()
                update_menu_pos()
                update_specs()

def generate_board_from_file(file_name):
    board = []
    i = 0
    try:
        with open(BOARDS_DIR + file_name, "r") as file:
            for line in file:
                board.append([])
                for c in line.strip("\n"):
                    if c != "-" and c != "0":
                        raise Exception("Invalid character in board file.")
                    else:
                        board[i].append(c)
                i += 1
        return board
    except Exception as e:
        tk.messagebox.showerror(title="Error", message="Error: " + str(e))

def is_board_rectangular(board):
    line_length = len(board[0])
    valid = True
    for i in range(len(board)):
        if len(board[i]) != line_length:
            valid = False
    return valid

def save_board():
    if pause:
        f_name = f_name_input.get() + ".txt"
        available = check_file_name(f_name)

        if available:
            write_file(f_name)
            f_name_input.set("")
            dd_cbox["values"] = get_board_file_names()
        else:
            ow_msg = "A file with this name already exists. Do you want to overwrite the existing file?"
            overwrite = tk.messagebox.askyesno(title="Warning", message=ow_msg)
            if overwrite:
                write_file(f_name)
                f_name_input.set("")
                dd_cbox["values"] = get_board_file_names()

def check_file_name(name):
    for f in get_board_file_names():
        if f == name:
            return False
    return True

def write_file(name):
    try:
        with open(BOARDS_DIR + name, "w") as f:
            for i in range(board_h):
                for j in range(board_w):
                    f.write(game_board[i][j])
                f.write("\n")
    except OSError:
        print("Error: Invalid file name.")
    except Exception as e:
        print("Error: " + e)

# ---------------------------------------------------------------------------
# Initialise the starting state:
game_board = random_board()

# Set up the window GUI:
root = tk.Tk()
root.title("Conway's Game of Life")
root.iconbitmap("game-of-life.ico")
root.resizable(0, 0)

canvas = tk.Canvas(root, bd=MARGIN, bg=BG_COLOR, width=1, height=1)
update_canvas_size()
canvas.pack()
redraw_board()

# Set up the menu GUI:
menu_frame = tk.Frame(root, bg=MENU_COLOR)
frame_x = (board_w * CELL_H) + (GAP * (board_w - 1)) + (MARGIN * 2)
frame_y = MARGIN
menu_frame.place(x=frame_x, y=frame_y, width=MENU_W, height=MENU_H)

# --- Define the y coord of menu rows:
# --- Spec label is on top (row 0) by default.
row_1 = LB_H + (MENU_GAP_Y * 1)
row_2 = LB_H + (MENU_GAP_Y * 2) + (BT_H * 1)
row_3 = LB_H + (MENU_GAP_Y * 3) + (BT_H * 2)
row_4 = LB_H + (MENU_GAP_Y * 4) + (BT_H * 3)
row_5 = LB_H + (MENU_GAP_Y * 5) + (BT_H * 4)

# Menu items
# --- Specs label
spec_lb = tk.Label(menu_frame, text="", bg=MENU_COLOR)
update_specs()
spec_lb.place(relx=0.05)

# --- Key buttons
pause_bt = tk.Button(menu_frame, text="Pause", command=toggle_pause, relief="sunken", bg="tomato", bd=3)
pause_bt.place(relx=0.05, y=row_1, relwidth=0.29)

wrap_bt = tk.Button(menu_frame, text="Wrap Around", command=toggle_wrap, relief="sunken", bg="sky blue", bd=3)
wrap_bt.place(relx=0.36, y=row_1, relwidth=0.29)

reset_bt = tk.Button(menu_frame, text="Reset", command=reset_board, bd=3)
reset_bt.place(relx=0.67, y=row_1, relwidth=0.29)

# --- Resizing menu
h_lb = tk.Label(menu_frame, text="H:", bg=MENU_COLOR)
h_lb.place(y=row_2+10, relx=0.05)

h_input = tk.StringVar()
h_entry = tk.Entry(menu_frame, textvariable=h_input, bd=3)
h_entry.place(relx=0.11, y=row_2, relwidth=0.12, height=BT_H)

w_lb = tk.Label(menu_frame, text="W:", bg=MENU_COLOR)
w_lb.place(y=row_2+10, relx=0.29)

w_input = tk.StringVar()
w_entry = tk.Entry(menu_frame, textvariable=w_input, bd=3)
w_entry.place(relx=0.36, y=row_2, relwidth=0.12, height=BT_H)

resize_bt = tk.Button(menu_frame, text="Resize", command=resize, bd=3)
resize_bt.place(relx=0.05, y=row_3, relwidth=0.44)

# --- Probability setting menu
prob_lb = tk.Label(menu_frame, text="Probability:", justify=tk.CENTER, bg=MENU_COLOR)
prob_lb.place(y=row_2+10, relx=0.57)

prob_input = tk.StringVar()
prob_entry = tk.Entry(menu_frame, textvariable=prob_input, bd=3)
prob_entry.place(relx=0.83, y=row_2, relwidth=0.12, height=BT_H)

change_prob_bt = tk.Button(menu_frame, text="Change Probability", command=change_probability, bd=3)
change_prob_bt.place(relx=0.52, y=row_3, relwidth=0.44)

# --- Load file menu
dd_options = get_board_file_names()
dd_selection = tk.StringVar()
dd_selection.set("Select file")
dd_cbox = tk.ttk.Combobox(menu_frame, values=dd_options, textvariable=dd_selection, state="readonly")
dd_cbox.place(relx=0.05, y=row_4, relwidth=0.6, height=BT_H+3)

# --- Combobox callback below is just for visual appearance. On Combobox selection
# --- it moves the focus form the Combobox to the root window to remove the blue
# --- highlight from the Combobox.
def dd_callback(event):
    root.focus()
dd_cbox.bind("<<ComboboxSelected>>", dd_callback)

load_bt = tk.Button(menu_frame, text="Load", command=load_board, bd=3)
load_bt.place(relx=0.67, y=row_4, relwidth=0.29)

# --- Save file menu
f_name_input = tk.StringVar()
f_name_entry = tk.Entry(menu_frame, textvariable=f_name_input, bd=3, justify=tk.RIGHT)
f_name_entry.place(relx=0.05, y=row_5, relwidth=0.49, height=BT_H)

ext_lb = tk.Label(menu_frame, text=".txt", bg=MENU_COLOR)
ext_lb.place(y=row_5+10, relx=0.55)

save_bt = tk.Button(menu_frame, text="Save", command=save_board, bd=3)
save_bt.place(relx=0.67, y=row_5, relwidth=0.29)

root.after(TICK_TIME, board_tick)
root.mainloop()




