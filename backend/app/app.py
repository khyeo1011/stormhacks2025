
import os
from flask import Flask, jsonify, g, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
from flask_swagger_ui import get_swaggerui_blueprint
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash

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

    @app.route('/login', methods=['POST'])
    def login():
        email = request.json.get('email', None)
        password = request.json.get('password', None)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, password FROM users WHERE email = %s;', (email,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[1], password):
            user_id = user[0]
            access_token = create_access_token(identity=user_id)
            return jsonify(access_token=access_token)

        return jsonify({"msg": "Bad email or password"}), 401

    @app.route('/users', methods=['GET'])
    @jwt_required()
    def get_users():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, email, nickname, cumulativeScore FROM users;')
        users = cur.fetchall()
        cur.close()
        return jsonify(users)

    @app.route('/users', methods=['POST'])
    def add_user():
        data = request.get_json()
        email = data['email']
        password = data['password']
        nickname = data.get('nickname')
        cumulativeScore = data.get('cumulativeScore', 0)

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                'INSERT INTO Users (email, password, nickname, cumulativeScore) VALUES (%s, %s, %s, %s) RETURNING id',
                (email, hashed_password, nickname, cumulativeScore)
            )
            user_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            return jsonify({'id': user_id}), 201
        except psycopg2.IntegrityError:
            conn.rollback()
            cur.close()
            return jsonify({'error': 'email already exists'}), 409

    # --- Friend Request and Friends Endpoints ---

    @app.route('/friend-requests', methods=['POST'])
    @jwt_required()
    def send_friend_request():
        sender_id = get_jwt_identity()
        receiver_id = request.json.get('receiver_id')

        if not receiver_id:
            return jsonify({"error": "receiver_id is required"}), 400
        if sender_id == receiver_id:
            return jsonify({"error": "Cannot send a friend request to yourself"}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            # Check if a request already exists or if they are already friends
            cur.execute('SELECT 1 FROM friend_requests WHERE (sender_id = %s AND receiver_id = %s) OR (sender_id = %s AND receiver_id = %s)', (sender_id, receiver_id, receiver_id, sender_id))
            if cur.fetchone():
                return jsonify({"error": "Friend request already sent or received"}), 409
            
            cur.execute('SELECT 1 FROM friends WHERE user_id = %s AND friend_id = %s', (sender_id, receiver_id))
            if cur.fetchone():
                return jsonify({"error": "Users are already friends"}), 409

            cur.execute(
                'INSERT INTO friend_requests (sender_id, receiver_id, status) VALUES (%s, %s, %s)',
                (sender_id, receiver_id, 'pending')
            )
            conn.commit()
            cur.close()
            return jsonify({"msg": "Friend request sent"}), 201
        except psycopg2.Error as e:
            conn.rollback()
            cur.close()
            return jsonify({"error": str(e)}), 500

    @app.route('/friend-requests/pending', methods=['GET'])
    @jwt_required()
    def get_pending_requests():
        user_id = get_jwt_identity()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT fr.sender_id, u.nickname, u.email FROM friend_requests fr JOIN users u ON fr.sender_id = u.id WHERE fr.receiver_id = %s AND fr.status = %s', (user_id, 'pending'))
        requests = [{"sender_id": row[0], "nickname": row[1], "email": row[2]} for row in cur.fetchall()]
        cur.close()
        return jsonify(requests)

    @app.route('/friend-requests/handle', methods=['POST'])
    @jwt_required()
    def handle_friend_request():
        receiver_id = get_jwt_identity()
        sender_id = request.json.get('sender_id')
        action = request.json.get('action') # 'accept' or 'reject'

        if not all([sender_id, action in ['accept', 'reject']]):
            return jsonify({"error": "sender_id and a valid action ('accept' or 'reject') are required"}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            # Delete the request regardless of action
            cur.execute('DELETE FROM friend_requests WHERE sender_id = %s AND receiver_id = %s RETURNING status', (sender_id, receiver_id))
            request_exists = cur.fetchone()
            if not request_exists:
                return jsonify({"error": "Friend request not found"}), 404

            if action == 'accept':
                # Add friendship in both directions
                cur.execute('INSERT INTO friends (user_id, friend_id) VALUES (%s, %s)', (receiver_id, sender_id))
                cur.execute('INSERT INTO friends (user_id, friend_id) VALUES (%s, %s)', (sender_id, receiver_id))
            
            conn.commit()
            cur.close()
            return jsonify({"msg": f"Friend request {action}ed"}), 200
        except psycopg2.Error as e:
            conn.rollback()
            cur.close()
            return jsonify({"error": str(e)}), 500

    @app.route('/friends', methods=['GET'])
    @jwt_required()
    def get_friends():
        user_id = get_jwt_identity()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT f.friend_id, u.nickname, u.email, u.cumulativeScore FROM friends f JOIN users u ON f.friend_id = u.id WHERE f.user_id = %s', (user_id,))
        friends = [{"id": row[0], "nickname": row[1], "email": row[2], "cumulativeScore": row[3]} for row in cur.fetchall()]
        cur.close()
        return jsonify(friends)

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
                "/users": {
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

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8000, debug=True)
