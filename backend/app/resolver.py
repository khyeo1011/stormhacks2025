import os
import requests
from google.transit import gtfs_realtime_pb2
import psycopg2
import psycopg2.extras
import pandas as pd
import argparse
from datetime import datetime, timedelta
import sys

# --- Database Configuration ---
DB_HOST = os.environ.get('POSTGRES_HOST', 'db')
DB_NAME = os.environ.get('POSTGRES_DB', 'appdb')
DB_USER = os.environ.get('POSTGRES_USER', 'user')
DB_PASS = os.environ.get('POSTGRES_PASSWORD', 'password')

# --- GTFS Realtime API Configuration ---
API_KEY = "obFPHNKClWefKaJgzVec"
GTFS_RT_URL = f"https://gtfsapi.translink.ca/v3/gtfsrealtime?apikey={API_KEY}"

# --- API Configuration ---
BASE_URL = "http://localhost:8000"
# NOTE: In a real application, you would not hardcode credentials like this.
# You would use a more secure way to authenticate the resolver script.
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin"


def get_script_db_connection():
    """Establishes a database connection for the script."""
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def get_jwt_token():
    """Authenticates and returns a JWT token."""
    login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    response.raise_for_status()
    return response.json()['access_token']

def resolve_trips(force=False):
    """
    Fetches real-time GTFS data, determines trip outcomes, and updates the database.
    """
    try:
        # --- 0. Get JWT token ---
        print("Authenticating resolver...")
        token = get_jwt_token()
        headers = {"Authorization": f"Bearer {token}"}

        # --- 1. Load static GTFS data ---
        print("Loading static GTFS data...")
        stop_times_df = pd.read_csv('app/static_data/stop_times.txt')

        # --- 2. Get unresolved trips from the database ---
        conn = get_script_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('SELECT "id", "name" FROM "trips" WHERE "outcome" IS NULL')
        unresolved_trips = cur.fetchall()
        print(f"Found {len(unresolved_trips)} unresolved trips in the database.")

        if not unresolved_trips:
            print("No unresolved trips to process.")
            return

        # --- 3. Fetch real-time GTFS data ---
        print("Fetching real-time GTFS data...")
        response = requests.get(GTFS_RT_URL)
        response.raise_for_status()
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        print(f"Successfully fetched and parsed GTFS-RT feed. Timestamp: {feed.header.timestamp}")

        # --- 4. Process trip updates ---
        updates_processed = 0
        for trip in unresolved_trips:
            trip_id_db = trip['id']
            trip_id_gtfs = int(trip['name'])

            # Find the last stop for the trip
            trip_stops = stop_times_df[stop_times_df['trip_id'] == trip_id_gtfs]
            if trip_stops.empty:
                print(f"Could not find stop times for trip {trip_id_gtfs}")
                continue
            
            last_stop = trip_stops.sort_values(by='stop_sequence').iloc[-1]
            last_stop_arrival_time_str = last_stop['arrival_time']
            
            # Convert arrival time to datetime object
            try:
                h, m, s = map(int, last_stop_arrival_time_str.split(':'))
                arrival_time_delta = timedelta(hours=h, minutes=m, seconds=s)
                
                now = datetime.now()
                now_delta = timedelta(hours=now.hour, minutes=now.minute, seconds=now.second)

                if not force and now_delta < arrival_time_delta:
                    print(f"Trip {trip_id_gtfs} has not ended yet. Skipping.")
                    continue
            except ValueError:
                print(f"Could not parse arrival time for trip {trip_id_gtfs}. Skipping.")
                continue

            # Find the corresponding trip update in the real-time feed
            for entity in feed.entity:
                if entity.HasField('trip_update') and str(entity.trip_update.trip.trip_id) == str(trip_id_gtfs):
                    # Find the stop time update for the last stop
                    for stop_update in entity.trip_update.stop_time_update:
                        if stop_update.stop_sequence == last_stop['stop_sequence']:
                            delay = stop_update.arrival.delay if stop_update.HasField('arrival') else 0
                            outcome = "delayed" if delay > 60 else "on-time"

                            print(f"Resolving trip {trip_id_db} ('{trip_id_gtfs}') with outcome: {outcome}")

                            # Resolve the trip
                            resolve_response = requests.post(f"{BASE_URL}/trips/{trip_id_db}/resolve", headers=headers, json={"outcome": outcome})
                            resolve_response.raise_for_status()

                            # Score the trip
                            score_response = requests.post(f"{BASE_URL}/trips/{trip_id_db}/score", headers=headers)
                            score_response.raise_for_status()
                            
                            updates_processed += 1
                            break # Move to the next unresolved trip
                    break # Trip update found and processed

        cur.close()
        conn.close()
        print(f"Finished processing. {updates_processed} trips were resolved.")

    except requests.exceptions.RequestException as e:
        print(f"Error making API call: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    from app.app import create_app
    from app.auth.routes import get_db_connection
    import time
    app = create_app()
    with app.app_context():
        # Create a dummy admin user for the resolver to use
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            # A more secure way to handle passwords should be used.
            from werkzeug.security import generate_password_hash
            hashed_password = generate_password_hash(ADMIN_PASSWORD)
            cur.execute('INSERT INTO "users" ("email", "password", "nickname") VALUES (%s, %s, %s)', (ADMIN_EMAIL, hashed_password, "Admin"))
            conn.commit()
        except psycopg2.IntegrityError:
            conn.rollback() # User already exists
        finally:
            cur.close()

        parser = argparse.ArgumentParser(description='Resolve trip predictions.')
        parser.add_argument('--force', action='store_true', help='Force resolve all unresolved trips.')
        args = parser.parse_args()
        
        while True:
            print("Running resolver...")
            resolve_trips(force=args.force)
            print("Resolver finished. Waiting 60 seconds...")
            time.sleep(60)