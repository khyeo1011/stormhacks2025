#!/bin/sh

# Run the data loading script
python load_static_data.py

# Start the Flask application
exec python -m flask --debug run --host=0.0.0.0 --port=8000
