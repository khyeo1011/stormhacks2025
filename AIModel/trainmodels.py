import requests
import random
import hashlib
import numpy as np
import pandas as pd

# Credentials per model
CREDENTIALS = {
    "RandomForest": ("rf_user@example.com", "rf_pass123"),
    "LogisticRegression": ("lr_user@example.com", "lr_pass123"),
    "XGBoost": ("xgb_user@example.com", "xgb_pass123")
}

# Helper: convert date + time -> Unix timestamp
def to_timestamp(service_date, time_str):
    try:
        dt = pd.to_datetime(service_date.strip() + " " + time_str.strip())
        return int(dt.timestamp())
    except:
        return -1  # fallback if parsing fails

# Loop through each model and make predictions on 5 random trips
for name, m in models.items():

    email, pwd = CREDENTIALS[name]
    print(f"\n=== Predicting with {name} as {email} ===")

    response = requests.get("http://localhost:8000/trips", auth=(email, pwd))

    if response.status_code != 200:
        print(f"Failed to fetch trips for {name}. Status:", response.status_code)
        continue

    trips = response.json()
    sample_trips = random.sample(trips, min(5, len(trips)))

    # Convert trips to model input format
    rows = []
    for t in sample_trips:
        synthetic_stop_id = int(hashlib.md5(t["first_stop"].encode()).hexdigest(), 16) % 10000
        timestamp = to_timestamp(t["service_date"], t["first_stop_arrival_time"])

        rows.append({
            "route_id": t["route_id"],
            "direction_id": t["direction_id"],
            "stop_id": synthetic_stop_id,     # placeholder
            "stop_sequence": 0,               # first stop
            "vehicle_id": -1,                 # unknown
            "timestamp": timestamp            # inferred
        })

    X_new = pd.DataFrame(rows)

    # Encode categories like before
    for col in X_new.columns:
        if X_new[col].dtype == object:
            X_new[col] = X_new[col].astype("category").cat.codes

    preds = m.predict(X_new)

    print("\nPredictions on 5 sampled trips:")
    for trip, pred in zip(sample_trips, preds):
        print(f"Trip {trip['trip_id']} | Route {trip['route_id']} -> {'DELAYED' if pred == 1 else 'ON TIME'}")
