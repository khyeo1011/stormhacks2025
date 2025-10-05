# backend/app/trips.py

import os
from flask import Blueprint, jsonify, current_app
import psycopg2
import psycopg2.extras
import pandas as pd

from .auth.routes import get_db_connection

trips_bp = Blueprint('trips', __name__, url_prefix='/trips')

def get_static_data_path():
    """Constructs a reliable path to the static_data directory."""
    # Go up one level from the app's root path to the backend directory
    base_dir = os.path.abspath(os.path.join(current_app.root_path, os.pardir))
    return os.path.join(base_dir, 'static_data')

def populate_trips_from_static_data():
    """
    Reads trips from static GTFS data and populates the database.
    """
    import time
    time.sleep(5) # wait for the db to be ready
    conn = None
    try:
        conn = psycopg2.connect(
            host=os.environ.get('POSTGRES_HOST'),
            database=os.environ.get('POSTGRES_DB'),
            user=os.environ.get('POSTGRES_USER'),
            password=os.environ.get('POSTGRES_PASSWORD')
        )
        with conn.cursor() as cur:
            static_data_path = get_static_data_path()
            trips_df = pd.read_csv(os.path.join(static_data_path, 'trips.txt'))
            trips_df['route_id'] = pd.to_numeric(trips_df['route_id'], errors='coerce')
            trips_df.dropna(subset=['route_id'], inplace=True)
            trips_df['route_id'] = trips_df['route_id'].astype(int)

            for index, row in trips_df.iterrows():
                trip_id = row['trip_id']
                route_id = row['route_id']
                headsign = row.get('trip_headsign', '') # Use .get for safety
                cur.execute('SELECT 1 FROM "trips" WHERE "name" = %s', (str(trip_id),))
                if not cur.fetchone():
                    cur.execute(
                        'INSERT INTO "trips" ("name", "route_id", "headsign") VALUES (%s, %s, %s)',
                        (str(trip_id), route_id, headsign)
                    )
            conn.commit()
            print(f"Successfully populated {len(trips_df)} trips.")
    except FileNotFoundError:
        print("Error: GTFS data not found. Trips could not be populated.")
    except (Exception, psycopg2.Error) as e:
        if conn:
            conn.rollback()
        print(f"Error populating trips: {e}")
    finally:
        if conn:
            conn.close()


def update_scores(trip_id, outcome):
    """Awards points to users who predicted correctly."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT "userId" FROM "predictions" WHERE "tripId" = %s AND "predictedOutcome" = %s', (trip_id, outcome))
            winners = cur.fetchall()
            for winner in winners:
                user_id = winner[0]
                cur.execute('UPDATE "users" SET "cumulativeScore" = "cumulativeScore" + 1 WHERE "id" = %s', (user_id,))
            conn.commit()
            return len(winners)
    except psycopg2.Error as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

@trips_bp.route('', methods=['GET'])
def get_trips():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute('SELECT "id", "name" as "trip_id" FROM "trips";')
            trips = [dict(row) for row in cur.fetchall()]

        static_data_path = get_static_data_path()
        stop_times_df = pd.read_csv(os.path.join(static_data_path, 'stop_times.txt'))
        stops_df = pd.read_csv(os.path.join(static_data_path, 'stops.txt'))

        trips_with_stops = []
        for trip in trips:
            trip_id_str = trip['trip_id']
            # Convert trip_id from database to the type in the CSV for matching
            # This depends on the actual data types. Let's assume they are compatible as strings or integers.
            try:
                 # Check if trip_id from db is numeric and can be converted to int
                trip_id_val = int(float(trip_id_str))
            except (ValueError, TypeError):
                trip_id_val = trip_id_str # Keep as string if not numeric

            trip_stop_times = stop_times_df[stop_times_df['trip_id'] == trip_id_val]

            if not trip_stop_times.empty:
                first_stop_id = trip_stop_times.loc[trip_stop_times['stop_sequence'].idxmin()]['stop_id']
                last_stop_id = trip_stop_times.loc[trip_stop_times['stop_sequence'].idxmax()]['stop_id']

                first_stop_name = stops_df.loc[stops_df['stop_id'] == first_stop_id, 'stop_name'].iloc[0]
                last_stop_name = stops_df.loc[stops_df['stop_id'] == last_stop_id, 'stop_name'].iloc[0]

                trip['first_stop'] = first_stop_name
                trip['last_stop'] = last_stop_name
            else:
                trip['first_stop'] = None
                trip['last_stop'] = None
            trips_with_stops.append(trip)
        return jsonify(trips_with_stops)
    except (Exception, psycopg2.Error) as e:
        print(f"An error occurred in get_trips: {e}")
        return jsonify({"error": "An internal error occurred"}), 500
    finally:
        if conn:
            conn.close()


@trips_bp.route('/<int:trip_id>', methods=['GET'])
def get_trip(trip_id):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute('SELECT "id", "name", "route_id", "description", "outcome", "createdAt" FROM "trips" WHERE "id" = %s;', (trip_id,))
            trip = cur.fetchone()
            if trip:
                return jsonify(dict(trip))
            return jsonify({"error": "Trip not found"}), 404
    finally:
        conn.close()