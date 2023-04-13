import os
from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.utils import secure_filename
import datetime





app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Iamsuperman:devxspace@Iamsuperman.mysql.pythonanywhere-services.com/Iamsuperman$devxspace'

app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
app.secret_key = os.urandom(24)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


# def get_account():
#     with app.app_context():
#         web3 = Web3()
#         if web3.is_connected():
#             accounts = web3.eth.accounts
#             if len(accounts) > 0:
#                 account = accounts[0]
#                 return account
#             else:
#                 return 'No Ethereum accounts found'
#         else:
#             return 'Could not connect to Ethereum network'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(42), nullable=False, unique=True)
    avatar = db.Column(db.String(20), nullable=True)
    username = db.Column(db.String(20), nullable=True, unique=True)
    about = db.Column(db.String(255), nullable=True)
    skills = db.relationship('Skill', backref='user', lazy=True)

    services = db.relationship('Service', backref='user', lazy=True, foreign_keys='Service.user_address')

    def __repr__(self):
        return f"User {self.address}"



class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    image_file = db.Column(db.String(20), nullable=True)
    user_address = db.Column(db.String(42), db.ForeignKey('user.address'), nullable=False)

    def __repr__(self):
        return f"Name: {self.name}, Image: {self.image_file}"

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    accepted = db.Column(db.Boolean, default=False)
    completed = db.Column(db.Boolean, default=False)
    rejected = db.Column(db.Boolean, default=False)
    deadline = db.Column(db.DateTime, nullable=False)
    developer_address = db.Column(db.String(42), db.ForeignKey('user.address'), nullable=False)
    owner_address = db.Column(db.String(42), db.ForeignKey('user.address'), nullable=False)

    def __repr__(self):
        return f"Task {self.id}, Title: {self.title}, Status: {self.status}"


class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)






@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    address = data.get('address')

    if not address:
        return jsonify({'error': 'Wallet address not provided.'}), 400

    # Set session cookie to the wallet address
    session['address'] = address

    # Check if user exists in the database, if not create new user
    user = User.query.filter_by(address=address).first()
    session['logged_in'] = True
    if not user:
        new_user = User(address=address)
        db.session.add(new_user)
        db.session.commit()

    return jsonify({'message': 'Logged in successfully.'})




@app.route('/create_profile', methods=['POST'])
@login_required # require user to be logged in to access this endpoint
def create_profile():
    data = request.get_json()

    username = data.get('username')
    about = data.get('about')
    skill_names = data.get('skills')

    user = User.query.filter_by(address=current_user.address).first()

    if user:
        return jsonify({'error': 'User already exists'})

    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        return jsonify({'error': 'Username already exists'})

    avatar = data.get('avatar')
    if avatar is not None:
        try:
            avatar_file = avatar.get('file')
            if avatar_file is not None:
                filename = secure_filename(avatar_file.filename)
                avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                avatar_file.save(avatar_path)
                avatar = filename
            else:
                avatar = None
        except Exception as e:
            print(f'Error saving avatar: {e}')
            avatar = None

    user = User(address=current_user.address, avatar=avatar, username=username, about=about)
    db.session.add(user)
    db.session.commit()

    skills = []
    for skill_name in skill_names:
        skill = Skill(name=skill_name, user=user)
        db.session.add(skill)
        db.session.commit()
        skills.append(skill.name)

    return jsonify({'success': 'Profile created successfully', 'skills': skills})


@app.route('/users')
def get_users():
    users = User.query.all()
    user_list = []
    for user in users:
        user_dict = {
            'id': user.id,
            'address': user.address,
            'avatar': user.avatar,
            'username': user.username,
            'about': user.about,
            'skills': [skill.name for skill in user.skills]
        }
        user_list.append(user_dict)
    return {'users': user_list}

# GET A USER
@app.route('/users/<address>')
def get_user(address):
    user = User.query.filter_by(address=address).first()
    if user:
        return {
            'id': user.id,
            'address': user.address,
            'avatar': user.avatar,
            'username': user.username,
            'about': user.about,
            'skills': [skill.name for skill in user.skills]
        }
    else:
        return {'error': f'User with address {address} not found'}, 404





# UPDATE A USER PROFILE

@app.route('/update_profile', methods=['POST'])
def update_profile():
    data = request.json

    user_address = data.get('user_address')
    user = User.query.filter_by(address=user_address).first()
    if not user:
        return jsonify({'message': 'User not found.'}), 404

    avatar = data.get('avatar')
    username = data.get('username')
    about = data.get('about')
    skills = data.get('skills')

    if avatar:
        user.avatar = avatar
    if username:
        user.username = username
    if about:
        user.about = about
    if skills:
        # First remove all existing skills
        for skill in user.skills:
            db.session.delete(skill)
        # Then add new skills
        for skill_name in skills:
            skill = Skill(name=skill_name, user=user)
            db.session.add(skill)

    db.session.commit()
    return jsonify({'message': 'Profile updated successfully.'}), 200



