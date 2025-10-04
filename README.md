# Buss-in-it

> A web game where you predict if a Translink bus will be on time.

This project is a web game where players bet on whether a bus will be on time or not, based on data from Translink's public API. It features a React frontend, a Flask backend, and a PostgreSQL database.

## How to Play

1.  Create an account and log in.
2.  Find a bus route and an upcoming bus.
3.  Place your bet: will the bus be "Buss-in-it" (on time) or not?
4.  Check back after the bus has arrived to see if you were right and see your score update!

## Getting Started

1.  **Prerequisites:**
    *   Docker
    *   Docker Compose

2.  **Build and run the application:**

    ```bash
    docker-compose up --build
    ```

    This will start the following services:

    *   **Frontend:** React app on `http://localhost:3000`
    *   **Backend:** Flask app on `http://localhost:8000`
    *   **Database:** PostgreSQL on port `5432`

## Services

-   **Frontend:** The React application is located in the `frontend` directory.
-   **Backend:** The Flask application is located in the `backend` directory.
-   **Database:** The PostgreSQL database is configured in `docker-compose.yml`. The initialization script is in `database/init.sql`.
