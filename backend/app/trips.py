import os
import pandas as pd
from flask import Blueprint, jsonify
from sqlalchemy import create_engine
from datetime import datetime, timedelta

# Blueprint definition
trips_bp = Blueprint('trips', __name__, url_prefix='/trips')

# Global DataFrames to hold the data
trips_df = pd.DataFrame()
stops_df = pd.DataFrame()
routes_df = pd.DataFrame()
calendar_df = pd.DataFrame()
stop_times_df = pd.DataFrame()
trips_with_stops_df = pd.DataFrame()

def get_db_connection():
    # This function is needed for update_scores
    import psycopg2
    import os
    return psycopg2.connect(
        host=os.environ.get('POSTGRES_HOST'),
        database=os.environ.get('POSTGRES_DB'),
        user=os.environ.get('POSTGRES_USER'),
        password=os.environ.get('POSTGRES_PASSWORD')
    )

def update_scores(trip_id: str, service_date: datetime.date, outcome: str):
    """Awards points to users who predicted correctly."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Get predictions for this trip and service_date
            cur.execute('SELECT user_id, predicted_outcome FROM predictions WHERE trip_id = %s AND service_date = %s', (trip_id, service_date))
            predictions = cur.fetchall()

            for user_id, predicted_outcome in predictions:
                if predicted_outcome == outcome:
                    cur.execute('UPDATE users SET cumulative_score = cumulative_score + 1 WHERE id = %s', (user_id,))
            conn.commit()
            print(f"Scores updated for trip {trip_id} on {service_date} with outcome {outcome}")
    except Exception as e:
        conn.rollback()
        print(f"Error updating scores: {e}")
    finally:
        if conn:
            conn.close()

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

        # Convert service_date to datetime objects
        trips_df['service_date'] = pd.to_datetime(trips_df['service_date']).dt.date
        stop_times_df['service_date'] = pd.to_datetime(stop_times_df['service_date']).dt.date

        print("Successfully loaded data from the database.")
        print(f"trips_df columns before filter: {trips_df.columns.tolist()}")
        print(f"trips_df shape before filter: {trips_df.shape}")

        # --- Filter trips for a relevant date range ---
        today = datetime.now().date()
        future_days = 0 # Load trips for today only
        date_filter_start = today
        date_filter_end = today + timedelta(days=future_days)

        trips_df = trips_df[(trips_df['service_date'] >= date_filter_start) & (trips_df['service_date'] <= date_filter_end)]
        valid_trip_ids_dates = trips_df[['trip_id', 'service_date']].drop_duplicates()
        
        stop_times_df = pd.merge(stop_times_df, valid_trip_ids_dates, on=['trip_id', 'service_date'], how='inner')
        # --- End Filter trips ---

        print(f"trips_df columns after filter: {trips_df.columns.tolist()}")
        print(f"trips_df shape after filter: {trips_df.shape}")

        # Pre-calculate the trips with stops dataframe
        # Group by both trip_id and service_date
        first_stops = stop_times_df.loc[stop_times_df.groupby(['trip_id', 'service_date'])['stop_sequence'].idxmin()]
        last_stops = stop_times_df.loc[stop_times_df.groupby(['trip_id', 'service_date'])['stop_sequence'].idxmax()]

        first_stops = pd.merge(first_stops, stops_df, on='stop_id', how='left')
        last_stops = pd.merge(last_stops, stops_df, on='stop_id', how='left')

        trips_with_stops = pd.merge(trips_df, first_stops[['trip_id', 'service_date', 'stop_name', 'arrival_time']], on=['trip_id', 'service_date'], how='left')
        trips_with_stops.rename(columns={'stop_name': 'first_stop', 'arrival_time': 'first_stop_arrival_time'}, inplace=True)
        
        trips_with_stops_df = pd.merge(trips_with_stops, last_stops[['trip_id', 'service_date', 'stop_name', 'arrival_time']], on=['trip_id', 'service_date'], how='left')
        trips_with_stops_df.rename(columns={'stop_name': 'last_stop', 'arrival_time': 'last_stop_arrival_time'}, inplace=True)

        print("Successfully pre-calculated trips with stops.")

    except Exception as e:
        print(f"Error loading data from database: {e}")

@trips_bp.route('', methods=['GET'])
def get_trips():
    """Returns a list of trips with their first and last stops."""
    if trips_with_stops_df.empty:
        return jsonify({"error": "Data not loaded"}), 500

    # Convert arrival times to timedelta for sorting
    trips_output = trips_with_stops_df.copy()
    trips_output['first_stop_arrival_timedelta'] = trips_output['first_stop_arrival_time'].apply(lambda x: sum(int(i) * 60 ** idx for idx, i in enumerate(reversed(x.split(':')))) if pd.notna(x) else pd.NaT)
    
    # Sort by first_stop_arrival_timedelta
    trips_output = trips_output.sort_values(by='first_stop_arrival_timedelta').drop(columns=['first_stop_arrival_timedelta'])

    # Convert service_date to string for JSON serialization
    trips_output['service_date'] = trips_output['service_date'].astype(str)
    return jsonify(trips_output.to_dict(orient='records'))

@trips_bp.route('/<string:trip_id>/<string:service_date>', methods=['GET'])
def get_trip(trip_id: str, service_date: str):
    """Returns the details of a single trip."""
    if trips_df.empty:
        return jsonify({"error": "Data not loaded"}), 500

    # Convert service_date string to date object for comparison
    service_date_obj = datetime.strptime(service_date, '%Y-%m-%d').date()

    trip_details = trips_df[(trips_df['trip_id'] == trip_id) & (trips_df['service_date'] == service_date_obj)]

    if trip_details.empty:
        return jsonify({"error": "Trip not found"}), 404

    # Convert service_date to string for JSON serialization
    trip_output = trip_details.copy()
    trip_output['service_date'] = trip_output['service_date'].astype(str)
    return jsonify(trip_output.to_dict(orient='records')[0])