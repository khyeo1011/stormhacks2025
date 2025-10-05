import os
from flask import Flask, jsonify, g, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
from flask_swagger_ui import get_swaggerui_blueprint

import psycopg2
from flask_cors import CORS

from werkzeug.security import generate_password_hash, check_password_hash

from .auth.routes import auth_bp
from .trips import trips_bp
from .predictions import predictions_bp
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
            "components": {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            },
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
                    }
                },
                "/auth/register": {
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
                                            "nickname": {"type": "string"}
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
                },
                "/auth/login": {
                    "post": {
                        "summary": "User login",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "email": {"type": "string"},
                                            "password": {"type": "string"}
                                        },
                                        "required": ["email", "password"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Login successful",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "accessToken": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            },
                            "401": {
                                "description": "Bad email or password"
                            }
                        }
                    }
                },
                "/auth/friend-requests": {
                    "post": {
                        "summary": "Send a friend request",
                        "security": [{"bearerAuth": []}],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "receiverId": {"type": "integer"}
                                        },
                                        "required": ["receiverId"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "201": {
                                "description": "Friend request sent"
                            },
                            "400": {
                                "description": "Bad request"
                            },
                            "409": {
                                "description": "Friend request already sent or received or users are already friends"
                            }
                        }
                    }
                },
                "/auth/friend-requests/pending": {
                    "get": {
                        "summary": "Get pending friend requests",
                        "security": [{"bearerAuth": []}],
                        "responses": {
                            "200": {
                                "description": "A list of pending friend requests",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "senderId": {"type": "integer"},
                                                    "nickname": {"type": "string"},
                                                    "email": {"type": "string"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/auth/friend-requests/handle": {
                    "post": {
                        "summary": "Handle a friend request",
                        "security": [{"bearerAuth": []}],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "senderId": {"type": "integer"},
                                            "action": {"type": "string", "enum": ["accept", "reject"]}
                                        },
                                        "required": ["senderId", "action"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Friend request handled"
                            },
                            "400": {
                                "description": "Bad request"
                            },
                            "404": {
                                "description": "Friend request not found"
                            }
                        }
                    }
                },
                "/auth/friends": {
                    "get": {
                        "summary": "Get friends list",
                        "security": [{"bearerAuth": []}],
                        "responses": {
                            "200": {
                                "description": "A list of friends",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {"type": "integer"},
                                                    "nickname": {"type": "string"},
                                                    "email": {"type": "string"},
                                                    "cumulativeScore": {"type": "integer"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/trips": {
                    "get": {
                        "summary": "Get all trips",
                        "responses": {
                            "200": {
                                "description": "A list of trips",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {"type": "integer"},
                                                    "name": {"type": "string"},
                                                    "description": {"type": "string"},
                                                    "outcome": {"type": "string"},
                                                    "createdAt": {"type": "string", "format": "date-time"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "post": {
                        "summary": "Create a new trip",
                        "security": [{"bearerAuth": []}],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"},
                                            "description": {"type": "string"}
                                        },
                                        "required": ["name"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "201": {
                                "description": "Trip created"
                            }
                        }
                    }
                },
                "/trips/{tripId}": {
                    "get": {
                        "summary": "Get a single trip",
                        "parameters": [
                            {
                                "name": "tripId",
                                "in": "path",
                                "required": True,
                                "schema": {
                                    "type": "integer"
                                }
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "A single trip",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "integer"},
                                                "name": {"type": "string"},
                                                "description": {"type": "string"},
                                                "outcome": {"type": "string"},
                                                "createdAt": {"type": "string", "format": "date-time"}
                                            }
                                        }
                                    }
                                }
                            },
                            "404": {
                                "description": "Trip not found"
                            }
                        }
                    }
                },
                "/trips/{tripId}/resolve": {
                    "post": {
                        "summary": "Resolve a trip",
                        "security": [{"bearerAuth": []}],
                        "parameters": [
                            {
                                "name": "tripId",
                                "in": "path",
                                "required": True,
                                "schema": {
                                    "type": "integer"
                                }
                            }
                        ],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "outcome": {"type": "string"}
                                        },
                                        "required": ["outcome"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Trip resolved"
                            }
                        }
                    }
                },
                "/predictions": {
                    "get": {
                        "summary": "Get user's predictions",
                        "security": [{"bearerAuth": []}],
                        "responses": {
                            "200": {
                                "description": "A list of predictions",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {"type": "integer"},
                                                    "tripId": {"type": "integer"},
                                                    "predictedOutcome": {"type": "string"},
                                                    "createdAt": {"type": "string", "format": "date-time"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "post": {
                        "summary": "Cast a prediction",
                        "security": [{"bearerAuth": []}],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "tripId": {"type": "integer"},
                                            "predictedOutcome": {"type": "string"}
                                        },
                                        "required": ["tripId", "predictedOutcome"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "201": {
                                "description": "Prediction created"
                            },
                            "409": {
                                "description": "Prediction already exists"
                            }
                        }
                    }
                }
            }
        }
        return jsonify(spec)

    app.register_blueprint(auth_bp)
    app.register_blueprint(trips_bp)
    app.register_blueprint(predictions_bp)



    app.register_blueprint(blueprint)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8000, debug=True)
