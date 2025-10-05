#!/bin/bash

echo "Testing duplicate prediction error message..."

# First, let's register a test user and get a token
echo "1. Registering test user..."
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "nickname": "testuser"
  }')

echo "Register response: $REGISTER_RESPONSE"

# Login to get token
echo "2. Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }')

echo "Login response: $LOGIN_RESPONSE"

# Extract token
TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "Token: $TOKEN"

if [ -z "$TOKEN" ]; then
  echo "Failed to get token. Trying to login again..."
  LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/auth/login \
    -H "Content-Type: application/json" \
    -d '{
      "email": "test@example.com",
      "password": "testpass123"
    }')
  echo "Second login attempt: $LOGIN_RESPONSE"
  TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
fi

if [ -z "$TOKEN" ]; then
  echo "ERROR: Could not get authentication token"
  exit 1
fi

# Get available trips first
echo "3. Getting available trips..."
TRIPS_RESPONSE=$(curl -s -X GET http://localhost:8000/trips \
  -H "Authorization: Bearer $TOKEN")

echo "Trips response: $TRIPS_RESPONSE"

# Extract first trip_id
TRIP_ID=$(echo $TRIPS_RESPONSE | grep -o '"trip_id":"[^"]*' | head -1 | cut -d'"' -f4)
echo "First trip ID: $TRIP_ID"

if [ -z "$TRIP_ID" ]; then
  echo "ERROR: Could not get trip ID"
  exit 1
fi

# Extract service_date
SERVICE_DATE=$(echo $TRIPS_RESPONSE | grep -o '"service_date":"[^"]*' | head -1 | cut -d'"' -f4)
echo "Service date: $SERVICE_DATE"

if [ -z "$SERVICE_DATE" ]; then
  echo "ERROR: Could not get service date"
  exit 1
fi

# Make first prediction
echo "4. Making first prediction..."
FIRST_PREDICTION=$(curl -s -X POST http://localhost:8000/simple-predictions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"trip_id\": \"$TRIP_ID\",
    \"service_date\": \"$SERVICE_DATE\",
    \"predicted_outcome\": \"on_time\"
  }")

echo "First prediction response: $FIRST_PREDICTION"

# Make duplicate prediction
echo "5. Making duplicate prediction..."
DUPLICATE_PREDICTION=$(curl -s -X POST http://localhost:8000/simple-predictions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"trip_id\": \"$TRIP_ID\",
    \"service_date\": \"$SERVICE_DATE\",
    \"predicted_outcome\": \"late\"
  }")

echo "Duplicate prediction response: $DUPLICATE_PREDICTION"

# Check if error message is present
if echo "$DUPLICATE_PREDICTION" | grep -q "already made a prediction"; then
  echo "✅ SUCCESS: Duplicate prediction error message is working!"
else
  echo "❌ FAILURE: Duplicate prediction error message is NOT working"
  echo "Expected error message about duplicate prediction"
fi