# REGISTER A SERVICE AS A FREELANCER

@app.route('/register_service', methods=['POST'])
def register_service():
    if 'address' not in session:
        return jsonify({'error': 'User not logged in.'}), 401

    data = request.get_json()
    address = session['address']
    service_name = data.get('name')
    service_desc = data.get('description')
    service_image = request.files.get('image_file')

    filename = None
    if service_image:
        filename = secure_filename(service_image.filename)
        service_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    user = User.query.filter_by(address=address).first()
    new_service = Service(name=service_name, description=service_desc, image_file=filename, user=user)
    db.session.add(new_service)
    db.session.commit()
    return jsonify({'message': 'Service registered successfully.'})




# HIRE A DEVELOPER AS BUYER
@app.route('/hire_developer', methods=['POST'])
def hire_developer():
    if 'address' not in session:
        return jsonify({'error': 'User not logged in.'}), 401

    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    time_frame = data.get('time_frame')
    developer_address = data.get('developer_address')

    user_address = session['address']

    task = Task(title=title, description=description, time_frame=time_frame, user_address=user_address, developer_address=developer_address)
    db.session.add(task)
    db.session.commit()

    return jsonify({'message': 'Task created successfully.'})


# LIST OF TASKS AVAILABLE TO A USER
@app.route('/available_tasks', methods=['GET'])
def get_available_tasks():
    if 'address' not in session:
        return jsonify({'error': 'User not logged in.'}), 401

    developer_address = request.json.get('address')
    developer = User.query.filter_by(address=developer_address).first()
    if not developer:
        return jsonify({'error': 'Developer not found: create a profile.'}), 404

    available_tasks = Task.query.filter_by(developer_address='developer').all()
    tasks = []
    for task in available_tasks:
        tasks.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'price': task.price,
            'accepted': task.accepted,
            'completed': task.completed,
            'rejected': task.rejected,
            'deadline': task.deadline.strftime("%Y-%m-%d %H:%M:%S"),
            'developer_address': developer_address,
            'owner_address': task.owner_address
        })
    return jsonify({'tasks': tasks})









# ACCEPT A TASK
@app.route('/tasks/accept', methods=['POST'])
def accept_task():
    data = request.get_json()
    task_id = data.get('task_id')
    developer_address = session.get('address')

    task = Task.query.filter_by(id=task_id, developer_address=developer_address, accepted=False, rejected=False).first()

    if not task:
        return jsonify({'error': 'Task not found or already accepted/rejected.'}), 404

    task.accepted = True
    task.accepted_date = datetime.utcnow()
    db.session.commit()

    return jsonify({'message': 'Task accepted successfully.'})


# REJECT A TASK
@app.route('/tasks/reject', methods=['POST'])
def reject_task():
    data = request.get_json()
    task_id = data.get('task_id')
    developer_address = session.get('address')

    task = Task.query.filter_by(id=task_id, developer_address=developer_address, accepted=False, rejected=False).first()

    if not task:
        return jsonify({'error': 'Task not found or already accepted/rejected.'}), 404

    task.rejected = True
    db.session.commit()

    return jsonify({'message': 'Task rejected successfully.'})



# BUYER CANCELS A TASK
@app.route('/tasks/cancel', methods=['POST'])
def cancel_task():
    data = request.get_json()
    task_id = data.get('task_id')
    user_address = session.get('address')

    task = Task.query.filter_by(id=task_id, owner_address=user_address, accepted=False, rejected=False, completed=False).first()

    if not task:
        return jsonify({'error': 'Task not found or cannot be cancelled.'}), 404

    task.cancelled = True
    db.session.commit()

    return jsonify({'message': 'Task cancelled successfully.'})




# LIST ALL SERVICES A DEVELOPER CREATED
@app.route('/list_services', methods=['GET'])
def list_services():
    address = request.args.get('address')
    if address:
        user = User.query.filter_by(address=address).first()
        if not user:
            return jsonify({'error': 'User not found'})
        services = Service.query.filter_by(user_address=user.user_address).all()
    else:
        services = Service.query.all()
    return jsonify([{'id': service.id, 'name': service.name, 'image_file': service.image_file, 'user_address': service.user.address} for service in services])




if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the table
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.run(host='0.0.0.0', port=8000, debug=True)