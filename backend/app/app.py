import os
from flask import Flask, jsonify, g, current_app
from flask_jwt_extended import JWTManager
from flask_swagger_ui import get_swaggerui_blueprint
import json
import psycopg2
from flask_cors import CORS

from .auth.routes import auth_bp, get_db_connection
from .trips import trips_bp, populate_trips_from_static_data
from .predictions import predictions_bp
from .routes_data import routes_data_bp

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
            "http://127.0.0.1:3000",
            "https://localhost:3000",
            "https://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "https://localhost:5173",
            "https://127.0.0.1:5173",
            "http://localhost:5000",
            "http://127.0.0.1:5000",
            "https://localhost:5000",
            "https://127.0.0.1:5000",
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
    jwt = JWTManager(app)

    @app.teardown_appcontext
    def close_db(e=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    @app.route('/')
    def hello():
        return "Hello from Flask!"

    @app.route('/leaderboard', methods=['GET'])
    def get_leaderboard():
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute('SELECT nickname, "cumulativeScore" FROM users ORDER BY "cumulativeScore" DESC LIMIT 10;')
                leaderboard = cur.fetchall()
                # The result from fetchall is a list of tuples. Convert to a list of dicts for proper JSON.
                leaderboard_json = [{"nickname": row[0], "cumulativeScore": row[1]} for row in leaderboard]
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
    app.register_blueprint(routes_data_bp)

    with app.app_context():
        populate_trips_from_static_data()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8000, debug=True)