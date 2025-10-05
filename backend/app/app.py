import os
from flask import Flask, jsonify, g, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
from flask_swagger_ui import get_swaggerui_blueprint
import json
import requests
import psycopg2
import json
from flask_cors import CORS

from werkzeug.security import generate_password_hash, check_password_hash

from .auth.routes import auth_bp
from .trips import trips_bp
from .predictions import predictions_bp
from .routes_data import routes_data_bp
from .auth.routes import get_db_connection

# URL for exposing Swagger UI (without trailing '/')
SWAGGER_URL = '/api/docs'
# This must point to a valid OpenAPI/Swagger JSON definition
API_URL = '/swagger.json'

blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "Test application"
    },
)


def create_app():
    app = Flask(__name__)
    CORS(app)

    # Configure CORS for API endpoints and Swagger
    origins_env = os.getenv("FRONTEND_ORIGINS") or os.getenv("FRONTEND_ORIGIN")
    if origins_env:
        origins = [o.strip() for o in origins_env.split(",") if o.strip()]
    else:
        origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://localhost:3000",
            "https://127.0.0.1:3000",
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
    app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET_KEY', 'super-secret-fallback') # Change this in production!
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
        cur = conn.cursor() 
        cur.execute('SELECT nickname, "cumulativeScore" FROM users ORDER BY "cumulativeScore" DESC LIMIT 10;')
        leaderboard = cur.fetchall()
        cur.close()
        return jsonify(leaderboard)



    @app.get('/swagger.json')
    def swagger_spec():
        with open('app/swagger.json', 'r') as f:
            spec = json.load(f)
        return jsonify(spec)

    app.register_blueprint(blueprint)
    app.register_blueprint(auth_bp)
    app.register_blueprint(trips_bp)
    app.register_blueprint(predictions_bp)
    app.register_blueprint(routes_data_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8000, debug=True)
