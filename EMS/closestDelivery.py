import csv
from datetime import datetime, timedelta
import pytz
import requests
import json 

filepath = 'weeklySchedule.csv'
DETROIT_TZ = pytz.timezone("America/Detroit")
UTC_TZ = pytz.UTC

upcoming_delivery_time = None

def read_schedule_from_csv(file_path):
    """
    Reads the delivery schedule from a CSV file.
    
    Args:
        file_path (str): Path to the CSV file.
        
    Returns:
        list: A list of dictionaries representing delivery tasks.
    """
    schedule = []
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            start_time = row['StartTime'].strip() if row['StartTime'] else None
            if start_time is None:
                print(f"Skipping row due to missing StartTime: {row}")
                continue
            
            try:
                # Convert data into appropriate types
                schedule.append({
                    'description': row['Description'],
                    'start_date': datetime.strptime(row['StartDate'], '%m/%d/%Y').date(),
                    'start_time': start_time,
                    'end_time': row['EndTime'].strip() if row['EndTime'] else None,
                    'is_repeat': row['IsRepeat'].strip().lower() == 'true',
                    'days_of_week': [day.strip() for day in row['DaysOfWeek'].split(',')] if row['DaysOfWeek'] else []
                })
            except ValueError as e:
                print(f"Skipping row due to invalid data format: {row}")
                print(f"Error: {e}")
                continue
    return schedule

def get_next_delivery(schedule, current_time):
    """
    Find the next delivery task based on the current time.
    
    Args:
        schedule (list): List of delivery tasks.
        current_time (datetime): Current time in Detroit timezone.
        
    Returns:
        dict: The next delivery task.
        datetime: The start time of the next delivery.
    """
    next_delivery = None
    min_time_difference = timedelta.max
    next_delivery = None

    for task in schedule:
        try:
            # Parse the start_time
            start_time = datetime.strptime(task['start_time'].strip(), '%H:%M').time()
        except ValueError as e:
            print(f"Skipping task due to invalid start_time format: {task}")
            continue

        # Calculate task_datetime for one-time and repeating tasks
        if task['is_repeat']:
            for i in range(7):  # Look up to a week ahead
                candidate_date = current_time + timedelta(days=i)
                candidate_day = candidate_date.strftime('%A')  # Day name

                if candidate_day in task['days_of_week']:
                    # Combine candidate date and task start_time
               
                    task_datetime = datetime.combine(candidate_date.date(), start_time, tzinfo=DETROIT_TZ)
                    # Check if it's today's task and still in the future
                    if i == 0 and task_datetime > current_time:
                        break
                    # Otherwise, use the task from a future date
                    elif i > 0:
                        break
        else:
            # One-time task
            task_datetime = datetime.combine(task['start_date'], start_time, tzinfo=DETROIT_TZ)
        
        # Check if the task is in the future and closer than the current closest
        if task_datetime > current_time:
            time_difference = task_datetime - current_time
            if time_difference < min_time_difference:
                min_time_difference = time_difference
                next_delivery = task
                next_delivery_time = task_datetime

    
    global upcoming_delivery_time 
    upcoming_delivery_time = next_delivery_time       
    return next_delivery, next_delivery_time, min_time_difference if next_delivery else None



if __name__ == "__main__":    
    schedule = read_schedule_from_csv(filepath)
    current_time = datetime.now(DETROIT_TZ)
    # Find the next delivery
    next_delivery, next_delivery_time, min_time_difference = get_next_delivery(schedule, current_time)
    print(f"next delivery task is: {next_delivery['description']}\n", f"start_time: {next_delivery_time}\n", f"time before depature: {min_time_difference}")
 
    