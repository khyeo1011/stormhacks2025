import requests
from google.protobuf.json_format import MessageToDict
from google.transit import gtfs_realtime_pb2
import pandas as pd

api_key="YIfpfuaHJyiHPSTdNyZn"
url=f"https://gtfsapi.translink.ca/v3/gtfsrealtime?apikey={api_key}"

response = requests.get(url)

# Parse protobuf
feed = gtfs_realtime_pb2.FeedMessage()
feed.ParseFromString(response.content)
rows = []

for entity in feed.entity:
    if not entity.HasField("trip_update"):
        continue

    tu = entity.trip_update
    trip = tu.trip
    vehicle = tu.vehicle if tu.HasField("vehicle") else None

    for stop in tu.stop_time_update:
        rows.append({
            "trip_id": trip.trip_id,               
            "route_id": trip.route_id,       
            "direction_id": trip.direction_id,  
            "stop_id": stop.stop_id,           
            "stop_sequence": stop.stop_sequence, 
            "vehicle_id": vehicle.id if vehicle else None,
            "arrival_delay": stop.arrival.delay if stop.HasField("arrival") else None,
            "departure_delay": stop.departure.delay if stop.HasField("departure") else None,
            "timestamp": stop.arrival.time if stop.HasField("arrival") else None,
            "delayed": 1 if (stop.arrival.delay if stop.HasField("arrival") else 0) > 0 else 0
        })

df = pd.DataFrame(rows)
print(df.head())

df.to_csv("gtfs_realtime.csv", index=False)
