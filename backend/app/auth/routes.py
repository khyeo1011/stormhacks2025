from flask import Blueprint
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