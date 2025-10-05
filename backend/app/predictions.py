import os
from flask import Blueprint, jsonify, request, g
from flask_jwt_extended import jwt_required, get_jwt_identity
import psycopg2
import psycopg2.extras
import pandas as pd
from datetime import datetime

from .auth.routes import get_db_connection

predictions_bp = Blueprint('predictions', __name__, url_prefix='/predictions')

@predictions_bp.route('', methods=['POST'])
@jwt_required()
def create_prediction():
    data = request.get_json()
    trip_id_db = data.get('tripId')
    predicted_outcome = data.get('predictedOutcome')
    user_id = get_jwt_identity()

    if not all([trip_id_db, predicted_outcome]):
        return jsonify({"error": "tripId and predictedOutcome are required"}), 400

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        # Get trip name (GTFS trip_id) from the database
        cur.execute('SELECT "name" FROM "trips" WHERE "id" = %s', (trip_id_db,))
        trip = cur.fetchone()
        if not trip:
            return jsonify({"error": "Trip not found"}), 404
        trip_id_gtfs = int(trip['name'])

        # Load stop_times.txt to check the first stop's arrival time
        stop_times_df = pd.read_csv('static_data/stop_times.txt')
        trip_stops = stop_times_df[stop_times_df['trip_id'] == trip_id_gtfs]
        if trip_stops.empty:
            return jsonify({"error": "Could not find stop times for this trip"}), 404
        
        first_stop = trip_stops.sort_values(by='stop_sequence').iloc[0]
        first_stop_arrival_time_str = first_stop['arrival_time']

        try:
            arrival_time = datetime.strptime(first_stop_arrival_time_str, '%H:%M:%S').time()
            now = datetime.now().time()

            if now > arrival_time:
                return jsonify({"error": "Cannot make a prediction for a trip that has already started"}), 403
        except ValueError:
            return jsonify({"error": "Could not parse arrival time for the trip"}), 500

        # Check if the user has already made a prediction for this trip
        cur.execute('SELECT 1 FROM "predictions" WHERE "userId" = %s AND "tripId" = %s', (user_id, trip_id_db))
        if cur.fetchone():
            return jsonify({"error": "You have already made a prediction for this trip"}), 409

        cur.execute(
            'INSERT INTO "predictions" ("userId", "tripId", "predictedOutcome") VALUES (%s, %s, %s) RETURNING "id"',
            (user_id, trip_id_db, predicted_outcome)
        )
        prediction_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        return jsonify({'id': prediction_id}), 201
    except psycopg2.Error as e:
        conn.rollback()
        cur.close()
        return jsonify({"error": str(e)}), 500
    except FileNotFoundError:
        return jsonify({"error": "GTFS data not found"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@predictions_bp.route('', methods=['GET'])
@jwt_required()
def get_predictions():
    user_id = get_jwt_identity()
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT "id", "tripId", "predictedOutcome", "createdAt" FROM "predictions" WHERE "userId" = %s;', (user_id,))
    predictions = [dict(row) for row in cur.fetchall()]
    cur.close()
    return jsonify(predictions)