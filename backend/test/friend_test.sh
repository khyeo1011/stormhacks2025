#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Helper Functions ---
check_deps() {
  echo "--- Checking for dependencies (curl, jq) ---"
  if ! command -v curl &> /dev/null; then
    echo "curl could not be found. Please install it."
    exit 1
  fi
  if ! command -v jq &> /dev/null; then
    echo "jq could not be found. Please install it."
    exit 1
  fi
  echo "--- Dependencies found ---"
}

# --- Configuration ---
BASE_URL="http://localhost:8000"
EMAIL_A="alice-$(date +%s)@example.com"
PASSWORD_A="passwordA"
NICKNAME_A="Alice"

EMAIL_B="bob-$(date +%s)@example.com"
PASSWORD_B="passwordB"
NICKNAME_B="Bob"

# --- Main Script ---
check_deps

echo "--- Starting Friend Request Test ---"

# 1. Create two users with unique emails to ensure idempotency
echo "1. Creating users Alice and Bob..."
USER_A_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"email": "'$EMAIL_A'", "password": "'$PASSWORD_A'", "nickname": "'$NICKNAME_A'"}' \
  "$BASE_URL/auth/register")
echo "   - Server response for Alice: $USER_A_RESPONSE"
USER_ID_A=$(echo "$USER_A_RESPONSE" | jq -r .id)

USER_B_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"email": "'$EMAIL_B'", "password": "'$PASSWORD_B'", "nickname": "'$NICKNAME_B'"}' \
  "$BASE_URL/auth/register")
echo "   - Server response for Bob: $USER_B_RESPONSE"
USER_ID_B=$(echo "$USER_B_RESPONSE" | jq -r .id)

echo "   - Alice created with ID: $USER_ID_A"
echo "   - Bob created with ID: $USER_ID_B"

# 2. Log in as both users
echo "2. Logging in as Alice and Bob..."
LOGIN_A_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"email": "'$EMAIL_A'", "password": "'$PASSWORD_A'"}' \
  "$BASE_URL/auth/login")
echo "   - Login response for Alice: $LOGIN_A_RESPONSE"
TOKEN_A=$(echo "$LOGIN_A_RESPONSE" | jq -r .access_token)

LOGIN_B_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"email": "'$EMAIL_B'", "password": "'$PASSWORD_B'"}' \
  "$BASE_URL/auth/login")
echo "   - Login response for Bob: $LOGIN_B_RESPONSE"
TOKEN_B=$(echo "$LOGIN_B_RESPONSE" | jq -r .access_token)

echo "   - Alice's Token: $TOKEN_A"
echo "   - Bob's Token: $TOKEN_B"

# 3. Alice sends a friend request to Bob
echo "3. Alice is sending a friend request to Bob..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_A" \
  -d '{"receiverId": '$USER_ID_B'}' \
  "$BASE_URL/auth/friend-requests")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n -1)
echo "   - Response: $BODY (HTTP $HTTP_CODE)"
if [ "$HTTP_CODE" -ne 201 ]; then
  echo "   - FAILURE: Expected HTTP 201, but got $HTTP_CODE"
  exit 1
fi

# 4. Bob checks his pending friend requests
echo "4. Bob is checking his pending requests..."
PENDING_REQUESTS=$(curl -s -X GET -H "Authorization: Bearer $TOKEN_B" \
  "$BASE_URL/auth/friend-requests/pending")
echo "   - Pending requests for Bob: $PENDING_REQUESTS"

if echo "$PENDING_REQUESTS" | jq -e '.[] | select(.senderId == '$USER_ID_A')' > /dev/null; then
  echo "   - SUCCESS: Alice's request found in Bob's pending list."
else
  echo "   - FAILURE: Alice's request not found."
  exit 1
fi

# 5. Bob accepts Alice's friend request
echo "5. Bob is accepting Alice's friend request..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_B" \
  -d '{"senderId": '$USER_ID_A', "action": "accept"}' \
  "$BASE_URL/auth/friend-requests/handle")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n -1)
echo "   - Response: $BODY (HTTP $HTTP_CODE)"
if [ "$HTTP_CODE" -ne 200 ]; then
  echo "   - FAILURE: Expected HTTP 200, but got $HTTP_CODE"
  exit 1
fi

# 6. Bob checks his friends list
echo "6. Bob is checking his friends list..."
BOB_FRIENDS=$(curl -s -X GET -H "Authorization: Bearer $TOKEN_B" \
  "$BASE_URL/auth/friends")
echo "   - Bob's friends: $BOB_FRIENDS"

if echo "$BOB_FRIENDS" | jq -e '.[] | select(.id == '$USER_ID_A')' > /dev/null; then
  echo "   - SUCCESS: Alice is in Bob's friends list."
else
  echo "   - FAILURE: Alice is not in Bob's friends list."
  exit 1
fi

# 7. Alice checks her friends list
echo "7. Alice is checking her friends list..."
ALICE_FRIENDS=$(curl -s -X GET -H "Authorization: Bearer $TOKEN_A" \
  "$BASE_URL/auth/friends")
echo "   - Alice's friends: $ALICE_FRIENDS"

if echo "$ALICE_FRIENDS" | jq -e '.[] | select(.id == '$USER_ID_B')' > /dev/null; then
  echo "   - SUCCESS: Bob is in Alice's friends list."
else
  echo "   - FAILURE: Bob is not in Alice's friends list."
  exit 1
fi

echo "--- Test Complete: All checks passed! ---"
