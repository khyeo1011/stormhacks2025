#!/bin/bash

# This script tests the friend request functionality of the API.
# It requires jq to be installed (https://stedolan.github.io/jq/).

# --- User Data ---
EMAIL_A="alice@example.com"
PASSWORD_A="passwordA"
NICKNAME_A="Alice"

EMAIL_B="bob@example.com"
PASSWORD_B="passwordB"
NICKNAME_B="Bob"

# --- API Base URL ---
BASE_URL="http://localhost:8000"

echo "--- Starting Friend Request Test ---"

# 1. Create two users
echo "1. Creating users Alice and Bob..."
USER_A_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"email": "'$EMAIL_A'", "password": "'$PASSWORD_A'", "nickname": "'$NICKNAME_A'"}' \
  $BASE_URL/auth/register)
USER_ID_A=$(echo $USER_A_RESPONSE | jq -r .id)

USER_B_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"email": "'$EMAIL_B'", "password": "'$PASSWORD_B'", "nickname": "'$NICKNAME_B'"}' \
  $BASE_URL/auth/register)
USER_ID_B=$(echo $USER_B_RESPONSE | jq -r .id)

echo "   - Alice created with ID: $USER_ID_A"
echo "   - Bob created with ID: $USER_ID_B"

# 2. Log in as both users to get their tokens
echo "2. Logging in as Alice and Bob..."
LOGIN_A_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"email": "'$EMAIL_A'", "password": "'$PASSWORD_A'"}' \
  $BASE_URL/login)
TOKEN_A=$(echo $LOGIN_A_RESPONSE | jq -r .access_token)

LOGIN_B_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"email": "'$EMAIL_B'", "password": "'$PASSWORD_B'"}' \
  $BASE_URL/login)
TOKEN_B=$(echo $LOGIN_B_RESPONSE | jq -r .access_token)

# 3. Alice sends a friend request to Bob
echo "3. Alice is sending a friend request to Bob..."
curl -s -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_A" \
  -d '{"receiver_id": '$USER_ID_B'}' \
  $BASE_URL/auth/friend-requests

# 4. Bob checks his pending friend requests
echo "4. Bob is checking his pending requests..."
PENDING_REQUESTS=$(curl -s -X GET -H "Authorization: Bearer $TOKEN_B" \
  $BASE_URL/auth/friend-requests/pending)

echo "   - Pending requests for Bob: $PENDING_REQUESTS"

# Check if Alice's request is in Bob's pending requests
if echo "$PENDING_REQUESTS" | jq -e '.[] | select(.sender_id == '$USER_ID_A')' > /dev/null; then
  echo "   - SUCCESS: Alice's request found in Bob's pending list."
else
  echo "   - FAILURE: Alice's request not found."
  exit 1
fi

# 5. Bob accepts Alice's friend request
echo "5. Bob is accepting Alice's friend request..."
curl -s -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_B" \
  -d '{"sender_id": '$USER_ID_A', "action": "accept"}' \
  $BASE_URL/auth/friend-requests/handle

# 6. Bob checks his friends list
echo "6. Bob is checking his friends list..."
BOB_FRIENDS=$(curl -s -X GET -H "Authorization: Bearer $TOKEN_B" \
  $BASE_URL/auth/friends)

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
  $BASE_URL/auth/friends)

echo "   - Alice's friends: $ALICE_FRIENDS"

if echo "$ALICE_FRIENDS" | jq -e '.[] | select(.id == '$USER_ID_B')' > /dev/null; then
  echo "   - SUCCESS: Bob is in Alice's friends list."
else
  echo "   - FAILURE: Bob is not in Alice's friends list."
  exit 1
fi

echo "--- Test Complete: All checks passed! ---"
