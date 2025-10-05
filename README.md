# Buss-in-it

Ever get sick and tired of waiting for the bus, wondering if it'll ever show up?

 With Buss-in-it, you can stop just waiting and become part of the action!

## Description

Buss-in-it is an engaging web game that challenges players to predict the punctuality of Translink buses using real-time data. Built with a modern tech stack including React for the frontend, Flask for the backend, and PostgreSQL for data persistence, the game offers a unique blend of prediction, strategy, and social interaction. Players can create accounts, make predictions on upcoming bus trips, track their performance on a global leaderboard, and connect with friends.

## Features

*   **Bus Prediction Game:** Predict whether a bus will arrive "on time" or "late" at its final destination. "Early" arrivals are considered "on time" for simplified gameplay ~~Translink buses don't really come early anyways~~.
*   **Real-time Data Integration:** Leverages Translink's GTFS Realtime API to fetch live bus movement data, ensuring dynamic and accurate game outcomes.
*   **User Authentication & Profiles:** Secure user registration and login, with individual profiles tracking cumulative scores based on prediction accuracy.
*   **Social Features:** Send and manage friend requests, view friends' activities, and compete for the top spot on a global leaderboard.
*   **Automated Trip Resolution:** A background service automatically resolves bus trips near their scheduled arrival times, updating outcomes and scoring predictions without manual intervention.
*   **Dynamic Trip Filtering:** The backend efficiently loads and serves trips for the current day, with options for frontend filtering by date range.
*   **Scalable Architecture:** Containerized development using Docker and Docker Compose ensures a consistent and easily deployable environment.
*   **AI Model:** A machine learning pipeline to predict bus delays based on real-time and historical data.

## How to Play

1.  **Create an account:** Register with a unique email and nickname.
2.  **Log in:** Access your personalized dashboard.
3.  **View available trips:** Browse upcoming bus trips for the current day.
4.  **Make a prediction:** For a chosen trip, predict if it will be "on time" or "late" at its last stop.
5.  **Track your score:** After the bus completes its journey, the system will automatically resolve the trip, and your cumulative score will update based on your prediction's accuracy.
6.  **Connect with friends:** Send friend requests and see how your friends are performing.

## Getting Started

To get the Buss-in-it application up and running on your local machine, follow these steps:

### Prerequisites

Make sure you have the following installed:

*   **Docker:** [Install Docker](https://docs.docker.com/get-docker/)
*   **Docker Compose:** [Install Docker Compose](https://docs.docker.com/compose/install/)

### Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/stormhacks2025.git
    cd stormhacks2025
    ```

2.  **Build and run the application:**

    This command will build the Docker images for the frontend and backend, create and start the PostgreSQL database, and launch all services in detached mode.

    ```bash
    docker-compose up --build -d
    ```

3.  **Initialize the database with static GTFS data:**

    After the services are running, you need to populate the database with initial bus route and schedule data. This step is crucial and only needs to be performed once after the first setup or if you clear your database volume. **This should be done automatically, but if it fails run:**

    ```
    docker-compose exec backend python /app/load_static_data.py
    ```

4.  **Access the Application:**

    *   **Frontend (Web Game):** Open your browser and navigate to `http://localhost:5173`
    *   **Backend API Documentation (Swagger UI):** Access the API documentation at `http://localhost:8000/api/docs`

## Project Structure

*   `frontend/`: Contains the React.js application for the user interface.
*   `backend/`: Houses the Flask API, responsible for business logic, database interactions, and real-time data processing.
*   `database/`: Includes the PostgreSQL database initialization scripts (`init.sql`).
*   `docker-compose.yml`: Defines the multi-container Docker application.

## Technologies Used

*   **Frontend:** React.js, TypeScript, Axios, React Router DOM
*   **Backend:** Flask, Python, PostgreSQL, SQLAlchemy, Pandas, Flask-APScheduler, Psycopg2, Flask-JWT-Extended, Requests
*   **Containerization:** Docker, Docker Compose
*   **Real-time Data:** Translink GTFS Realtime API

## API Documentation

Detailed API documentation is available via Swagger UI at `http://localhost:8000/api/docs`.

## Future Enhancements

*   Implement real-time updates for bus positions on the frontend.
*   Add more sophisticated prediction algorithms.
*   Expand social features with direct messaging or groups.
*   Allow users to filter trips by route, time, or destination.
*   Implement push notifications for prediction outcomes.