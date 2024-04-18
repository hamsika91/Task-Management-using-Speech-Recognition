import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry  # Import the DateEntry widget
import json
import speech
import pymysql
from speech import *
import threading

# database connection
connection = pymysql.connect(host="localhost", port=3306, user="root", passwd="", database="speech")
cursor = connection.cursor()
class TodoListApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Todo List App")
        self.geometry("400x500")
   
        

        # Create listbox to display added tasks at the top
        self.task_list = tk.Listbox(self, font=("TkDefaultFont", 16), height=10, width=10, selectmode=tk.NONE , )
        self.task_list.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Create input field for adding tasks just below the listbox
        self.task_input = ttk.Entry(self, font=("Helvetica", 14), width=20)
        self.task_input.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        
        # Apply custom style to the entry widget
        self.task_input.configure(style="Custom.TEntry")

        # Create calendar for selecting the date
        self.date_picker = DateEntry(self, width=12, borderwidth=2)
        self.date_picker.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")

        # Set placeholder for input field
        self.task_input.insert(0, "Enter your task here")

        # Bind event to clear placeholder when input field is clicked
        self.task_input.bind("<FocusIn>", self.clear_placeholder)
        # Bind event to restore placeholder when input field loses focus
        self.task_input.bind("<FocusOut>", self.restore_placeholder)

        # Create button for adding tasks on the right side of the entry
        ttk.Button(self, text="Add", command=self.add_task).grid(row=1, column=2, padx=5, pady=5, sticky="nsew")

        # Create buttons for marking tasks as done or deleting them
        ttk.Button(self, text="Done", style="success.TButton", command=self.mark_done).grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        ttk.Button(self, text="Show", style="danger.TButton", command=self.show).grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
        
        # Create button for displaying task statistics
        ttk.Button(self, text="Voice", style="info.TButton", command=self.voice).grid(row=3, column=0, columnspan=3, pady=10, sticky="nsew")
        
        # Configure row and column weights to make the widgets expand and center
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.load_tasks()

    def view_stats(self):
        done_count = 0
        total_count = self.task_list.size()
        for i in range(total_count):
            if self.task_list.itemcget(i, "fg") == "green":
                done_count += 1
        messagebox.showinfo("Task Statistics", f"Total tasks: {total_count}\nCompleted tasks: {done_count}")

    def add_task(self):
        task = self.task_input.get()
        date_task = self.date_picker.get_date()
        print(date_task)
        time_task="6pm"
        
        if task != "Enter your task here":
            self.task_list.insert(tk.END, f"{date_task}: {task}")
            self.task_list.itemconfig(tk.END, fg="orange")
            self.task_input.delete(0, tk.END)
        def database_op():
            insert_sql = "INSERT INTO task_data values('{}','{}','{}')".format(task, date_task, time_task)
            cursor.execute(insert_sql)
            connection.commit()
        threading.Thread(target=database_op).start()

        

    def mark_done(self):
        task_index = self.task_list.curselection()
        
        if task_index:
            text = self.task_list.get(task_index)
            #text=str(text)
            #print("text",text)
            insert_sql="delete from task_data where task=%s"
            cursor.execute(insert_sql, (text,))
            connection.commit()
            self.task_list.delete(task_index)
           # self.save_tasks()

    
    def show(self):
        self.task_list.delete(0, tk.END)
        selected_date = self.date_picker.get_date()
        print(selected_date)
        def database_op():
            insert_sql = "SELECT task  FROM task_data WHERE date_task = %s"
            cursor.execute(insert_sql, (selected_date,))
            result = cursor.fetchall()
            for data in result :
                task_string = ', '.join(map(str, data))  
                print(task_string)
                self.task_list.insert(tk.END,task_string)
        threading.Thread(target=database_op).start()
        
    
    def clear_placeholder(self, event):
        if self.task_input.get() == "Enter your task here":
            self.task_input.delete(0, tk.END)

    def restore_placeholder(self, event):
        if self.task_input.get() == "":
            self.task_input.insert(0, "Enter your task here")
    def load_tasks(self):
        try:
            with open("tasks.json", "r") as f:
                data = json.load(f)
                for task in data:
                    self.task_list.insert(tk.END, task["text"])
                    self.task_list.itemconfig(tk.END, fg=task["color"])
        except FileNotFoundError:
            pass
   
    
    def voice(self):
        def voice_operation():
            speech.transcribe_audio()
        threading.Thread(target=voice_operation).start()

app = TodoListApp()
app.mainloop()
cursor.close()
connection.close()
