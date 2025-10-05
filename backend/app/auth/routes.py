from flask import Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, email, nickname, cumulativeScore FROM users;')
    users = cur.fetchall()
    cur.close()
    return jsonify(users)


@auth_bp.route('/users', methods=['POST'])
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