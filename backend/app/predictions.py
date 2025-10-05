import os
from flask import Blueprint, jsonify, request, g
from flask_jwt_extended import jwt_required, get_jwt_identity
import psycopg2

from .auth.routes import get_db_connection

predictions_bp = Blueprint('predictions', __name__, url_prefix='/predictions')

@predictions_bp.route('', methods=['POST'])
@jwt_required()
def create_prediction():
    data = request.get_json()
    trip_id = data.get('tripId')
    predicted_outcome = data.get('predictedOutcome')
    user_id = get_jwt_identity()

    if not all([trip_id, predicted_outcome]):
        return jsonify({"error": "tripId and predictedOutcome are required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Check if the user has already made a prediction for this trip
        cur.execute('SELECT 1 FROM "predictions" WHERE "userId" = %s AND "tripId" = %s', (user_id, trip_id))
        if cur.fetchone():
            return jsonify({"error": "You have already made a prediction for this trip"}), 409

        cur.execute(
            'INSERT INTO "predictions" ("userId", "tripId", "predictedOutcome") VALUES (%s, %s, %s) RETURNING "id"',
            (user_id, trip_id, predicted_outcome)
        )
        prediction_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        return jsonify({'id': prediction_id}), 201
    except psycopg2.Error as e:
        conn.rollback()
        cur.close()
        return jsonify({"error": str(e)}), 500

@predictions_bp.route('', methods=['GET'])
@jwt_required()
def get_predictions():
    user_id = get_jwt_identity()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT "id", "tripId", "predictedOutcome", "createdAt" FROM "predictions" WHERE "userId" = %s;', (user_id,))
    predictions = [{"id": row[0], "tripId": row[1], "predictedOutcome": row[2], "createdAt": row[3]} for row in cur.fetchall()]
    cur.close()
    return jsonify(predictions)
