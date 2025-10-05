import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
import os
import requests
import random
import hashlib

df=pd.read_csv("gtfs_realtime.csv")
# 1. Drop only arrival & departure delays. Keep stop_id, stop_sequence, timestamp for model features
df2 = df.drop(columns=["arrival_delay", "departure_delay"])

# 2. Features (everything except delayed)
X = df2.drop(columns=["delayed"])
y = df2["delayed"]

# 3. Encode categorical feature columns to numeric codes (mirror inference step)
for col in X.columns:
    if X[col].dtype == object:
        X[col] = X[col].astype("category").cat.codes

# 3b. Basic NA handling to avoid estimator issues
X = X.fillna(-1)

# 4. Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
 
# 5. Train model
models = {
    "RandomForest": RandomForestClassifier(),
    "LogisticRegression": make_pipeline(SimpleImputer(strategy="most_frequent"), LogisticRegression(max_iter=1000)),
    "XGBoost": XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss"   # prevents warnings
    )
}

for name, m in models.items():
    m.fit(X_train, y_train)
    preds = m.predict(X_test)
    print(f"\n=== {name} ===")
    print("Accuracy:", accuracy_score(y_test, preds))
    print("Classification Report:\n", classification_report(y_test, preds))



# Credentials per model
CREDENTIALS = {
    "RandomForest": ("rf_user@example.com", "rf_pass123"),
    "LogisticRegression": ("lr_user@example.com", "lr_pass123"),
    "XGBoost": ("xgb_user@example.com", "xgb_pass123")
}

# Backend integration helpers
BASE_URL = os.environ.get("BACKEND_BASE_URL", "http://localhost:8000")

def login_and_get_token(email: str, password: str) -> str:
    url = f"{BASE_URL}/auth/login"
    resp = requests.post(url, json={"email": email, "password": password}, timeout=15)
    if resp.status_code != 200:
        print(f"Login failed for {email}. Status {resp.status_code}: {resp.text}")
        return ""
    data = resp.json()
    return data.get("access_token", "")

def register_user(email: str, password: str, nickname: str) -> bool:
    url = f"{BASE_URL}/auth/register"
    payload = {"email": email, "password": password, "nickname": nickname}
    try:
        resp = requests.post(url, json=payload, timeout=15)
    except Exception as e:
        print(f"Register request failed for {email}: {e}")
        return False
    if resp.status_code == 201:
        print(f"Registered user {email} ({nickname})")
        return True
    if resp.status_code == 409:
        # already exists, fine
        return True
    print(f"Register failed for {email}. Status {resp.status_code}: {resp.text}")
    return False

def post_prediction(token: str, trip_id: str, service_date: str, predicted_outcome: str):
    url = f"{BASE_URL}/predictions"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "trip_id": trip_id,
        "service_date": service_date,  # must be YYYY-MM-DD
        "predicted_outcome": predicted_outcome  # one of: on_time, late, early
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=15)
    if resp.status_code not in (200, 201):
        print(f"Failed to submit prediction for trip {trip_id} on {service_date}. Status {resp.status_code}: {resp.text}")
    else:
        print(f"Submitted prediction for {trip_id} on {service_date}: {predicted_outcome}")

# Helper: convert date + time -> Unix timestamp
def to_timestamp(service_date, time_str):
    try:
        dt = pd.to_datetime(service_date.strip() + " " + time_str.strip())
        return int(dt.timestamp())
    except:
        return -1  # fallback if parsing fails

def run_daily_predictions():
    # Fetch today's trips once
    trips_resp = requests.get(f"{BASE_URL}/trips", timeout=20)
    if trips_resp.status_code != 200:
        print("Failed to fetch trips. Status:", trips_resp.status_code, trips_resp.text)
        return
    trips = trips_resp.json()
    if not trips:
        print("No trips available today.")
        return

    for name, m in models.items():
        email, pwd = CREDENTIALS[name]
        nickname = f"{name.lower()}_bot"
        print(f"\n=== Predicting with {name} as {email} ===")

        # Ensure a user exists for this model
        register_user(email, pwd, nickname)

        token = login_and_get_token(email, pwd)
        if not token:
            print(f"Skipping {name}: login failed")
            continue

        sample_trips = random.sample(trips, min(5, len(trips)))

        # Build features for the selected trips
        rows = []
        for t in sample_trips:
            synthetic_stop_id = int(hashlib.md5(t["first_stop"].encode()).hexdigest(), 16) % 10000
            timestamp = to_timestamp(t["service_date"], t["first_stop_arrival_time"])

            rows.append({
                "route_id": t["route_id"],
                "direction_id": t["direction_id"],
                "stop_id": synthetic_stop_id,
                "stop_sequence": 0,
                "vehicle_id": -1,
                "timestamp": timestamp
            })

        X_new = pd.DataFrame(rows)

        # Encode categories like before
        for col in X_new.columns:
            if X_new[col].dtype == object:
                X_new[col] = X_new[col].astype("category").cat.codes

        # Ensure same feature columns/order as training
        X_new = X_new.reindex(columns=X.columns, fill_value=0).fillna(-1)

        preds = m.predict(X_new)

        print("\nPredictions on 5 sampled trips:")
        for trip, pred in zip(sample_trips, preds):
            outcome = 'late' if int(pred) == 1 else 'on_time'
            print(f"Trip {trip['trip_id']} | Route {trip['route_id']} -> {outcome.upper()}")
            # Submit prediction to backend
            post_prediction(token, trip['trip_id'], trip['service_date'], outcome)

if __name__ == "__main__":
    run_daily_predictions()
