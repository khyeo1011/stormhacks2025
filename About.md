# About Buss-in-it: The Story
## Our Inspiration
The idea for "Buss-in-it" sparked from a shared, universal experience: the frustration of waiting for a bus. As students and commuters in Metro Vancouver, we're all too familiar with checking the Translink app, wondering if the bus will actually arrive on time. We thought, what if we could turn this passive, often frustrating wait into an active, engaging, and fun experience? We wanted to gamify the commute, allowing people to use their local knowledge and intuition to predict bus schedules. "Buss-in-it" transforms a moment of impatience into a friendly competition.

## What We Learned
This project was a significant learning journey for our team across the full stack of web development:

- **Data Engineering:** We dove deep into the world of public transit data, learning how to parse and structure the complex GTFS (General Transit Feed Specification) data provided by Translink. Understanding the intricate relationships between routes, trips, stops, and schedules was our first major hurdle and a huge learning experience.

- **Backend Development:** We built a robust RESTful API using Flask and handled complex database operations with PostgreSQL. Implementing a secure user authentication system with JWT (JSON Web Tokens), including access and refresh tokens, taught us invaluable lessons about application security and state management.

- **Frontend Interactivity:** On the frontend, we honed our React skills, building a dynamic and responsive user interface that communicates effectively with our backend. Managing user state, handling asynchronous API calls, and creating an intuitive user experience were key areas of growth.

- **DevOps & Containerization:** One of the most valuable takeaways was learning to containerize a multi-service application using Docker and Docker Compose. We learned how to create a reproducible development environment, manage networking between containers, and orchestrate the entire application stack, which is a critical skill in modern software development.

- **AI & Machine Learning:** A major leap for us was integrating a predictive AI model. We learned the fundamentals of feature engineering, using historical transit data to select relevant factors like time of day, route, and weather patterns. We then trained a machine learning model to predict the probability of a bus being late, adding a powerful data-driven element to our game.

## How We Built It
Our development process was broken down into several key phases:

- **Foundation (Backend & Database):** We started by designing our PostgreSQL database schema to hold the parsed Translink data. We then built the core of our Flask API, creating the initial models and endpoints for users and bus trips. A crucial early step was writing Python scripts to process the raw GTFS text files and populate our database.

- **Building the Interface (Frontend):** With the backend taking shape, we began developing the React frontend. We started with the essential components for user authentication—registration and login—before moving on to the main dashboard where users could view and select bus trips.

- **Connecting the Pieces (Integration):** This phase involved wiring the frontend to the backend. We implemented the logic for making predictions, fetching trip data, and displaying it dynamically. We also built out the social features, like the leaderboard and friend request system, which required creating new API endpoints and corresponding UI components.

- **Deployment & Orchestration:** Finally, we containerized our application. We wrote Dockerfiles for both the React frontend and the Flask backend and created a docker-compose.yml file to manage the three services (frontend, backend, database) and their networking. This ensured that any developer could get the project running with a single command.

- **Integrating Intelligence (AI Model):** We developed a Python-based machine learning model using historical data to predict bus delays. This model was then integrated into our Flask backend. We created a new API endpoint that allows the frontend to query the model for a specific trip, providing users with an AI-powered prediction to complement their own intuition.

## Challenges We Faced
- **Data Complexity:** The GTFS dataset is incredibly normalized and relational. Our biggest initial challenge was mapping out how all the different files (routes.txt, trips.txt, stop_times.txt, etc.) connected to reconstruct a single, coherent bus journey.

- **Authentication Flow:** Implementing a secure and seamless authentication flow with JWTs was complex. Handling token expiration, secure storage on the client-side, and refreshing tokens without disrupting the user experience required careful planning and debugging.

- **Cross-Origin Resource Sharing (CORS):** As we developed the frontend and backend separately, we ran into CORS issues. Configuring the Flask server to correctly handle requests from the React development server was a technical hurdle we had to overcome to allow our app to function.

- **Scope Management:** With so many ideas, our biggest project management challenge was scoping down to a realistic MVP (Minimum Viable Product) for the hackathon. We had to prioritize core features like predictions and the leaderboard over more complex ideas to ensure we had a polished, working product at the end.

- **Model Accuracy and Feature Engineering:** Building an accurate predictive model was challenging. Identifying the most influential features (e.g., weather, time of day, route-specific patterns) and dealing with noisy or incomplete historical data required significant experimentation and refinement.