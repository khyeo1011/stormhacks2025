import os
from flask import Blueprint, jsonify, request, g
from flask_jwt_extended import jwt_required, get_jwt_identity
import psycopg2

from .auth.routes import get_db_connection

trips_bp = Blueprint('trips', __name__, url_prefix='/trips')

@trips_bp.route('', methods=['POST'])
@jwt_required()
def create_trip():
    # This endpoint could be restricted to admins
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    if not name:
        return jsonify({"error": "name is required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            'INSERT INTO "trips" ("name", "description") VALUES (%s, %s) RETURNING "id"',
            (name, description)
        )
        trip_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        return jsonify({'id': trip_id}), 201
    except psycopg2.Error as e:
        conn.rollback()
        cur.close()
        return jsonify({"error": str(e)}), 500

@trips_bp.route('', methods=['GET'])
def get_trips():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT "id", "name", "description", "outcome", "createdAt" FROM "trips";')
    trips = [{"id": row[0], "name": row[1], "description": row[2], "outcome": row[3], "createdAt": row[4]} for row in cur.fetchall()]
    cur.close()
    return jsonify(trips)

@trips_bp.route('/<int:trip_id>', methods=['GET'])
def get_trip(trip_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT "id", "name", "description", "outcome", "createdAt" FROM "trips" WHERE "id" = %s;', (trip_id,))
    trip = cur.fetchone()
    cur.close()
    if trip:
        return jsonify({"id": trip[0], "name": trip[1], "description": trip[2], "outcome": trip[3], "createdAt": trip[4]})
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

        # Award points to users who predicted correctly
        cur.execute('SELECT "userId" FROM "predictions" WHERE "tripId" = %s AND "predictedOutcome" = %s', (trip_id, outcome))
        winners = cur.fetchall()
        for winner in winners:
            user_id = winner[0]
            cur.execute('UPDATE "users" SET "cumulativeScore" = "cumulativeScore" + 1 WHERE "id" = %s', (user_id,))

        conn.commit()
        cur.close()
        return jsonify({"msg": "Trip resolved and scores updated"}), 200
    except psycopg2.Error as e:
        conn.rollback()
        cur.close()
        return jsonify({"error": str(e)}), 500
