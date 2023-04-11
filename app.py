import os
from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Iamsuperman:devxspace@Iamsuperman.mysql.pythonanywhere-services.com/Iamsuperman$devxspace'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = os.urandom(24)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(42), nullable=False, unique=True)
    avatar = db.Column(db.String(20), nullable=True)
    username = db.Column(db.String(20), nullable=True, unique=True)

    services = db.relationship('Service', backref='user', lazy=True)

    def __repr__(self):
        return f"User {self.address}"


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    image_file = db.Column(db.String(20), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.Integer, db.ForeignKey('user.username'), nullable=False)

    def __repr__(self):
        return f"Name: {self.name}, Image: {self.image_file}"


# @app.route('/login', methods=['POST'])
# def login():
#     address = request.headers.get('address')
#     if not address:
#         return jsonify({'error': 'Wallet address not provided.'}), 400

#     # Set session cookie to the wallet address
#     session['address'] = address

#     # Check if user exists in the database, if not create new user
#     user = User.query.filter_by(address=address).first()
#     if not user:
#         new_user = User(address=address)
#         db.session.add(new_user)
#         db.session.commit()

#     return jsonify({'message': 'Logged in successfully.'})



@app.route('/create_profile', methods=['POST'])
def create_profile():
    address = session.get('address')
    if not address:
        return jsonify({'error': 'User not logged in.'}), 401

    data = request.form
    avatar = request.files.get('avatar')
    username = data.get('username')

    if not username:
        return jsonify({'error': 'Username not provided.'}), 400

    filename = None
    if avatar:
        filename = secure_filename(avatar.filename)
        avatar.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    user = User.query.filter_by(address=address).first()
    if not user:
        user = User(address=address)

    user.username = username
    if filename:
        user.avatar = filename

    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Profile created successfully.'})


@app.route('/update_profile', methods=['PUT'])
def update_profile():
    if 'address' not in session:
        return jsonify({'error': 'User not logged in.'}), 401

    data = request.form
    address = session['address']
    avatar = request.files.get('avatar')

    user = User.query.filter_by(address=address).first()
    if not user:
        return jsonify({'error': 'User not found.'}), 404

    if avatar:
        filename = secure_filename(avatar.filename)
        avatar.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        user.avatar = filename

    db.session.commit()
    return jsonify({'message': 'Profile updated successfully.'})


@app.route('/register_service', methods=['POST'])
def register_service():
    if 'address' not in session:
        return jsonify({'error': 'User not logged in.'}), 401

    data = request.form
    address = session['address']
    service_name = data.get('name')
    service_image = request.files.get('image_file')
    if not service_image:
        return jsonify({'error': 'Image file not provided.'}), 400

    filename = secure_filename(service_image.filename)
    service_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    user_id = User.query.filter_by(address=address).first().id
    new_service = Service(name=service_name, image_file=filename, user_id=user_id)
    db.session.add(new_service)
    db.session.commit()
    return jsonify({'message': 'Service registered successfully.'})



@app.route('/list_services', methods=['GET'])
def list_services():
    user_id = request.args.get('user_id')
    if user_id:
        services = Service.query.filter_by(user_id=user_id).all()
    else:
        services = Service.query.all()
    return jsonify([{'id': service.id, 'name': service.name, 'image_file': service.image_file} for service in services])


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the table
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.run(host='0.0.0.0', port=8000, debug=True)