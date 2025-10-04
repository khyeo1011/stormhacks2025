# stormhacks2025

This project is a web application with a React frontend, a Flask backend, and a PostgreSQL database.

## Prerequisites

- Docker
- Docker Compose

## Getting Started

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd <repository-folder>
    ```

2.  **Build and run the application:**

    ```bash
    docker-compose up --build
    ```

    This will start the following services:

    -   **Frontend:** React app on `http://localhost:3000`
    -   **Backend:** Flask app on `http://localhost:5000`
    -   **Database:** PostgreSQL on port `5432`

## Services

-   **Frontend:** The React application is located in the `frontend` directory.
-   **Backend:** The Flask application is located in the `backend` directory.
-   **Database:** The PostgreSQL database is configured in `docker-compose.yml`. The initialization script is in `database/init.sql`.