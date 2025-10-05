#!/bin/sh

# Wait for the database to be ready
sleep 5

# Run the data loading script
python /app/load_static_data.py

# Start the Flask application
exec python -m flask --debug run --host=0.0.0.0 --port=8000
