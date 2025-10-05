#!/bin/sh


python /app/load_static_data.py

echo "Starting Flask application..."
exec python -m flask --debug run --host=0.0.0.0 --port=8000