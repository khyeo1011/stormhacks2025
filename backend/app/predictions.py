from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta

from .auth.routes import get_db_connection

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

    # Validate predicted_outcome
    valid_outcomes = ['on_time', 'late', 'early']
    if predicted_outcome not in valid_outcomes:
        return jsonify({"error": f"predicted_outcome must be one of: {', '.join(valid_outcomes)}"}), 400

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    try:
        # Ensure trip exists for the given date
        cur.execute('SELECT 1 FROM trips WHERE trip_id = %s AND service_date = %s', (gtfs_trip_id, service_date))
        if cur.fetchone() is None:
            return jsonify({"error": "Trip not found for the given service_date"}), 404

        # Check if the user has already made a prediction for this trip and date
        cur.execute('SELECT 1 FROM predictions WHERE user_id = %s AND trip_id = %s AND service_date = %s', (user_id, gtfs_trip_id, service_date))
        if cur.fetchone():
            return jsonify({"error": "You have already made a prediction for this trip on this date"}), 409

        # Insert the prediction with service_date
        cur.execute(
            'INSERT INTO predictions (user_id, trip_id, service_date, predicted_outcome) VALUES (%s, %s, %s, %s) RETURNING id',
            (user_id, gtfs_trip_id, service_date, predicted_outcome)
        )
        prediction_id = cur.fetchone()[0]
        conn.commit()
        
        return jsonify({
            'id': prediction_id,
            'message': 'Prediction created successfully',
            'trip_id': gtfs_trip_id,
            'service_date': service_date.isoformat(),
            'predicted_outcome': predicted_outcome
        }), 201
        
    except psycopg2.Error as e:
        conn.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
    finally:
        cur.close()
        conn.close()

@predictions_bp.route('', methods=['GET'])
@jwt_required()
def get_predictions():
    user_id = get_jwt_identity()
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    try:
        cur.execute('SELECT id, trip_id, service_date, predicted_outcome, created_at FROM predictions WHERE user_id = %s ORDER BY created_at DESC', (user_id,))
        predictions = [dict(row) for row in cur.fetchall()]
        
        # Convert service_date to string for JSON serialization
        for p in predictions:
            if 'service_date' in p and hasattr(p['service_date'], 'isoformat'):
                p['service_date'] = p['service_date'].isoformat()
        
        return jsonify(predictions)
        
    except psycopg2.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
    finally:
        cur.close()
        conn.close()