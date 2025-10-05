import os
from flask import Blueprint
from flask import jsonify, g, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2


auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

ALLOWED_EXTENTIONS = ('png', 'jpg', 'jpeg',)
UPLOAD_FOLDER = 'static/uploads/'

def allowed_file(filename):
    'check if file extention is valid'
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENTIONS

def upload_image(photo):
    """
    function for saving photos to UPLOAD_FOLDER directory
    :return: path to saved file
    """

    if photo.filename == '':
        flash("No image selected")
        return redirect(request.url)

    if photo and allowed_file(photo.filename):
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(UPLOAD_FOLDER, filename))

        flash("uploaded")
        return os.path.join(UPLOAD_FOLDER, filename)


def get_db_connection():
    if 'db' not in g:
        g.db = psycopg2.connect(
            host=os.environ.get('POSTGRES_HOST'),
            database=os.environ.get('POSTGRES_DB'),
            user=os.environ.get('POSTGRES_USER'),
            password=os.environ.get('POSTGRES_PASSWORD')
        )
    return g.db

@auth_bp.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, email, nickname, cumulativeScore FROM users;')
    users = cur.fetchall()
    cur.close()
    return jsonify(users)


@auth_bp.route('/register', methods=['POST'])
def add_user():
    data = request.get_json()
    email = data['email']
    password = data['password']
    nickname = data.get('nickname')
    cumulativeScore = 0

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



@auth_bp.route('/login', methods=['POST'])
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

@auth_bp.route('/friend-requests', methods=['POST'])
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

@auth_bp.route('/friend-requests/pending', methods=['GET'])
@jwt_required()
def get_pending_requests():
    user_id = get_jwt_identity()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT fr.sender_id, u.nickname, u.email FROM friend_requests fr JOIN users u ON fr.sender_id = u.id WHERE fr.receiver_id = %s AND fr.status = %s', (user_id, 'pending'))
    requests = [{"sender_id": row[0], "nickname": row[1], "email": row[2]} for row in cur.fetchall()]
    cur.close()
    return jsonify(requests)

@auth_bp.route('/friend-requests/handle', methods=['POST'])
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

@auth_bp.route('/friends', methods=['GET'])
@jwt_required()
def get_friends():
    user_id = get_jwt_identity()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT f.friend_id, u.nickname, u.email, u.cumulativeScore FROM friends f JOIN users u ON f.friend_id = u.id WHERE f.user_id = %s', (user_id,))
    friends = [{"id": row[0], "nickname": row[1], "email": row[2], "cumulativeScore": row[3]} for row in cur.fetchall()]
    cur.close()
    return jsonify(friends)