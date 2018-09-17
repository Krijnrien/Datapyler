# region imports
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import sqlite3
import datetime

import pandas

# endregion

# This code was designed around one table database implementation. Thus all queries point to below's table name
# variable. Queries requires changing to accommodate for multiple tables.
table_name = ""


class CheckBar(tk.Frame):
    def __init__(self, parent=None, picks=None):
        tk.Frame.__init__(self, parent)
        if picks is None:
            picks = []
        self.vars = []
        for pick in picks:
            self.var = tk.StringVar()
            chk = tk.Checkbutton(parent, text=pick, onvalue=pick, offvalue="NULL", variable=self.var)
            chk.setvar(pick)
            chk.deselect()
            chk.pack(anchor=tk.W, expand=tk.YES)
            self.vars.append(self.var)

    def state(self):
        return map((lambda var: var.get()), self.vars)


# region database class & initialization
class Database:
    def __init__(self, name=":memory:"):
        self.conn = None
        self.cursor = None

        if name:
            self.open(name)

    def open(self, name):
        try:
            self.conn = sqlite3.connect(name)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print("Error connecting to database! " + str(e))

    def close(self):
        if self.conn:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def select(self, table, columns, limit=None):
        query = "SELECT {0} from {1};".format(columns, table)
        self.cursor.execute(query)

        # fetch data
        rows = self.cursor.fetchall()
        return rows[len(rows) - limit if limit else 0:]

    def select_one(self, table, columns):
        query = "SELECT {0} from {1};".format(columns, table)
        self.cursor.execute(query)

        # fetch data
        row = self.cursor.fetchone()
        return row

    def select_last(self, table, columns):
        return self.select(table, columns, limit=1)[0]

    def select_all(self, table):
        print(table)
        query = "SELECT * from {0}".format(table)
        self.cursor.execute(query)

        # fetch data
        rows = self.cursor.fetchall()
        return rows

    def select_distinct_column(self, column, table):
        query = "SELECT DISTINCT {0} FROM {1}".format(column, table)
        self.cursor.execute(query)

        # fetch data
        rows = self.cursor.fetchall()
        return rows

    def select_all_column_names(self, table):
        query = "SELECT * FROM {0}".format(table)
        column_names = [description[0] for description in self.cursor.execute(query).description]
        return column_names

    @staticmethod
    def to_csv(data, file_name="output"):
        with open(file_name + str(datetime.datetime.now()) + ".csv", 'a') as file:
            file.write(",".join([str(j) for i in data for j in i]))

    def insert(self, table, columns, data):
        query = "INSERT INTO {0} ({1}) VALUES ({2});".format(table, columns, data)
        self.cursor.execute(query)

    def raw_query(self, sql):
        self.cursor.execute(sql)

    def load_csv(self, file):
        df = pandas.read_csv(file.name, encoding="ISO-8859-1")
        global table_name
        table_name = os.path.splitext(os.path.basename(file.name))[0]
        df.to_sql(table_name, self.conn, if_exists='append', index=False)


db = Database()


# endregion

# region button event handler

def add_dataset_command():
    open_csv_file_dialog()


# endregion


def open_csv_file_dialog():
    file = filedialog.askopenfilename(initialdir="./", title="Select file", filetypes=(("CSV Files", "*.csv"),))
    try:
        with open(file, 'r') as open_file:
            db.load_csv(open_file)
            popup_select_columns()
    except FileNotFoundError:
        print("No file exists")


def popup_select_columns():
    frame = tk.Toplevel(width=300)
    frame.grid()
    canvas = tk.Canvas(frame, scrollregion=(0, 0, 900, 900))
    vbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
    vbar.pack(side=tk.RIGHT, fill=tk.Y)
    vbar.config(command=canvas.yview)
    canvas.config(yscrollcommand=vbar.set)

    select_options_label = tk.Label(canvas, text="Select columns to normalize values.")
    select_options_label.pack()

    def all_states():
        create_notebook_tabs(list(state()))
        canvas.destroy()

    def state():
        return map((lambda var: var.get()), vars)

    tk.Button(canvas, text='Ok', command=all_states).pack(side=tk.TOP)

    column_names = db.select_all_column_names(table_name)

    # check_buttons_state_list = CheckBar(canvas, column_names)
    # check_buttons_state_list.pack(side=tk.TOP, fill=tk.X)
    # check_buttons_state_list.config(relief=tk.GROOVE, bd=2)

    vars = []
    #for pick in column_names:
        #var = tk.StringVar()
        #tk.Button(canvas, text='Ok', command=all_states).pack(side=tk.TOP)
        #tk.Checkbutton(canvas, text=pick, onvalue=pick, offvalue="NULL").pack()
        #chk.setvar(pick)
        #chk.deselect()
        #chk.pack(anchor=tk.W)
        #vars.append(var)

    canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)


def create_notebook_tabs(check_buttons_state_list):
    for column_name in check_buttons_state_list:
        if column_name != "NULL":
            print(column_name)
            tab = tk.Frame(column_tabs_notebook)
            tab.setvar(name="column_name", value=column_name)

            column_row_frame = tk.Frame(tab)
            column_row_frame.pack()

            distinct_rows = db.select_distinct_column(column_name, table_name)

            print(distinct_rows)

            # for distinct in distinct_rows:
            #     variable = StringVar()
            #     variable.set(distinct)
            #     distinct_value_option_menu = OptionMenu(tab, variable, distinct_rows)
            #     distinct_value_option_menu.pack()

            column_tabs_notebook.add(tab, text=column_name)
            column_tabs_notebook.pack(expand=1, fill="both")


def do_nothing():
    print("nothing happening")


# region GUI
# ** Root frame **
root_frame = tk.Tk(screenName="Datapyler", baseName="Datapyler")
root_frame.title("Datapyler")

# ** Menu bar **
menu_bar = tk.Menu(root_frame)
root_frame.config(menu=menu_bar)
root_frame.minsize(height=400, width=600)

file_menu_option = tk.Menu(menu_bar)
menu_bar.add_cascade(label="File", menu=file_menu_option)
file_menu_option.add_command(label="Add dataset", command=add_dataset_command)
file_menu_option.add_command(label="Export", command=do_nothing)
file_menu_option.add_command(label="Exit", command=do_nothing)

view_menu_option = tk.Menu(menu_bar)
menu_bar.add_cascade(label="View", menu=view_menu_option)
view_menu_option.add_command(label="Log", command=do_nothing)
view_menu_option.add_command(label="All Queries", command=do_nothing)

# ** Notebook tabs **
column_tabs_notebook = ttk.Notebook(root_frame)

# ** Status bar **
status_bar_label = tk.Label(root_frame, text="Done...", bd=1, relief=tk.SUNKEN, anchor=tk.W)
status_bar_label.pack(side=tk.BOTTOM, fill=tk.X)

# Keeps UI active. This program executes like a script. When it's done it would exit, the mainloop() prevents closing.
root_frame.mainloop()
# endregion
