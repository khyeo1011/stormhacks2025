# backend/app/trips.py

import os
from flask import Blueprint, jsonify, request, g, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import psycopg2
import psycopg2.extras
import pandas as pd

from .auth.routes import get_db_connection

trips_bp = Blueprint('trips', __name__, url_prefix='/trips')

def populate_trips_from_static_data():
    """
    Reads trips from static GTFS data and populates the database.
    This function is intended to be run at application startup.
    """
    with current_app.app_context():
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            trips_df = pd.read_csv('static_data/trips.txt')
            target_route_id = 37807
            route_trips = trips_df[trips_df['route_id'] == target_route_id]

            for index, row in route_trips.iterrows():
                trip_id = row['trip_id']
                cur.execute('SELECT 1 FROM "trips" WHERE "name" = %s', (str(trip_id),))
                if not cur.fetchone():
                    cur.execute(
                        'INSERT INTO "trips" ("name") VALUES (%s)',
                        (str(trip_id),)
                    )
            conn.commit()
            print(f"Successfully populated {len(route_trips)} trips for route {target_route_id}.")
        except FileNotFoundError:
            print("Error: GTFS data not found. Trips could not be populated.")
        except Exception as e:
            conn.rollback()
            print(f"Error populating trips: {e}")
        finally:
            cur.close()


def update_scores(trip_id, outcome):
    """Awards points to users who predicted correctly."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('SELECT "userId" FROM "predictions" WHERE "tripId" = %s AND "predictedOutcome" = %s', (trip_id, outcome))
        winners = cur.fetchall()
        for winner in winners:
            user_id = winner[0]
            cur.execute('UPDATE "users" SET "cumulativeScore" = "cumulativeScore" + 1 WHERE "id" = %s', (user_id,))
        conn.commit()
        cur.close()
        return len(winners)
    except psycopg2.Error as e:
        conn.rollback()
        cur.close()
        raise e

@trips_bp.route('', methods=['GET'])
def get_trips():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT "id", "name" as "trip_id" FROM "trips";')
    trips = [dict(row) for row in cur.fetchall()]
    cur.close()
    return jsonify(trips)


@trips_bp.route('/<int:trip_id>', methods=['GET'])
def get_trip(trip_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT "id", "name", "description", "outcome", "createdAt" FROM "trips" WHERE "id" = %s;', (trip_id,))
    trip = cur.fetchone()
    cur.close()
    if trip:
        return jsonify(dict(trip))
    return jsonify({"error": "Trip not found"}), 404