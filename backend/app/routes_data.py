import os
from flask import Blueprint, jsonify
import pandas as pd

routes_data_bp = Blueprint('routes_data', __name__, url_prefix='/routes')

@routes_data_bp.route('/<int:route_id>/trips', methods=['GET'])
def get_route_trips(route_id):
    try:
        # Load GTFS data
        trips_df = pd.read_csv('static_data/trips.txt')
        routes_df = pd.read_csv('static_data/routes.txt')
        stop_times_df = pd.read_csv('static_data/stop_times.txt')

        # Convert route_id to numeric
        trips_df['route_id'] = pd.to_numeric(trips_df['route_id'], errors='coerce')
        routes_df['route_id'] = pd.to_numeric(routes_df['route_id'], errors='coerce')

        # Get route name
        route_info = routes_df[routes_df['route_id'] == route_id]
        if route_info.empty:
            return jsonify({"error": "Route not found"}), 404
        route_name = route_info.iloc[0]['route_long_name']

        # Get trips for the route
        route_trips = trips_df[trips_df['route_id'] == route_id]
        trip_ids = route_trips['trip_id'].unique()

        if len(trip_ids) == 0:
            return jsonify({"trips": [], "route_name": route_name})

        # Get stop times for the trips
        trip_stop_times = stop_times_df[stop_times_df['trip_id'].isin(trip_ids)]

        # Format the response
        trips_data = []
        for trip_id in trip_ids:
            trip_stops = trip_stop_times[trip_stop_times['trip_id'] == trip_id].sort_values(by='stop_sequence')
            if not trip_stops.empty:
                first_stop = trip_stops.iloc[0].to_dict()
                last_stop = trip_stops.iloc[-1].to_dict()
                stops = [first_stop, last_stop]
            else:
                stops = []
            
            trips_data.append({
                "trip_id": int(trip_id),
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
