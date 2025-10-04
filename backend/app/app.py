import os
from flask import Flask, jsonify, g, request
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
import os

import psycopg2
from werkzeug.security import generate_password_hash

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

def get_db_connection():
    if 'db' not in g:
        g.db = psycopg2.connect(
            host=os.environ.get('POSTGRES_HOST'),
            database=os.environ.get('POSTGRES_DB'),
            user=os.environ.get('POSTGRES_USER'),
            password=os.environ.get('POSTGRES_PASSWORD')
        )
    return g.db

def create_app():
    app = Flask(__name__)

    @app.teardown_appcontext
    def close_db(e=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    @app.route('/')
    def hello():
        return "Hello from Flask!"

    @app.route('/users', methods=['GET'])
    def get_users():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, email, firstName, lastName, cumulativeScore FROM users;')
        users = cur.fetchall()
        cur.close()
        return jsonify(users)

    @app.route('/users', methods=['POST'])
    def add_user():
        data = request.get_json()
        email = data['email']
        password = data['password']
        firstName = data.get('firstName')
        lastName = data.get('lastName')
        cumulativeScore = data.get('cumulativeScore', 0)

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                'INSERT INTO users (email, password, firstName, lastName, cumulativeScore) VALUES (%s, %s, %s, %s, %s) RETURNING id',
                (email, hashed_password, firstName, lastName, cumulativeScore)
            )
            user_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            return jsonify({'id': user_id}), 201
        except psycopg2.IntegrityError:
            conn.rollback()
            cur.close()
            return jsonify({'error': 'email already exists'}), 409

    # Minimal OpenAPI 3.0 spec so Swagger UI can render
    @app.get('/swagger.json')
    def swagger_spec():
        spec = {
            "openapi": "3.0.3",
            "info": {
                "title": "Test application",
                "version": "1.0.0",
                "description": "Minimal OpenAPI spec for the Flask app"
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
                "/users": {
                    "get": {
                        "summary": "Get all users",
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
                                                    "firstName": {"type": "string"},
                                                    "lastName": {"type": "string"},
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
                                            "firstName": {"type": "string"},
                                            "lastName": {"type": "string"},
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

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8000, debug=True)