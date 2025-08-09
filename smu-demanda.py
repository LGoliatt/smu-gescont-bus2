import pandas as pd
import os
from datetime import datetime

# Define the directory containing CSV files
data_dir = 'data_stops/'

import pandas as pd
import os
from datetime import datetime

def calculate_boarding_by_month(data_dir='data_stops/'):
    """
    Calculate the total boarding by month from CSV files in the specified directory.
    
    Parameters:
    data_dir (str): Directory containing CSV files with columns routeshortname, routelongname,
                    stopid, departuretime, stopsequence, boarding, landing, occupation,
                    day, stop_lon, stop_lat, stopname
    
    Returns:
    dict: Dictionary with month-year (YYYY-MM) as keys and total boarding as values
    """
    # Initialize a dictionary to store boarding sums by month
    boarding_by_month = {}
    
    # Iterate through all CSV files in the directory
    for filename in os.listdir(data_dir):
        if filename.endswith('.csv'):
            file_path = os.path.join(data_dir, filename)
            
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Convert 'day' column to datetime
            df['day'] = pd.to_datetime(df['day'])
            
            # Extract month-year as a string (e.g., '2025-08')
            df['month_year'] = df['day'].dt.strftime('%Y-%m')
            
            # Group by month-year and sum the 'boarding' column
            monthly_boarding = df.groupby('month_year')['boarding'].sum()
            
            # Update the boarding_by_month dictionary
            for month, boarding in monthly_boarding.items():
                if month in boarding_by_month:
                    boarding_by_month[month] += boarding
                else:
                    boarding_by_month[month] = boarding
    
    # Sort the results by month-year
    sorted_boarding = dict(sorted(boarding_by_month.items()))
    
    # Print the results
    for month, total_boarding in sorted_boarding.items():
        print(f"Month: {month}, Total Boarding: {total_boarding}")
    
    return sorted_boarding



def calculate_hourly_boarding_by_day_of_week(data_dir='data_stops/'):
    """
    Calculate the hourly average of boarding by day of the week from CSV files.
    
    Parameters:
    data_dir (str): Directory containing CSV files with columns routeshortname, routelongname,
                    stopid, departuretime, stopsequence, boarding, landing, occupation,
                    day, stop_lon, stop_lat, stopname
    
    Returns:
    dict: Dictionary with day of week as keys and DataFrame of hourly averages as values
    """
    # Initialize a dictionary to store dataframes by day of week
    weekly_hourly_data = {i: [] for i in range(7)}  # 0: Monday, 6: Sunday
    
    # Iterate through all CSV files in the directory
    for filename in os.listdir(data_dir):
        if filename.endswith('.csv'):
            file_path = os.path.join(data_dir, filename)
            
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Convert 'day' column to datetime
            df['day'] = pd.to_datetime(df['day'])
            
            # Convert 'departuretime' to datetime and extract hour, handling HH:MM format
            #df['hour'] = pd.to_datetime(df['departuretime'], format='%H:%M:%S').dt.hour            
            df['hour'] =  [int(i.split(":")[0]) for i in df['departuretime']]
            
            # Get day of week (0=Monday, 6=Sunday)
            df['day_of_week'] = df['day'].dt.dayofweek
            
            # Group by day of week and hour, summing boarding
            for day in range(7):
                day_data = df[df['day_of_week'] == day][['hour', 'boarding']]
                if not day_data.empty:
                    weekly_hourly_data[day].append(day_data)
    
    # Calculate averages for each day of week
    result = {}
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    for day in range(7):
        if weekly_hourly_data[day]:
            # Concatenate all data for this day
            day_df = pd.concat(weekly_hourly_data[day])
            # Calculate mean boarding by hour
            hourly_avg = day_df.groupby('hour')['boarding'].mean().round(2)
            # Convert to DataFrame and name it
            result[day_names[day]] = hourly_avg.reset_index()
            result[day_names[day]].columns = ['Hour', 'Average_Boarding']
    
    # Print results
    for day, df in result.items():
        print(f"\n{day}:")
        print(df.to_string(index=False))
    
    return result


def classify_day(date):
    # Monday=0, Sunday=6
    if date.weekday() < 5:  # Weekdays are Monday (0) to Friday (4)
        return 'weekday'
    else:  # Saturday (5) and Sunday (6) are weekends
        #return 'weekend'
        return 'saturday' if date.weekday()==5 else 'sunday'

#%%
# Calculate and print hourly boarding averages by day of week
#hourly_averages = calculate_hourly_boarding_by_day_of_week(data_dir='data_stops/')    
# Calculate and print total boarding by month
#monthly_boarding = calculate_boarding_by_month(data_dir='data_stops/')
    

# Step 1: Load the CSV file
# Define the folder path
folder_path = "data_stops"

# Initialize an empty list to store the cleaned filenames
file_list = []

# Iterate through all files in the folder
for file_name in os.listdir(folder_path):
    # Check if the file has a .csv extension
    if file_name.endswith(".csv"):
        # Remove the .csv suffix
        cleaned_name = file_name[:-4]  # Removes the last 4 characters (".csv")
        # Append the cleaned name to the list
        file_list.append(cleaned_name)

file_list.sort()


data=pd.DataFrame()
for selected_route in file_list:
    aux=pd.read_csv(f'./data_stops/{selected_route}.csv')
    #aux['hour'] = [i.split(':')[0]+':00' for i in aux['departuretime']]
    aux['hour'] = [int(i.split(':')[0]) for i in aux['departuretime']]
    aux['stop_lat'] = aux['stop_lat'].round(4)
    aux['stop_lon'] = aux['stop_lon'].round(4)
    aux['date'] = pd.to_datetime(aux['day'])
    aux['day_type'] = aux['date'].apply(classify_day)

    data=pd.concat([data,aux], axis=0)

data['stop_lat'] = data['stop_lat'].round(4)
data['stop_lon'] = data['stop_lon'].round(4)
data['date'] = pd.to_datetime(data['day'])

data['day_type'] = data['date'].apply(classify_day)
data['hour'] = [i.split(':')[0]+':00' for i in data['departuretime']]
data['day_of_week'] = [ i.strftime('%A') for i in  data['date'] ] #data['date'].dt.day_name()
#data['day_of_week_number'] = data['date'].dt.dayofweek
    