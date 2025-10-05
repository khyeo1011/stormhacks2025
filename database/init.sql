-- init.sql

-- Drop existing tables to ensure a clean slate on re-initialization
DROP TABLE IF EXISTS stop_times CASCADE;
DROP TABLE IF EXISTS trips CASCADE;
DROP TABLE IF EXISTS stops CASCADE;
DROP TABLE IF EXISTS routes CASCADE;
DROP TABLE IF EXISTS calendar CASCADE;
DROP TABLE IF EXISTS calendar_dates CASCADE;
DROP TABLE IF EXISTS agency CASCADE;
DROP TABLE IF EXISTS feed_info CASCADE;
DROP TABLE IF EXISTS shapes CASCADE;
DROP TABLE IF EXISTS transfers CASCADE;
DROP TABLE IF EXISTS predictions CASCADE;
DROP TABLE IF EXISTS friends CASCADE;
DROP TABLE IF EXISTS friend_requests CASCADE;
DROP TABLE IF EXISTS users CASCADE;



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
    trip_id VARCHAR(255) NOT NULL,
    service_date DATE NOT NULL,
    route_id VARCHAR(255) REFERENCES routes(route_id),
    service_id VARCHAR(255) REFERENCES calendar(service_id),
    trip_headsign VARCHAR(255),
    direction_id INT,
    shape_id VARCHAR(255),
    outcome VARCHAR(255) DEFAULT NULL,
    PRIMARY KEY (trip_id, service_date)
);

CREATE TABLE stop_times (
    trip_id VARCHAR(255) NOT NULL,
    service_date DATE NOT NULL,
    arrival_time VARCHAR(255),
    departure_time VARCHAR(255),
    stop_id VARCHAR(255) REFERENCES stops(stop_id),
    stop_sequence INT,
    PRIMARY KEY (trip_id, service_date, stop_sequence),
    FOREIGN KEY (trip_id, service_date) REFERENCES trips(trip_id, service_date)
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    nickname VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    cumulative_score INTEGER DEFAULT 0,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
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
    trip_id VARCHAR(255) NOT NULL,
    service_date DATE NOT NULL,
    predicted_outcome VARCHAR(255),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trip_id, service_date) REFERENCES trips(trip_id, service_date)
);