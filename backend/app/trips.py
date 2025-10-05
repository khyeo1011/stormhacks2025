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
            # Load the GTFS data
            trips_df = pd.read_csv('static_data/trips.txt')
            # Filter for the specific route
            target_route_id = 37807
            route_trips = trips_df[trips_df['route_id'] == target_route_id]

            for index, row in route_trips.iterrows():
                trip_id = row['trip_id']
                # Check if trip already exists in the database
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

@trips_bp.route('/<int:trip_id>/resolve', methods=['POST'])
@jwt_required()
def resolve_trip(trip_id):
    # This endpoint could be restricted to admins
    data = request.get_json()
    outcome = data.get('outcome')

    if not outcome:
        return jsonify({"error": "outcome is required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('UPDATE "trips" SET "outcome" = %s WHERE "id" = %s', (outcome, trip_id))
        conn.commit()
        cur.close()
        return jsonify({"msg": "Trip resolved"}), 200
    except psycopg2.Error as e:
        conn.rollback()
        cur.close()
        return jsonify({"error": str(e)}), 500

@trips_bp.route('/<int:trip_id>/score', methods=['POST'])
@jwt_required()
def score_trip(trip_id):
    # This endpoint could be restricted to admins
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT "outcome" FROM "trips" WHERE "id" = %s', (trip_id,))
    trip = cur.fetchone()
    cur.close()

    if not trip:
        return jsonify({"error": "Trip not found"}), 404
    
    if not trip['outcome']:
        return jsonify({"error": "Trip has not been resolved yet"}), 400

    try:
        winners_count = update_scores(trip_id, trip['outcome'])
        return jsonify({"msg": f"Scoring complete. {winners_count} users awarded points."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500