import pandas as pd

def find_trip_stop_times(route_id):
    """
    Finds trip IDs and stop times for a given route ID.

    Args:
        route_id: The route ID to search for.
    """
    try:
        # Load the GTFS data
        trips_df = pd.read_csv('backend/static_data/trips.txt')
        stop_times_df = pd.read_csv('backend/static_data/stop_times.txt')

        # Convert route_id to numeric
        trips_df['route_id'] = pd.to_numeric(trips_df['route_id'], errors='coerce')

        # Find the trips for the given route
        route_trips = trips_df[trips_df['route_id'] == route_id]
        trip_ids = route_trips['trip_id'].unique()

        if len(trip_ids) == 0:
            print(f"No trips found for route ID {route_id}")
            return

        print(f"Found {len(trip_ids)} trips for route ID {route_id}:")
        print(trip_ids)

        # Find the stop times for those trips
        trip_stop_times = stop_times_df[stop_times_df['trip_id'].isin(trip_ids)]

        print(f"\nStop times for the trips on route {route_id}:")
        print(trip_stop_times)

    except FileNotFoundError as e:
        print(f"Error: {e}. Make sure the GTFS files are in the 'backend/static_data' directory.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    # The user wants to find the trip ids for the trips in routeID 37807
    find_trip_stop_times(37807)
