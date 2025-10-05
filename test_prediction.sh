#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Clean up and start services ---

echo "--- Cleaning up and starting services ---"
docker-compose down -v
docker-compose up -d
echo "--- Waiting for services to start ---"
sleep 10

# --- Configuration -- - 
BASE_URL="http://localhost:8000"
EMAIL="test-user-$(date +%s)@example.com"
PASSWORD="password"
NICKNAME="TestUser"
VALID_TRIP_ID=14734177

# --- Helper Functions ---
check_deps() {
    command -v curl >/dev/null 2>&1 || { echo >&2 "curl is required but it's not installed. Aborting."; exit 1; }
    command -v jq >/dev/null 2>&1 || { echo >&2 "jq is required but it's not installed. Aborting."; exit 1; }
}

# --- Main Script ---
check_deps

echo "--- Starting Prediction Logic Test ---"

# 1. Create a user
echo "1. Creating user..."
USER_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
  -d @- \
  "$BASE_URL/auth/register" << EOF
{
    "email": "$EMAIL",
    "password": "$PASSWORD",
    "nickname": "$NICKNAME"
}
EOF
)
USER_ID=$(echo "$USER_RESPONSE" | jq -r .id)
echo "   - User created with ID: $USER_ID"

# 2. Log in as the user
echo "2. Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
  -d @- \
  "$BASE_URL/auth/login" << EOF
{
    "email": "$EMAIL",
    "password": "$PASSWORD"
}
EOF
)
TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r .access_token)
echo "   - Logged in successfully."

# 3. Try to create a trip with a tripId from a different route (should fail)
echo "3. Trying to create a trip from a wrong route (should fail)..."
INVALID_TRIP_ID=14672431 
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d @- \
  "$BASE_URL/trips" << EOF
{
    "tripId": $INVALID_TRIP_ID
}
EOF
)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
if [ "$HTTP_CODE" -ne 403 ]; then
  echo "   - FAILURE: Expected HTTP 403, but got $HTTP_CODE"
  exit 1
fi
echo "   - SUCCESS: Received HTTP 403 as expected."

# 4. Create a trip with a tripId from route 37807 (should succeed)
echo "4. Creating a trip from route 37807 (should succeed)..."
VALID_TRIP_ID=14734177
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d @- \
  "$BASE_URL/trips" << EOF
{
    "tripId": $VALID_TRIP_ID
}
EOF
)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n -1)
if [ "$HTTP_CODE" -ne 201 ]; then
  echo "   - FAILURE: Expected HTTP 201, but got $HTTP_CODE. Body: $BODY"
  exit 1
fi
TRIP_ID=$(echo "$BODY" | jq -r .id)
echo "   - SUCCESS: Trip created with ID: $TRIP_ID"

# 5. Get trips for route 37807
echo "5. Getting trips for route 37807..."
curl -s -X GET "$BASE_URL/routes/37807/trips" | jq .

# 6. Create a prediction
echo "6. Creating a prediction..."
PREDICTION_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d @- \
  "$BASE_URL/predictions" << EOF
{
    "tripId": $TRIP_ID,
    "predictedOutcome": "on-time"
}
EOF
)
echo "   - Prediction created: $PREDICTION_RESPONSE"

# 7. Run the resolver
echo "7. Running the resolver script..."
docker-compose run --rm backend python app/resolver.py --force

# 8. Check the user's score
echo "8. Checking user's score..."
USER_INFO=$(curl -s -X GET -H "Authorization: Bearer $TOKEN" "$BASE_URL/auth/users")
SCORE=$(echo "$USER_INFO" | jq -r --argjson id "$USER_ID" '.[] | select(.id == $id) | .cumulativeScore')
if [ "$SCORE" -eq 1 ]; then
    echo "   - SUCCESS: User score is 1."
else
    echo "   - FAILURE: User score is not 1, it is $SCORE."
    exit 1
fi

echo "--- Prediction Logic Test Complete ---"