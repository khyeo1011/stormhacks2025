import pandas as pd
from sqlalchemy import create_engine, text
import os
from datetime import datetime, timedelta

# Database connection settings from docker-compose
db_user = os.environ.get("POSTGRES_USER")
db_password = os.environ.get("POSTGRES_PASSWORD")
db_host = os.environ.get("POSTGRES_HOST")
db_name = os.environ.get("POSTGRES_DB")

# SQLAlchemy connection string
db_url = f'postgresql://{db_user}:{db_password}@{db_host}/{db_name}'
engine = create_engine(db_url)

# Path to static data files
static_data_path = './static_data/'

# Load data into pandas DataFrames
stops_df = pd.read_csv(static_data_path + 'stops.txt', dtype={'stop_id': str})
routes_df = pd.read_csv(static_data_path + 'routes.txt', dtype={'route_id': str})
calendar_df = pd.read_csv(static_data_path + 'calendar.txt', dtype={'service_id': str})
trips_df = pd.read_csv(static_data_path + 'trips.txt', dtype={'trip_id': str, 'route_id': str, 'service_id': str, 'shape_id': str})
stop_times_df = pd.read_csv(static_data_path + 'stop_times.txt', dtype={'trip_id': str, 'stop_id': str})

# --- Data Pruning ---
route_id_to_keep = '37807'

routes_df = routes_df[routes_df['route_id'] == route_id_to_keep]

trips_df = trips_df[trips_df['route_id'] == route_id_to_keep]

valid_trip_ids = trips_df['trip_id'].unique()
stop_times_df = stop_times_df[stop_times_df['trip_id'].isin(valid_trip_ids)]

valid_stop_ids = stop_times_df['stop_id'].unique()
stops_df = stops_df[stops_df['stop_id'].isin(valid_stop_ids)]

valid_service_ids = trips_df['service_id'].unique()
calendar_df = calendar_df[calendar_df['service_id'].isin(valid_service_ids)]
# --- End Data Pruning ---

# Select and rename columns to match the database schema
stops_df = stops_df[['stop_id', 'stop_name', 'stop_lat', 'stop_lon']]
routes_df = routes_df[['route_id', 'route_short_name', 'route_long_name']]
calendar_df = calendar_df[['service_id', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'start_date', 'end_date']]
trips_df = trips_df[['trip_id', 'route_id', 'service_id', 'trip_headsign', 'direction_id', 'shape_id']]
stop_times_df = stop_times_df[['trip_id', 'arrival_time', 'departure_time', 'stop_id', 'stop_sequence']]

# --- Expand trips and stop_times with service_date ---
expanded_trips_data = []
for idx, trip_row in trips_df.iterrows():
    service_id = trip_row['service_id']
    calendar_entry = calendar_df[calendar_df['service_id'] == service_id].iloc[0]

    start_date = datetime.strptime(str(calendar_entry['start_date']), '%Y%m%d').date()
    end_date = datetime.strptime(str(calendar_entry['end_date']), '%Y%m%d').date()

    current_date = start_date
    while current_date <= end_date:
        day_of_week = current_date.weekday() # Monday is 0, Sunday is 6
        
        service_runs_today = False
        if day_of_week == 0 and calendar_entry['monday'] == 1: service_runs_today = True
        if day_of_week == 1 and calendar_entry['tuesday'] == 1: service_runs_today = True
        if day_of_week == 2 and calendar_entry['wednesday'] == 1: service_runs_today = True
        if day_of_week == 3 and calendar_entry['thursday'] == 1: service_runs_today = True
        if day_of_week == 4 and calendar_entry['friday'] == 1: service_runs_today = True
        if day_of_week == 5 and calendar_entry['saturday'] == 1: service_runs_today = True
        if day_of_week == 6 and calendar_entry['sunday'] == 1: service_runs_today = True

        if service_runs_today:
            new_trip_row = trip_row.copy()
            new_trip_row['service_date'] = current_date
            expanded_trips_data.append(new_trip_row)
        
        current_date += timedelta(days=1)

trips_df_expanded = pd.DataFrame(expanded_trips_data)

# Merge stop_times with expanded trips to get service_date for each stop_time
stop_times_df_expanded = pd.merge(stop_times_df, trips_df_expanded[['trip_id', 'service_date']], on='trip_id', how='inner')

# --- End Expand trips and stop_times with service_date ---

with engine.connect() as connection:
    connection.execute(text("DROP TABLE IF EXISTS stop_times CASCADE"))
    connection.execute(text("DROP TABLE IF EXISTS trips CASCADE"))
    connection.execute(text("DROP TABLE IF EXISTS stops CASCADE"))
    connection.execute(text("DROP TABLE IF EXISTS routes CASCADE"))
    connection.execute(text("DROP TABLE IF EXISTS calendar CASCADE"))
    connection.execute(text("DROP TABLE IF EXISTS predictions CASCADE"))
    connection.execute(text("DROP TABLE IF EXISTS friends CASCADE"))
    connection.execute(text("DROP TABLE IF EXISTS friend_requests CASCADE"))
    connection.execute(text("DROP TABLE IF EXISTS users CASCADE"))
    connection.commit()

# Write DataFrames to the database
print(f"Loading {len(stops_df)} stops...")
stops_df.to_sql('stops', engine, if_exists='append', index=False)
print(f"Loading {len(routes_df)} routes...")
routes_df.to_sql('routes', engine, if_exists='append', index=False)
print(f"Loading {len(calendar_df)} calendar entries...")
calendar_df.to_sql('calendar', engine, if_exists='append', index=False)
print(f"Loading {len(trips_df_expanded)} expanded trips...")
trips_df_expanded.to_sql('trips', engine, if_exists='append', index=False)
print(f"Loading {len(stop_times_df_expanded)} expanded stop times...")
stop_times_df_expanded.to_sql('stop_times', engine, if_exists='append', index=False)

print("Data loaded successfully into the database.")
