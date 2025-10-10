import tkinter as tk
import threading
import time
from datetime import datetime
from tkinter import messagebox
import json
import subprocess
# import currentWattTime as wt
import csv
import os


current_temperature = 55.0
tmin = 51.0
tmax = 59.0
coolth = 35.0
econ = 48.0
tolerance_time = 40 #min 
current_mode = "Rule-Based" 
current_charge_setpoint = 70.0
global realtime_charge
global realtime_MOER
global realtime 
realtime = datetime.now()

# realtime_MOER = wt.get_current_wattT()
realtime_charge = 0.0

tasks = []


def load_tasks_from_csv(file_name='weeklySchedule.csv'):
    tasks = []
    try:
        with open(file_name, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                task = {
                    'description': row['Description'],
                    'start_date': datetime.strptime(row['StartDate'], "%m/%d/%Y"),
                    'time': row['StartTime'],
                    'endTime': row['EndTime'],
                    'is_repeat': row['IsRepeat'] == 'True',
                    # 'days': row['DaysOfWeek'].split(', ') if row['DaysOfWeek'] else [],
                    'days': [day.strip() for day in row['DaysOfWeek'].split(',')] if row['DaysOfWeek'] else [],
                    'last_executed': None
                }
                tasks.append(task)
    except FileNotFoundError:
        print("No schedule file found, starting with an empty task list.")
    return tasks

def save_tasks_to_csv(tasks, file_name='weeklySchedule.csv'):
    try:
        print("Saving the following tasks to CSV:")
        for task in tasks:
            print(task)  # Print each task to verify the data before saving

        with open(file_name, mode='w', newline='') as file:
            fieldnames = ['Description', 'StartDate', 'StartTime', 'EndTime', 'IsRepeat', 'DaysOfWeek']
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            # Write the header
            writer.writeheader()

            # Write each task back to the CSV
            for task in tasks:
                writer.writerow({
                    'Description': task['description'],
                    'StartDate': task['start_date'].strftime("%m/%d/%Y"),
                    'StartTime': task['time'],
                    'EndTime': task['endTime'],
                    'IsRepeat': 'True' if task['is_repeat'] else 'False',
                    'DaysOfWeek': ', '.join(task['days'])
                })
    except Exception as e:
        print(f"Error saving tasks to CSV: {e}")

# Add a function to read walking steps from a JSON file
def update_realtime_charge():
    global realtime_charge
    while True:
        try:
            with open('charge_data.json', 'r') as file:
                data = json.load(file)
                realtime_charge = data['charge']  # Simulate charge being walking steps
        except FileNotFoundError:
            realtime_charge = 0.0  # If file doesn't exist, set to 0
        time.sleep(1)

def fetch_and_update_charge_label(realtime_charge_label):
    # Fetch the latest steps and update the label


    realtime_charge_label.config(text=f"Current Charge: {realtime_charge} %")
    # Schedule the next update after 1000 milliseconds (1 second)
    realtime_charge_label.after(1000, fetch_and_update_charge_label, realtime_charge_label)
        
# def fetch_and_update_MOER_label(current_MOER_label):
#     realtime_MOER = wt.get_current_wattT()
#     current_MOER_label.config(text=f"Current MOER: {realtime_MOER} lbs CO2/MWh at {datetime.now()}")
#     current_MOER_label.after(60000, fetch_and_update_MOER_label, current_MOER_label)


     
def open_temp_setting():
    def reset_temperature():
        global current_temperature
        global tmin
        global tmax, coolth, econ, tolerance_time
        try:
            # Update current temperature
            if temp_entry.get():
                new_temp = float(temp_entry.get())
                current_temperature = new_temp
                current_temp_label.config(text=f"Current Temperature Setpoint: {current_temperature}°F")
            
            # Update Tmin
            if tmin_entry.get():
                new_tmin = float(tmin_entry.get())
                tmin = new_tmin
                current_tmin_label.config(text=f"Current Tmin: {tmin}°F")

            # Update Tmax
            if tmax_entry.get():
                new_tmax = float(tmax_entry.get())
                tmax = new_tmax
                current_tmax_label.config(text=f"Current Tmax: {tmax}°F")

            # Update Coolth
            if coolth_entry.get():
                new_coolth = float(coolth_entry.get())
                coolth = new_coolth
                current_coolth_label.config(text=f"Current Coolth Setpoint : {coolth}°F")

            # Update Econ
            if econ_entry.get():
                new_econ = float(econ_entry.get())
                econ = new_econ
                current_econ_label.config(text=f"Current Econ Setpoint: {econ}°F")

            # Update tolerance Time 
            if tolerance_entry.get():
                new_tolerance = float(tolerance_entry.get())
                tolerance_time = new_tolerance
                current_tolerance_label.config(text=f"Current Coolth/Econ Tolerance Time: {tolerance_time}min")

            # Clear all entry fields
            temp_entry.delete(0, tk.END)
            tmin_entry.delete(0, tk.END)
            tmax_entry.delete(0, tk.END)
            coolth_entry.delete(0, tk.END)
            econ_entry.delete(0, tk.END)
            tolerance_entry.delete(0, tk.END)

            messagebox.showinfo("Success", "Temperature settings updated successfully.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number.")

    temp_window = tk.Toplevel()
    temp_window.title("Temperature Settings")
    temp_window.geometry("300x600")

    # Current Temperature
    current_temp_label = tk.Label(temp_window, text=f"Current Temperature Setpoint: {current_temperature}°F")
    current_temp_label.pack(pady=5)
    temp_label = tk.Label(temp_window, text="Reset Current Temperature:")
    temp_label.pack()
    temp_entry = tk.Entry(temp_window)
    temp_entry.pack(pady=5)

    # Current Tmin
    current_tmin_label = tk.Label(temp_window, text=f"Current Tmin: {tmin}°F")
    current_tmin_label.pack(pady=5)
    tmin_label = tk.Label(temp_window, text="Reset Tmin:")
    tmin_label.pack()
    tmin_entry = tk.Entry(temp_window)
    tmin_entry.pack(pady=5)

    # Current Tmax
    current_tmax_label = tk.Label(temp_window, text=f"Current Tmax: {tmax}°F")
    current_tmax_label.pack(pady=5)
    tmax_label = tk.Label(temp_window, text="Reset Tmax:")
    tmax_label.pack()
    tmax_entry = tk.Entry(temp_window)
    tmax_entry.pack(pady=5)

    # Current coolth
    current_coolth_label = tk.Label(temp_window, text=f"Current Coolth Setpoint: {coolth}°F")
    current_coolth_label.pack(pady=5)
    coolth_label = tk.Label(temp_window, text="Reset Coolth Setpoint:")
    coolth_label.pack()
    coolth_entry = tk.Entry(temp_window)
    coolth_entry.pack(pady=5)

    # Current econ
    current_econ_label = tk.Label(temp_window, text=f"Current Econ Setpoint: {econ}°F")
    current_econ_label.pack(pady=5)
    econ_label = tk.Label(temp_window, text="Reset Econ Setpoint:")
    econ_label.pack()
    econ_entry = tk.Entry(temp_window)
    econ_entry.pack(pady=5)

    # Current tolerance 
    current_tolerance_label = tk.Label(temp_window, text=f"Current Coolth/Econ Tolerance Time: {tolerance_time} min")
    current_tolerance_label.pack(pady=5)
    tolerance_label = tk.Label(temp_window, text="Reset To:")
    tolerance_label.pack()
    tolerance_entry = tk.Entry(temp_window)
    tolerance_entry.pack(pady=5)



    # Reset Button
    reset_temp_button = tk.Button(temp_window, text="Save", command=reset_temperature)
    reset_temp_button.pack(pady=10)

def open_charging_setting():
    def reset_charge():
        global current_charge_setpoint
        global realtime_charge
        try:
            new_charge = float(charge_entry.get())
            current_charge_setpoint= new_charge
            # Update the displayed current temperature
            current_charge_label.config(text=f"Current Charge Setpoint: {current_charge_setpoint}%")
            # Clear the entry field
            charge_entry.delete(0, tk.END)
            messagebox.showinfo("Success", f"Charge reset to {current_charge_setpoint}%.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number.")

    charge_window = tk.Toplevel()
    charge_window.title("Charging Settings")
    charge_window.geometry("300x300")

    # Current Charge Label
    current_charge_label = tk.Label(charge_window, text=f"Current Charge Setpoint: {current_charge_setpoint}%")
    current_charge_label.pack(pady=10)

    # Realtime charge
    # realtime_charge_lable = tk.Label(charge_window, text=f"Current Charge: {realtime_charge}%")
    # realtime_charge_lable.pack(pady=10)
    # fetch_and_update_charge_label(realtime_charge_lable)

    # Reset
    charge_label = tk.Label(charge_window, text="Reset to: ")
    charge_label.pack(pady=10)

    # Entry to input new charge
    charge_entry = tk.Entry(charge_window)
    charge_entry.pack(pady=5)

    # Reset Temperature Button
    reset_charge_button = tk.Button(charge_window, text="Save", command=reset_charge)
    reset_charge_button.pack(pady=10) 


def manage_delivery():
    global tasks  # Make tasks accessible outside this function
    global task_listbox

    def add_task():
        task_desc = task_entry.get().strip()
        date_str = date_entry.get().strip()
        time_str = time_entry.get().strip()
        time_str2 = time_entry2.get().strip()
        is_repeat = repeat_var.get()
        selected_days = [day for day in days_of_week if day_vars[day].get()]

        if not task_desc:
            messagebox.showwarning("Input Error", "Please enter a task description.")
            return

        if not date_str:
            messagebox.showwarning("Input Error", "Please enter a start date.")
            return
        # Validate date format
        try:
            start_date = datetime.strptime(date_str, "%m/%d/%Y")
        except ValueError:
            messagebox.showerror("Invalid Date Format", "Please enter the date in MM/DD/YYYY format.")
            return

        if not time_str:
            messagebox.showwarning("Input Error", "Please enter a start time.")
            return

        if not time_str2:
            messagebox.showwarning("Input Error", "Please enter an end time.")
            return

        # Validate time formats
        try:
            datetime.strptime(time_str, "%H:%M")
            datetime.strptime(time_str2, "%H:%M")
        except ValueError:
            messagebox.showerror("Invalid Time Format", "Please enter the time in HH:MM (24-hour) format.")
            return

        if is_repeat and not selected_days:
            messagebox.showwarning("Input Error", "Please select at least one day for the repeating task.")
            return

        # Create a task dictionary
        task = {
            'description': task_desc,
            'is_repeat': is_repeat,
            'start_date': start_date,
            'time': time_str,
            'endTime': time_str2,
            'days': selected_days,
            'last_executed': None  # Initialize last executed time
        }

        tasks.append(task)
        update_task_list()
        # Clear the entry fields
        task_entry.delete(0, tk.END)
        date_entry.delete(0, tk.END)
        time_entry.delete(0, tk.END)
        time_entry2.delete(0, tk.END)
        repeat_var.set(False)
        for day in days_of_week:
            day_vars[day].set(False)

    def delete_task():
        selected_task_indices = task_listbox.curselection()
        if selected_task_indices:
            for index in selected_task_indices[::-1]:
                del tasks[index]
            update_task_list()
        else:
            messagebox.showwarning("Selection Error", "Please select a task to delete.")

    def update_task_list():
        task_listbox.delete(0, tk.END)
        for idx, task in enumerate(tasks):
            days_str = ', '.join(task['days']) if task['days'] else 'No days selected'
            repeat_str = 'Repeats' if task['is_repeat'] else 'One-time'
            task_str = f"{task['start_date'].strftime('%m/%d/%Y')} {task['time']} - {task['endTime']} : {task['description']} [{repeat_str} on {days_str}]"

            # Add to main task list
            task_listbox.insert(tk.END, task_str)

    todo_window = tk.Toplevel()
    todo_window.title("Delivery Manager")

    # Create a canvas and scrollbar
    canvas = tk.Canvas(todo_window, width=450, height=800)
    scrollbar = tk.Scrollbar(todo_window, orient=tk.VERTICAL, command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Add widgets to the scrollable_frame instead of todo_window
    todo_label = tk.Label(scrollable_frame, text="All Tasks:")
    todo_label.pack(pady=10)

    all_tasks_frame = tk.Frame(scrollable_frame)
    all_tasks_frame.pack()

    task_scrollbar = tk.Scrollbar(all_tasks_frame, orient=tk.VERTICAL)
    task_listbox = tk.Listbox(all_tasks_frame, width=50, height=15, yscrollcommand=task_scrollbar.set)
    task_scrollbar.config(command=task_listbox.yview)
    task_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    task_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    task_label = tk.Label(scrollable_frame, text="Task Description:")
    task_label.pack(pady=5)
    task_entry = tk.Entry(scrollable_frame, width=40)
    task_entry.pack(pady=5)

    date_label = tk.Label(scrollable_frame, text="Start Date (MM/DD/YYYY):")
    date_label.pack(pady=5)
    date_entry = tk.Entry(scrollable_frame, width=20)
    date_entry.pack(pady=5)

    repeat_var = tk.BooleanVar()
    repeat_checkbox = tk.Checkbutton(scrollable_frame, text="Repeat Task", variable=repeat_var)
    repeat_checkbox.pack(pady=5)

    day_vars = {}
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    days_label = tk.Label(scrollable_frame, text="Repeat on Days:")
    days_label.pack(pady=5)
    for day in days_of_week:
        day_vars[day] = tk.BooleanVar()
        day_checkbox = tk.Checkbutton(scrollable_frame, text=day, variable=day_vars[day])
        day_checkbox.pack(anchor='w')

    time_label = tk.Label(scrollable_frame, text="Start Time (HH:MM, 24-hour):")
    time_label.pack(pady=5)
    time_entry = tk.Entry(scrollable_frame, width=20)
    time_entry.pack(pady=5)

    time_label2 = tk.Label(scrollable_frame, text="End Time (HH:MM, 24-hour):")
    time_label2.pack(pady=5)
    time_entry2 = tk.Entry(scrollable_frame, width=20)
    time_entry2.pack(pady=5)

    add_task_button = tk.Button(scrollable_frame, text="Add Task", command=add_task)
    add_task_button.pack(pady=10)

    delete_task_button = tk.Button(scrollable_frame, text="Delete Selected Task(s)", command=delete_task)
    delete_task_button.pack(pady=5)

    update_task_list()


def view_today_schedules():
    global tasks  # Ensure we have access to the tasks list

    def update_today_tasks():
        today_task_listbox.delete(0, tk.END)
        for task in tasks:
            now = datetime.now()
            current_day = now.strftime('%A')  # e.g., 'Monday'
            current_date = now.date()
            task_date = task['start_date'].date()
            is_today = False

            if current_date >= task_date:
                if task['is_repeat']:
                    if current_day in task['days']:
                        is_today = True
                else:
                    if current_date == task_date:
                        is_today = True

            if is_today:
                days_str = ', '.join(task['days']) if task['days'] else 'No days selected'
                repeat_str = 'Repeats' if task['is_repeat'] else 'One-time'
                # Use today's date instead of the task's start date
                task_str = f"{current_date.strftime('%m/%d/%Y')} {task['time']} - {task['endTime']} : {task['description']} [{repeat_str}]"
                today_task_listbox.insert(tk.END, task_str)

        # Create a new window for today's tasks
    today_window = tk.Toplevel()
    today_window.title("Today's Delivery Schedules")
    today_window.geometry("450x300")

    # Label for Today's Tasks
    today_label = tk.Label(today_window, text="Today's Tasks:")
    today_label.pack(pady=10)

    # Frame for Today's Tasks Listbox and Scrollbar
    today_frame = tk.Frame(today_window)
    today_frame.pack()

    # Scrollbar for Today's Tasks
    today_scrollbar = tk.Scrollbar(today_frame, orient=tk.VERTICAL)
    today_task_listbox = tk.Listbox(today_frame, width=50, height=10, yscrollcommand=today_scrollbar.set)
    today_scrollbar.config(command=today_task_listbox.yview)
    today_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    today_task_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Populate today's tasks
    update_today_tasks()

# def open_moer_setting():

#     moer_window = tk.Toplevel()
#     moer_window.title("MOER")
#     moer_window.geometry("300x300")

#     current_MOER_label = tk.Label(moer_window, text=f"Current MOER: {realtime_MOER} lbs CO2/MWh at {datetime.now()}")
#     current_MOER_label.pack(pady=10)

#     fetch_and_update_MOER_label(current_MOER_label)

def open_mode_setting():
    def set_mode():
        global current_mode
        current_mode = mode_var.get()
        # Update the label to reflect the new mode
        current_mode_label.config(text=f"Current Mode: {current_mode}")
        messagebox.showinfo("Mode Updated", f"System mode updated to: {current_mode}")

    mode_window = tk.Toplevel()
    mode_window.title("System Mode")
    mode_window.geometry("300x200")

    # Current Mode Label
    current_mode_label = tk.Label(mode_window, text=f"Current Mode: {current_mode}")
    current_mode_label.pack(pady=10)

    # Instructions
    instruction_label = tk.Label(mode_window, text="Choose a system mode:")
    instruction_label.pack(pady=5)

    # Mode Selection Radiobuttons
    mode_var = tk.StringVar(value=current_mode)  # Bind variable to radiobuttons
    rule_based_button = tk.Radiobutton(mode_window, text="Rule-Based", variable=mode_var, value="Rule-Based")
    optimization_button = tk.Radiobutton(mode_window, text="Optimization", variable=mode_var, value="Optimization")

    rule_based_button.pack(anchor="w", padx=20)
    optimization_button.pack(anchor="w", padx=20)

    # Save Mode Button
    save_button = tk.Button(mode_window, text="Save", command=set_mode)
    save_button.pack(pady=20)

def run_main_gui():

    process = subprocess.Popen(["python", "draftCharger.py"])

    main_window = tk.Tk()
    main_window.title("EMS Settings Panel")
    main_window.geometry("300x250")


    # open_MOER_button = tk.Button(main_window, text="Current MOER", command=open_moer_setting)
    # open_MOER_button.pack(pady=10)

    open_mode_button = tk.Button(main_window, text="System Mode", command=open_mode_setting)
    open_mode_button.pack(pady=10)

    # Button to open Temperature Setting GUI
    open_temp_button = tk.Button(main_window, text="Temperature Settings", command=open_temp_setting)
    open_temp_button.pack(pady=10)

    # Button to open Charging Setting GUI
    open_temp_button = tk.Button(main_window, text="Charging Settings", command=open_charging_setting)
    open_temp_button.pack(pady=10)

    # Button to add delivery schedule 
    open_delivery_button = tk.Button(main_window, text="Manage Delivery Schedules", command=manage_delivery)
    open_delivery_button.pack(pady=10) 

    # New Button to view today's delivery schedules
    view_today_button = tk.Button(main_window, text="View Today's Delivery Schedules", command=view_today_schedules)
    view_today_button.pack(pady=10)

    def on_closing():
        process.kill()
        print("subprocess killed")
        main_window.destroy()

    main_window.protocol("WM_DELETE_WINDOW", on_closing)

    main_window.mainloop()


def main_script():
    global tasks  # Ensure we can access the tasks list
    while True:
        now = datetime.now()
        current_day = now.strftime('%A')  # e.g., 'Monday'
        current_date = now.date()
        current_time = now.strftime('%H:%M')
        save_to_json()

        for task in tasks.copy():
            task_date = task['start_date'].date()

            if current_date >= task_date:
                if task['is_repeat']:
                    if current_day in task['days']:
                        if current_time == task['time']:
                            last_executed = task.get('last_executed')
                            if last_executed != current_date:
                                print(f"Executing repeating task: {task['description']}")
                                # Here, you can add the code to perform the actual task
                                task['last_executed'] = current_date
                else:
                    # One-time task
                    task_datetime = datetime.combine(task_date, datetime.strptime(task['time'], "%H:%M").time())
                    if now >= task_datetime and now <= task_datetime.replace(second=59):
                        print(f"Executing one-time task: {task['description']}")
                        # Here, you can add the code to perform the actual task
                        tasks.remove(task)
                        print(f"One-time task '{task['description']}' executed and removed from the list.")
        

        time.sleep(5)

def save_to_json():
    global current_charge_setpoint, current_temperature, tmin, tmax, coolth, econ, tolerance_time, current_mode
    config = {
        "current_temperature": current_temperature,
        "tmin": tmin,
        "tmax": tmax,
        "coolth": coolth,
        "econ": econ,
        "tolerance_time": tolerance_time,
        "current_mode": current_mode,
        "current_charge_setpoint": current_charge_setpoint
    }
    # Define the file path
    file_path = "config.json"
    
    if not os.path.exists(file_path):
        print(f"{file_path} does not exist. Creating a new file.")
    
    try:
        # Save to JSON file
        with open(file_path, "w") as json_file:
            json.dump(config, json_file, indent=4)
        # print(f"Configuration saved to {file_path}.")
    except Exception as e:
        print(f"Error saving configuration: {e}")
    
def ui_main():
    global tasks
    tasks = load_tasks_from_csv()
    # Start the main script thread
    main_thread = threading.Thread(target=main_script)
    main_thread.daemon = True  # Daemonize thread to exit when main thread exits
    main_thread.start()

    # Run the main GUI in the main thread
    run_main_gui()
    save_tasks_to_csv(tasks)


if __name__ == "__main__":
    ui_main()
