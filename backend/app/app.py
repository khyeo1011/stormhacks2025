
import os
from flask import Flask, jsonify, g, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
from flask_swagger_ui import get_swaggerui_blueprint
from werkzeug.security import generate_password_hash, check_password_hash

from .auth.routes import auth_bp
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



    # Minimal OpenAPI 3.0 spec so Swagger UI can render
    @app.get('/swagger.json')
    def swagger_spec():
        spec = {
            "openapi": "3.0.3",
            "info": {
                "title": "Buss-in-it API",
                "version": "1.0.0",
                "description": "API for the Buss-in-it web game."
            },
            "servers": [
                {"url": "http://localhost:8000"}
            ],
            "paths": {
                "/": {
                    "get": {
                        "summary": "Hello endpoint",
                        "responses": {
                            "200": {
                                "description": "A friendly greeting",
                                "content": {
                                    "text/plain": {
                                        "schema": {"type": "string"},
                                        "examples": {"example": {"value": "Hello from Flask!"}}
                                    }
                                }
                            }
                        }
                    }
                },
                "/auth/users": {
                    "get": {
                        "summary": "Get all users",
                        "security": [{"bearerAuth": []}],
                        "responses": {
                            "200": {
                                "description": "A list of users",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {"type": "integer"},
                                                    "email": {"type": "string"},
                                                    "nickname": {"type": "string"},
                                                    "cumulativeScore": {"type": "integer"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "post": {
                        "summary": "Create a new user",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "email": {"type": "string"},
                                            "password": {"type": "string"},
                                            "nickname": {"type": "string"},
                                            "cumulativeScore": {"type": "integer"}
                                        },
                                        "required": ["email", "password"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "201": {
                                "description": "User created",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "integer"}
                                            }
                                        }
                                    }
                                }
                            },
                            "409": {
                                "description": "Email already exists"
                            }
                        }
                    }
                }
            }
        }
        return jsonify(spec)

    app.register_blueprint(blueprint)
    app.register_blueprint(auth_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8000, debug=True)
