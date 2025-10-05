import random
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta
from flask import current_app

from .auth.routes import get_db_connection
from .trips import update_scores

def resolve_pending_trips(app, trips_data, stop_times_data): # Accept app and dataframes as arguments
    """
    Simulates trip outcomes for pending trips and updates the database.
    """
    with app.app_context(): # Use the passed app instance to push the application context
        print("Running resolver to check for pending trips...")
        
        # Dataframes are now passed as arguments, no need to load them here
        # from .trips import load_data_from_db, stop_times_df, trips_df
        # load_data_from_db()
        
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # --- 1. Get unresolved trips from the database that are due for resolution ---
            # We need to iterate through trips_data to find trips that are due
            unresolved_trips_due = []
            for idx, trip_row in trips_data[trips_data['outcome'].isnull()].iterrows():
                trip_id = trip_row['trip_id']
                service_date = trip_row['service_date']

                trip_stops = stop_times_data[(stop_times_data['trip_id'] == trip_id) & (stop_times_data['service_date'] == service_date)]

                if trip_stops.empty:
                    # print(f"Could not find stop times for trip {trip_id} on {service_date}. Skipping for resolution check.")
                    continue
                
                last_stop = trip_stops.sort_values(by='stop_sequence').iloc[-1]
                last_stop_arrival_time_str = last_stop['arrival_time']
                
                try:
                    h, m, s = map(int, last_stop_arrival_time_str.split(':'))
                    scheduled_arrival_datetime = datetime(service_date.year, service_date.month, service_date.day, 0, 0, 0) + timedelta(hours=h, minutes=m, seconds=s)
                    resolution_window_end = scheduled_arrival_datetime + timedelta(minutes=5)

                    if datetime.now() >= resolution_window_end:
                        unresolved_trips_due.append({'trip_id': trip_id, 'service_date': service_date})
                except ValueError:
                    print(f"Could not parse arrival time for trip {trip_id} on {service_date}. Skipping for resolution check.")
                    continue

            print(f"Found {len(unresolved_trips_due)} unresolved trips due for resolution.")

            if not unresolved_trips_due:
                print("No unresolved trips due to process.")
                return

            updates_processed = 0
            for trip_db in unresolved_trips_due:
                trip_id = trip_db['trip_id']
                service_date = trip_db['service_date']

                # --- 3. Simulate trip outcome ---
                outcome = random.choice(["on_time", "late"])
                
                # --- 4. Update trip outcome in the database ---
                cur.execute(
                    'UPDATE trips SET outcome = %s WHERE trip_id = %s AND service_date = %s',
                    (outcome, trip_id, service_date)
                )
                conn.commit()
                print(f"Resolved trip {trip_id} on {service_date} with simulated outcome: {outcome}")

                # --- 5. Score predictions ---
                update_scores(trip_id, service_date, outcome)
                updates_processed += 1

            cur.close()
            conn.close()
            print(f"Finished processing. {updates_processed} trips were resolved.")

        except Exception as e:
            print(f"An error occurred during trip resolution: {e}")
        finally:
            if conn:
                conn.close()
