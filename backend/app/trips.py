import os
import pandas as pd
from flask import Blueprint, jsonify
from sqlalchemy import create_engine

# Blueprint definition
trips_bp = Blueprint('trips', __name__, url_prefix='/trips')

# Global DataFrames to hold the data
trips_df = pd.DataFrame()
stops_df = pd.DataFrame()
routes_df = pd.DataFrame()
calendar_df = pd.DataFrame()
stop_times_df = pd.DataFrame()
trips_with_stops_df = pd.DataFrame()

def load_data_from_db():
    """Loads all necessary data from the database into global pandas DataFrames."""
    global trips_df, stops_df, routes_df, calendar_df, stop_times_df, trips_with_stops_df

    db_user = os.environ.get("POSTGRES_USER")
    db_password = os.environ.get("POSTGRES_PASSWORD")
    db_host = os.environ.get("POSTGRES_HOST")
    db_name = os.environ.get("POSTGRES_DB")

    db_url = f'postgresql://{db_user}:{db_password}@{db_host}/{db_name}'
    engine = create_engine(db_url)

    try:
        stops_df = pd.read_sql('SELECT * FROM stops', engine)
        routes_df = pd.read_sql('SELECT * FROM routes', engine)
        calendar_df = pd.read_sql('SELECT * FROM calendar', engine)
        trips_df = pd.read_sql('SELECT * FROM trips', engine)
        stop_times_df = pd.read_sql('SELECT * FROM stop_times', engine)

        print("Successfully loaded data from the database.")

        # Pre-calculate the trips with stops dataframe
        first_stops = stop_times_df.loc[stop_times_df.groupby('trip_id')['stop_sequence'].idxmin()]
        last_stops = stop_times_df.loc[stop_times_df.groupby('trip_id')['stop_sequence'].idxmax()]

        first_stops = pd.merge(first_stops, stops_df, on='stop_id', how='left')
        last_stops = pd.merge(last_stops, stops_df, on='stop_id', how='left')

        trips_with_stops = pd.merge(trips_df, first_stops[['trip_id', 'stop_name', 'arrival_time']], on='trip_id', how='left')
        trips_with_stops.rename(columns={'stop_name': 'first_stop', 'arrival_time': 'first_stop_arrival_time'}, inplace=True)
        
        trips_with_stops_df = pd.merge(trips_with_stops, last_stops[['trip_id', 'stop_name', 'arrival_time']], on='trip_id', how='left')
        trips_with_stops_df.rename(columns={'stop_name': 'last_stop', 'arrival_time': 'last_stop_arrival_time'}, inplace=True)

        print("Successfully pre-calculated trips with stops.")

    except Exception as e:
        print(f"Error loading data from database: {e}")

@trips_bp.route('', methods=['GET'])
def get_trips():
    """Returns a list of trips with their first and last stops."""
    if trips_with_stops_df.empty:
        return jsonify({"error": "Data not loaded"}), 500

    return jsonify(trips_with_stops_df.to_dict(orient='records'))

@trips_bp.route('/<string:trip_id>', methods=['GET'])
def get_trip(trip_id):
    """Returns the details of a single trip."""
    if trips_df.empty:
        return jsonify({"error": "Data not loaded"}), 500

    trip_details = trips_df[trips_df['trip_id'] == trip_id]

    if trip_details.empty:
        return jsonify({"error": "Trip not found"}), 404

    return jsonify(trip_details.to_dict(orient='records')[0])
