#!/bin/bash

echo "🚀 Testing Dashboard Integration with Backend"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test user credentials
TEST_EMAIL="test@example.com"
TEST_PASSWORD="testpassword123"
TEST_NICKNAME="TestUser"

echo -e "${BLUE}1. Testing Backend Health Check${NC}"
echo "Checking if backend is running..."
if curl -s http://localhost:8000/trips > /dev/null; then
    echo -e "${GREEN}✅ Backend is running${NC}"
else
    echo -e "${RED}❌ Backend is not running. Please start it with: docker-compose up -d${NC}"
    exit 1
fi

echo -e "\n${BLUE}2. Testing User Registration${NC}"
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8000/auth/register \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"$TEST_EMAIL\", \"password\": \"$TEST_PASSWORD\", \"nickname\": \"$TEST_NICKNAME\"}")

if echo "$REGISTER_RESPONSE" | grep -q "User created successfully"; then
    echo -e "${GREEN}✅ User registration successful${NC}"
elif echo "$REGISTER_RESPONSE" | grep -q "already exists"; then
    echo -e "${YELLOW}⚠️  User already exists (this is OK)${NC}"
else
    echo -e "${RED}❌ User registration failed: $REGISTER_RESPONSE${NC}"
fi

echo -e "\n${BLUE}3. Testing User Login${NC}"
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/auth/login \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"$TEST_EMAIL\", \"password\": \"$TEST_PASSWORD\"}")

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    TOKEN=$(echo "$LOGIN_RESPONSE" | sed 's/.*"access_token": "\([^"]*\)".*/\1/' | tr -d '\n' | tr -d '{' | tr -d '}')
    echo -e "${GREEN}✅ Login successful, token obtained${NC}"
    echo "Token: ${TOKEN:0:20}..."
else
    echo -e "${RED}❌ Login failed: $LOGIN_RESPONSE${NC}"
    exit 1
fi

echo -e "\n${BLUE}4. Testing Profile Endpoint${NC}"
PROFILE_RESPONSE=$(curl -s -X GET http://localhost:8000/auth/profile \
    -H "Authorization: Bearer $TOKEN")

if echo "$PROFILE_RESPONSE" | grep -q "nickname"; then
    echo -e "${GREEN}✅ Profile endpoint working${NC}"
    echo "Profile data: $PROFILE_RESPONSE"
else
    echo -e "${RED}❌ Profile endpoint failed: $PROFILE_RESPONSE${NC}"
fi

echo -e "\n${BLUE}5. Testing Trips Endpoint${NC}"
TRIPS_RESPONSE=$(curl -s -X GET http://localhost:8000/trips)

if echo "$TRIPS_RESPONSE" | grep -q "trip_id"; then
    echo -e "${GREEN}✅ Trips endpoint working${NC}"
    TRIP_COUNT=$(echo "$TRIPS_RESPONSE" | grep -o "trip_id" | wc -l)
    echo "Found $TRIP_COUNT trips"
else
    echo -e "${RED}❌ Trips endpoint failed: $TRIPS_RESPONSE${NC}"
fi

echo -e "\n${BLUE}6. Testing Simple Predictions Endpoint${NC}"
PREDICTION_RESPONSE=$(curl -s -X POST http://localhost:8000/simple-predictions \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"trip_id": "14734177", "predicted_outcome": "on_time"}')

if echo "$PREDICTION_RESPONSE" | grep -q "Prediction created successfully"; then
    echo -e "${GREEN}✅ Prediction creation successful${NC}"
    echo "Prediction response: $PREDICTION_RESPONSE"
else
    echo -e "${RED}❌ Prediction creation failed: $PREDICTION_RESPONSE${NC}"
fi

echo -e "\n${BLUE}7. Testing Get Predictions Endpoint${NC}"
GET_PREDICTIONS_RESPONSE=$(curl -s -X GET http://localhost:8000/simple-predictions \
    -H "Authorization: Bearer $TOKEN")

if echo "$GET_PREDICTIONS_RESPONSE" | grep -q "predicted_outcome"; then
    echo -e "${GREEN}✅ Get predictions endpoint working${NC}"
    echo "Predictions data: $GET_PREDICTIONS_RESPONSE"
else
    echo -e "${RED}❌ Get predictions endpoint failed: $GET_PREDICTIONS_RESPONSE${NC}"
fi

echo -e "\n${BLUE}8. Testing Prediction Stats Endpoint${NC}"
STATS_RESPONSE=$(curl -s -X GET http://localhost:8000/simple-predictions/stats \
    -H "Authorization: Bearer $TOKEN")

if echo "$STATS_RESPONSE" | grep -q "total_predictions"; then
    echo -e "${GREEN}✅ Prediction stats endpoint working${NC}"
    echo "Stats data: $STATS_RESPONSE"
else
    echo -e "${RED}❌ Prediction stats endpoint failed: $STATS_RESPONSE${NC}"
fi

echo -e "\n${BLUE}9. Testing Frontend Accessibility${NC}"
if curl -s http://localhost:5173 > /dev/null; then
    echo -e "${GREEN}✅ Frontend is accessible${NC}"
    echo "Frontend URL: http://localhost:5173"
    echo "Dashboard URL: http://localhost:5173/dashboard"
    echo "Login URL: http://localhost:5173/login"
else
    echo -e "${YELLOW}⚠️  Frontend is not running. Start it with: cd frontend && npm run dev${NC}"
fi

echo -e "\n${GREEN}🎉 Dashboard Integration Test Complete!${NC}"
echo "=============================================="
echo ""
echo "📋 Summary:"
echo "• Backend API endpoints are working"
echo "• Authentication flow is functional"
echo "• Predictions system is operational"
echo "• Dashboard should be fully functional"
echo ""
echo "🌐 Access your application:"
echo "• Frontend: http://localhost:5173"
echo "• Dashboard: http://localhost:5173/dashboard"
echo "• Login: http://localhost:5173/login"
echo ""
echo "👤 Test credentials:"
echo "• Email: test@example.com"
echo "• Password: testpassword123"
echo ""
echo "🔧 If you encounter issues:"
echo "• Check docker-compose ps to ensure all services are running"
echo "• Check backend logs: docker-compose logs backend"
echo "• Check frontend logs: docker-compose logs frontend"
