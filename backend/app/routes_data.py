import os
from flask import Blueprint, jsonify
import pandas as pd
from .auth.routes import get_db_connection
import psycopg2.extras

routes_data_bp = Blueprint('routes_data', __name__, url_prefix='/routes')

@routes_data_bp.route('/<int:route_id>/trips', methods=['GET'])
def get_route_trips(route_id):
    try:
        # Load GTFS data for route name
        routes_df = pd.read_csv('static_data/routes.txt')
        routes_df['route_id'] = pd.to_numeric(routes_df['route_id'], errors='coerce')
        route_info = routes_df[routes_df['route_id'] == route_id]
        if route_info.empty:
            return jsonify({"error": "Route not found"}), 404
        route_short_name = route_info.iloc[0].get('route_short_name', '')
        route_long_name = route_info.iloc[0].get('route_long_name', '')
        route_name = f"{route_short_name} {route_long_name}".strip()

        # Get trips from the database
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('SELECT "name", "headsign" FROM "trips" WHERE "route_id" = %s', (route_id,))
        trips = cur.fetchall()
        cur.close()
        conn.close()

        if not trips:
            return jsonify({"trips": [], "route_name": route_name})

        trip_ids = [trip['name'] for trip in trips]
        # Get stop times for the trips
        stop_times_df = pd.read_csv('static_data/stop_times.txt')
        # The trip_id in stop_times.txt might be integer, but in our db it is string.
        # Let's convert trip_ids from db to int for comparison
        trip_ids_int = [int(tid) for tid in trip_ids]
        trip_stop_times = stop_times_df[stop_times_df['trip_id'].isin(trip_ids_int)]

        # Format the response
        trips_data = []
        for trip in trips:
            trip_id = int(trip['name'])
            trip_stops = trip_stop_times[trip_stop_times['trip_id'] == trip_id].sort_values(by='stop_sequence')
            if not trip_stops.empty:
                first_stop = trip_stops.iloc[0].to_dict()
                last_stop = trip_stops.iloc[-1].to_dict()
                stops = [first_stop, last_stop]
            else:
                stops = []
            
            trips_data.append({
                "trip_id": trip_id,
                "headsign": trip['headsign'],
                "stop_times": stops
            })

        return jsonify({
            "route_id": route_id,
            "route_name": route_name,
            "trips": trips_data
        })

    except FileNotFoundError:
        return jsonify({"error": "GTFS data not found"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500