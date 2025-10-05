
import os
from flask import Blueprint, jsonify, request, g
from flask_jwt_extended import jwt_required, get_jwt_identity
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta

from .auth.routes import get_db_connection
from .trips import trips_df, stop_times_df

predictions_bp = Blueprint('predictions', __name__, url_prefix='/predictions')

@predictions_bp.route('', methods=['POST'])
@jwt_required()
def create_prediction():
    data = request.get_json()
    gtfs_trip_id = data.get('trip_id')
    predicted_outcome = data.get('predicted_outcome')
    user_id = get_jwt_identity()

    if not all([gtfs_trip_id, predicted_outcome]):
        return jsonify({"error": "trip_id and predicted_outcome are required"}), 400

    # Get trip from the in-memory dataframe
    trip = trips_df[trips_df['trip_id'] == gtfs_trip_id]
    if trip.empty:
        return jsonify({"error": "Trip not found"}), 404

    # Get stop times from the in-memory dataframe
    trip_stops = stop_times_df[stop_times_df['trip_id'] == gtfs_trip_id]
    if trip_stops.empty:
        return jsonify({"error": "Could not find stop times for this trip"}), 404
    
    first_stop = trip_stops.sort_values(by='stop_sequence').iloc[0]
    first_stop_arrival_time_str = first_stop['arrival_time']

    try:
        # Handle times > 23:59:59
        h, m, s = map(int, first_stop_arrival_time_str.split(':'))
        arrival_time_delta = timedelta(hours=h, minutes=m, seconds=s)
        
        now = datetime.now()
        now_delta = timedelta(hours=now.hour, minutes=now.minute, seconds=now.second)

        if now_delta > arrival_time_delta:
            return jsonify({"error": "Cannot make a prediction for a trip that has already started"}), 403
    except ValueError:
        return jsonify({"error": "Could not parse arrival time for the trip"}), 500

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        # Check if the user has already made a prediction for this trip
        cur.execute('SELECT 1 FROM predictions WHERE user_id = %s AND trip_id = %s', (user_id, gtfs_trip_id))
        if cur.fetchone():
            return jsonify({"error": "You have already made a prediction for this trip"}), 409

        cur.execute(
            'INSERT INTO predictions (user_id, trip_id, predicted_outcome) VALUES (%s, %s, %s) RETURNING id',
            (user_id, gtfs_trip_id, predicted_outcome)
        )
        prediction_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        return jsonify({'id': prediction_id}), 201
    except psycopg2.Error as e:
        conn.rollback()
        cur.close()
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        conn.rollback()
        cur.close()
        return jsonify({"error": str(e)}), 500

@predictions_bp.route('', methods=['GET'])
@jwt_required()
def get_predictions():
    user_id = get_jwt_identity()
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT id, trip_id, predicted_outcome, created_at FROM predictions WHERE user_id = %s;', (user_id,))
    predictions = [dict(row) for row in cur.fetchall()]
    cur.close()
    return jsonify(predictions)
