-- init.sql

-- Drop existing tables to ensure a clean slate on re-initialization
DROP TABLE IF EXISTS stop_times;
DROP TABLE IF EXISTS trips;
DROP TABLE IF EXISTS stops;
DROP TABLE IF EXISTS routes;
DROP TABLE IF EXISTS calendar;
DROP TABLE IF EXISTS calendar_dates;
DROP TABLE IF EXISTS agency;
DROP TABLE IF EXISTS feed_info;
DROP TABLE IF EXISTS shapes;
DROP TABLE IF EXISTS transfers;
DROP TABLE IF EXISTS predictions;
DROP TABLE IF EXISTS friends;
DROP TABLE IF EXISTS friend_requests;
DROP TABLE IF EXISTS users;



CREATE TABLE stops (
    stop_id VARCHAR(255) PRIMARY KEY,
    stop_name VARCHAR(255),
    stop_lat DOUBLE PRECISION,
    stop_lon DOUBLE PRECISION
);

CREATE TABLE routes (
    route_id VARCHAR(255) PRIMARY KEY,
    route_short_name VARCHAR(255),
    route_long_name VARCHAR(255)
);

CREATE TABLE calendar (
    service_id VARCHAR(255) PRIMARY KEY,
    monday INT,
    tuesday INT,
    wednesday INT,
    thursday INT,
    friday INT,
    saturday INT,
    sunday INT,
    start_date INT,
    end_date INT
);

CREATE TABLE trips (
    trip_id VARCHAR(255) PRIMARY KEY,
    route_id VARCHAR(255) REFERENCES routes(route_id),
    service_id VARCHAR(255) REFERENCES calendar(service_id),
    trip_headsign VARCHAR(255),
    direction_id INT,
    shape_id VARCHAR(255)
);

CREATE TABLE stop_times (
    trip_id VARCHAR(255) REFERENCES trips(trip_id),
    arrival_time VARCHAR(255),
    departure_time VARCHAR(255),
    stop_id VARCHAR(255) REFERENCES stops(stop_id),
    stop_sequence INT,
    PRIMARY KEY (trip_id, stop_sequence)
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    nickname VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    cumulative_score INTEGER DEFAULT 0
);

CREATE TABLE friend_requests (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER REFERENCES users(id),
    receiver_id INTEGER REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'pending', -- e.g., 'pending', 'accepted', 'declined'
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE friends (
    user_id1 INTEGER REFERENCES users(id),
    user_id2 INTEGER REFERENCES users(id),
    PRIMARY KEY (user_id1, user_id2)
);

CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    trip_id VARCHAR(255) REFERENCES trips(trip_id),
    predicted_outcome VARCHAR(255),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);