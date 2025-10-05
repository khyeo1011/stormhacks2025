from flask import Blueprint, jsonify, request
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
    service_date_str = data.get('service_date')
    predicted_outcome = data.get('predicted_outcome')
    user_id = get_jwt_identity()

    if not all([gtfs_trip_id, service_date_str, predicted_outcome]):
        return jsonify({"error": "trip_id, service_date, and predicted_outcome are required"}), 400

    try:
        service_date = datetime.strptime(service_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Invalid service_date format. Use YYYY-MM-DD."}), 400

    if predicted_outcome not in ["late", "on_time"]:
        return jsonify({"error": "predicted_outcome must be 'late' or 'on_time'"}), 400

    # Ensure data is loaded
    if trips_df.empty:
        from .trips import load_data_from_db
        load_data_from_db()

    # Get trip from the in-memory dataframe
    trip = trips_df[(trips_df['trip_id'] == gtfs_trip_id) & (trips_df['service_date'] == service_date)]
    if trip.empty:
        return jsonify({"error": "Trip not found"}), 404

    # Get stop times from the in-memory dataframe
    trip_stops = stop_times_df[(stop_times_df['trip_id'] == gtfs_trip_id) & (stop_times_df['service_date'] == service_date)]
    if trip_stops.empty:
        return jsonify({"error": "Could not find stop times for this trip"}), 404
    
    first_stop = trip_stops.sort_values(by='stop_sequence').iloc[0]
    first_stop_arrival_time_str = first_stop['arrival_time']

    try:
        # Handle times > 23:59:59
        h, m, s = map(int, first_stop_arrival_time_str.split(':'))
        scheduled_arrival_datetime = datetime(service_date.year, service_date.month, service_date.day, 0, 0, 0) + timedelta(hours=h, minutes=m, seconds=s)
        
        if datetime.now() > scheduled_arrival_datetime:
            return jsonify({"error": "Cannot make a prediction for a trip that has already started"}), 403
    except ValueError:
        return jsonify({"error": "Could not parse arrival time for the trip"}), 500

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        # Check if the user has already made a prediction for this trip on this service_date
        cur.execute('SELECT 1 FROM predictions WHERE user_id = %s AND trip_id = %s AND service_date = %s', (user_id, gtfs_trip_id, service_date))
        if cur.fetchone():
            return jsonify({"error": "You have already made a prediction for this trip on this date"}), 409

        cur.execute(
            'INSERT INTO predictions (user_id, trip_id, service_date, predicted_outcome) VALUES (%s, %s, %s, %s) RETURNING id',
            (user_id, gtfs_trip_id, service_date, predicted_outcome)
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
    cur.execute('SELECT id, trip_id, service_date, predicted_outcome, created_at FROM predictions WHERE user_id = %s;', (user_id,))
    predictions = [dict(row) for row in cur.fetchall()]
    cur.close()
    # Convert service_date to string for JSON serialization
    for p in predictions:
        if 'service_date' in p and isinstance(p['service_date'], datetime.date):
            p['service_date'] = p['service_date'].isoformat()
    return jsonify(predictions)