import os
import requests
from google.transit import gtfs_realtime_pb2
import psycopg2
import psycopg2.extras
import pandas as pd

# --- Database Configuration ---
DB_HOST = os.environ.get('POSTGRES_HOST', 'db')
DB_NAME = os.environ.get('POSTGRES_DB', 'appdb')
DB_USER = os.environ.get('POSTGRES_USER', 'user')
DB_PASS = os.environ.get('POSTGRES_PASSWORD', 'password')

# --- GTFS Realtime API Configuration ---
API_KEY = "obFPHNKClWefKaJgzVec"
GTFS_RT_URL = f"https://gtfsapi.translink.ca/v3/gtfsrealtime?apikey={API_KEY}"

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def resolve_trips():
    """
    Fetches real-time GTFS data, determines trip outcomes, and updates the database.
    """
    try:
        # --- 1. Fetch real-time GTFS data ---
        print("Fetching real-time GTFS data...")
        response = requests.get(GTFS_RT_URL)
        response.raise_for_status()  # Raise an exception for bad status codes
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        print(f"Successfully fetched and parsed GTFS-RT feed. Timestamp: {feed.header.timestamp}")

        # --- 2. Get unresolved trips from the database ---
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('SELECT "id", "name" FROM "trips" WHERE "outcome" IS NULL')
        unresolved_trips = cur.fetchall()
        print(f"Found {len(unresolved_trips)} unresolved trips in the database.")

        if not unresolved_trips:
            print("No unresolved trips to process.")
            return

        # --- 3. Process trip updates ---
        updates_processed = 0
        for trip in unresolved_trips:
            trip_id = trip['id']
            trip_name = trip['name'] # Assuming trip_name from your db corresponds to trip_id in GTFS

            # Find the corresponding trip update in the real-time feed
            for entity in feed.entity:
                if entity.HasField('trip_update') and str(entity.trip_update.trip.trip_id) == str(trip_name):
                    # Found an update for our trip. Let's determine the outcome.
                    # For simplicity, we'll just check the first stop time update.
                    if entity.trip_update.stop_time_update:
                        first_stop_update = entity.trip_update.stop_time_update[0]
                        delay = first_stop_update.arrival.delay if first_stop_update.HasField('arrival') else 0

                        outcome = "delayed" if delay > 60 else "on-time" # e.g., > 60s delay

                        print(f"Resolving trip {trip_id} ('{trip_name}') with outcome: {outcome}")

                        # --- 4. Update trip outcome and award points ---
                        # We can reuse the logic from the resolve_trip endpoint.
                        # For simplicity, we'll do it directly here.
                        cur.execute('UPDATE "trips" SET "outcome" = %s WHERE "id" = %s', (outcome, trip_id))

                        cur.execute('SELECT "userId" FROM "predictions" WHERE "tripId" = %s AND "predictedOutcome" = %s', (trip_id, outcome))
                        winners = cur.fetchall()
                        for winner in winners:
                            user_id = winner['userId']
                            print(f"  Awarding point to user {user_id}")
                            cur.execute('UPDATE "users" SET "cumulativeScore" = "cumulativeScore" + 1 WHERE "id" = %s', (user_id,))
                        
                        updates_processed += 1
                        conn.commit()
                        break # Move to the next unresolved trip

        cur.close()
        conn.close()
        print(f"Finished processing. {updates_processed} trips were resolved.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching GTFS-RT data: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    resolve_trips()
