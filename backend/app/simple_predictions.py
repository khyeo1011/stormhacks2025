import os
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import psycopg2
import psycopg2.extras
from datetime import datetime

# Create a new blueprint for simplified predictions
simple_predictions_bp = Blueprint('simple_predictions', __name__, url_prefix='/simple-predictions')

def get_db_connection():
    """Get database connection"""
    db_user = os.environ.get("POSTGRES_USER")
    db_password = os.environ.get("POSTGRES_PASSWORD")
    db_host = os.environ.get("POSTGRES_HOST")
    db_name = os.environ.get("POSTGRES_DB")
    
    return psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password
    )

@simple_predictions_bp.route('', methods=['POST'])
@jwt_required()
def create_simple_prediction():
    data = request.get_json()
    trip_id = data.get('trip_id')
    predicted_outcome = data.get('predicted_outcome')
    user_id = get_jwt_identity()

    if not all([trip_id, predicted_outcome]):
        return jsonify({"error": "trip_id and predicted_outcome are required"}), 400

    # Validate predicted_outcome
    valid_outcomes = ['on_time', 'late', 'early']
    if predicted_outcome not in valid_outcomes:
        return jsonify({"error": f"predicted_outcome must be one of: {', '.join(valid_outcomes)}"}), 400

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    try:
        # Check if the user has already made a prediction for this trip
        cur.execute('SELECT 1 FROM predictions WHERE user_id = %s AND trip_id = %s', (user_id, trip_id))
        if cur.fetchone():
            return jsonify({"error": "You have already made a prediction for this trip"}), 409

        # Insert the prediction
        cur.execute(
            'INSERT INTO predictions (user_id, trip_id, predicted_outcome) VALUES (%s, %s, %s) RETURNING id',
            (user_id, trip_id, predicted_outcome)
        )
        prediction_id = cur.fetchone()[0]
        conn.commit()
        
        return jsonify({
            'id': prediction_id,
            'message': 'Prediction created successfully',
            'trip_id': trip_id,
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

@simple_predictions_bp.route('', methods=['GET'])
@jwt_required()
def get_simple_predictions():
    user_id = get_jwt_identity()
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    try:
        cur.execute(
            'SELECT id, trip_id, predicted_outcome, created_at FROM predictions WHERE user_id = %s ORDER BY created_at DESC',
            (user_id,)
        )
        predictions = [dict(row) for row in cur.fetchall()]
        return jsonify(predictions)
        
    except psycopg2.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
    finally:
        cur.close()
        conn.close()

@simple_predictions_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_prediction_stats():
    user_id = get_jwt_identity()
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    try:
        # Get total predictions count
        cur.execute('SELECT COUNT(*) as total FROM predictions WHERE user_id = %s', (user_id,))
        total_result = cur.fetchone()
        total_predictions = total_result['total'] if total_result else 0
        
        # Get today's predictions count
        today = datetime.now().date()
        cur.execute(
            'SELECT COUNT(*) as today FROM predictions WHERE user_id = %s AND DATE(created_at) = %s',
            (user_id, today)
        )
        today_result = cur.fetchone()
        today_predictions = today_result['today'] if today_result else 0
        
        # Get predictions by outcome
        cur.execute(
            'SELECT predicted_outcome, COUNT(*) as count FROM predictions WHERE user_id = %s GROUP BY predicted_outcome',
            (user_id,)
        )
        outcome_counts = {row['predicted_outcome']: row['count'] for row in cur.fetchall()}
        
        # Calculate accuracy (simplified - assuming on_time predictions are correct)
        on_time_count = outcome_counts.get('on_time', 0)
        accuracy = round((on_time_count / total_predictions * 100) if total_predictions > 0 else 0, 1)
        
        return jsonify({
            'total_predictions': total_predictions,
            'today_predictions': today_predictions,
            'accuracy': accuracy,
            'outcome_counts': outcome_counts
        })
        
    except psycopg2.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
    finally:
        cur.close()
        conn.close()
