import os
from flask import Flask, jsonify, g, current_app, redirect, url_for
from flask_jwt_extended import JWTManager
from flask_swagger_ui import get_swaggerui_blueprint
import json
import psycopg2
from flask_cors import CORS
from flask_apscheduler import APScheduler

from .auth.routes import auth_bp, get_db_connection
from .trips import trips_bp, load_data_from_db, trips_df, stop_times_df # Import global dataframes
from .predictions import predictions_bp
from .resolver import resolve_pending_trips
from .contact import contact_bp
from .email_service import init_email_service

# URL for exposing Swagger UI (without trailing '/')
SWAGGER_URL = '/api/docs'
# This must point to a valid OpenAPI/Swagger JSON definition
API_URL = '/swagger.json'

blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Test application"
    },
)

def create_app():
    app = Flask(__name__)

    # Configure CORS
    origins_env = os.getenv("FRONTEND_ORIGINS") or os.getenv("FRONTEND_ORIGIN")
    if origins_env:
        origins = [o.strip() for o in origins_env.split(",") if o.strip()]
    else:
        origins = [
            "http://localhost:3000",
            "http://localhost:5173", 
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173"
        ]

    CORS(
        app,
        resources={r"/*": {"origins": origins}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
        expose_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )

    # Setup the Flask-JWT-Extended extension
    app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET_KEY', 'super-secret-fallback')
    # Optional: configure token expirations
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES_SECONDS', 99999))  # default 99999 seconds
    jwt = JWTManager(app)
    
    # Initialize email service
    init_email_service(app)

    @app.teardown_appcontext
    def close_db(e=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    @app.route('/')
    def hello():
        return redirect("/api/docs")

    @app.route('/leaderboard', methods=['GET'])
    def get_leaderboard():
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute('SELECT nickname, cumulative_score FROM users ORDER BY cumulative_score DESC LIMIT 10;')
                leaderboard = cur.fetchall()
                # The result from fetchall is a list of tuples. Convert to a list of dicts for proper JSON.
                leaderboard_json = [{"nickname": row[0], "cumulative_score": row[1]} for row in leaderboard]
                return jsonify(leaderboard_json)
        finally:
            conn.close()

    @app.get('/swagger.json')
    def swagger_spec():
        # Use a more robust path to swagger.json
        swagger_path = os.path.join(current_app.root_path, 'swagger.json')
        with open(swagger_path, 'r') as f:
            spec = json.load(f)
        return jsonify(spec)

    app.register_blueprint(blueprint)
    app.register_blueprint(auth_bp)
    app.register_blueprint(trips_bp)
    app.register_blueprint(predictions_bp)
    app.register_blueprint(contact_bp)

    # Load dataframes once at startup
    with app.app_context():
        load_data_from_db()

    # Initialize and start the scheduler
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    # Add a job to resolve pending trips every minute, passing the app and dataframes
    scheduler.add_job(id='resolve_trips', func=resolve_pending_trips, trigger='interval', minutes=1, args=[app, trips_df, stop_times_df])

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8000, debug=True)