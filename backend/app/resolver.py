import os
import requests
from google.transit import gtfs_realtime_pb2
import psycopg2
import psycopg2.extras
import pandas as pd
from datetime import datetime, timedelta
from flask import current_app

from .auth.routes import get_db_connection
from .trips import stop_times_df, trips_df, update_scores

# --- GTFS Realtime API Configuration ---
API_KEY = "obFPHNKClWefKaJgzVec" # This should be in environment variables
GTFS_RT_URL = f"https://gtfsapi.translink.ca/v3/gtfsrealtime?apikey={API_KEY}"

def resolve_pending_trips():
    """
    Fetches real-time GTFS data, determines trip outcomes, and updates the database
    for trips that are due to be resolved.
    """
    with current_app.app_context():
        print("Running resolver to check for pending trips...")
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # --- 1. Get unresolved trips from the database ---
            # Query for trips that have no outcome yet
            cur.execute('SELECT trip_id, service_date FROM trips WHERE outcome IS NULL')
            unresolved_trips_db = cur.fetchall()
            print(f"Found {len(unresolved_trips_db)} unresolved trips in the database.")

            if not unresolved_trips_db:
                print("No unresolved trips to process.")
                return

            # --- 2. Fetch real-time GTFS data ---
            print("Fetching real-time GTFS data...")
            response = requests.get(GTFS_RT_URL)
            response.raise_for_status()
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(response.content)
            print(f"Successfully fetched and parsed GTFS-RT feed. Timestamp: {feed.header.timestamp}")

            updates_processed = 0
            for trip_db in unresolved_trips_db:
                trip_id = trip_db['trip_id']
                service_date = trip_db['service_date']

                # Find the last stop for the trip from in-memory data
                # Need to filter stop_times_df by trip_id and service_date
                trip_stops = stop_times_df[(stop_times_df['trip_id'] == trip_id) & (stop_times_df['service_date'] == service_date)]

                if trip_stops.empty:
                    print(f"Could not find stop times for trip {trip_id} on {service_date}. Skipping.")
                    continue
                
                last_stop = trip_stops.sort_values(by='stop_sequence').iloc[-1]
                last_stop_arrival_time_str = last_stop['arrival_time']
                
                # Convert scheduled arrival time to datetime object for comparison
                try:
                    # GTFS times can exceed 24:00:00
                    h, m, s = map(int, last_stop_arrival_time_str.split(':'))
                    scheduled_arrival_datetime = datetime(service_date.year, service_date.month, service_date.day, 0, 0, 0) + timedelta(hours=h, minutes=m, seconds=s)

                    # Define a resolution window (e.g., 5 minutes after scheduled arrival)
                    resolution_window_end = scheduled_arrival_datetime + timedelta(minutes=5)

                    if datetime.now() < resolution_window_end:
                        print(f"Trip {trip_id} on {service_date} is not yet due for resolution. Skipping.")
                        continue
                except ValueError:
                    print(f"Could not parse arrival time for trip {trip_id} on {service_date}. Skipping.")
                    continue

                # --- 3. Find the corresponding trip update in the real-time feed ---
                outcome = "unknown" # Default outcome
                for entity in feed.entity:
                    if entity.HasField('trip_update') and \
                       entity.trip_update.trip.trip_id == trip_id and \
                       entity.trip_update.trip.start_date == service_date.strftime('%Y%m%d'):
                        
                        # Find the stop time update for the last stop
                        for stop_update in entity.trip_update.stop_time_update:
                            if stop_update.stop_sequence == last_stop['stop_sequence']:
                                delay = stop_update.arrival.delay if stop_update.HasField('arrival') else 0
                                
                                if delay > 60: # More than 1 minute late
                                    outcome = "late"
                                else:
                                    outcome = "on_time"
                                break # Stop update found
                        break # Trip update found
                
                # --- 4. Update trip outcome in the database ---
                cur.execute(
                    'UPDATE trips SET outcome = %s WHERE trip_id = %s AND service_date = %s',
                    (outcome, trip_id, service_date)
                )
                conn.commit()
                print(f"Resolved trip {trip_id} on {service_date} with outcome: {outcome}")

                # --- 5. Score predictions ---
                # Assuming update_scores can handle trip_id and service_date
                update_scores(trip_id, service_date, outcome)
                updates_processed += 1

            cur.close()
            conn.close()
            print(f"Finished processing. {updates_processed} trips were resolved.")

        except requests.exceptions.RequestException as e:
            print(f"Error making API call: {e}")
        except Exception as e:
            print(f"An error occurred during trip resolution: {e}")
        finally:
            if conn:
                conn.close()
