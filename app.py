import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from stitcher import stitch_images

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
# DB Config (Use your Neon connection string here)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///local.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File Upload Config
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- Database Models ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    sessions = db.relationship('StitchingSession', backref='user', lazy=True)

class StitchingSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    session_name = db.Column(db.String(100))
    result_image = db.Column(db.String(200)) # Path to stitched output

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Routes ---

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return redirect(url_for('signup'))
        
        # 1. CHANGE: Only create user, do not login automatically
        new_user = User(username=username, password=generate_password_hash(password, method='pbkdf2:sha256'))
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! Please log in.', 'success')
        # 1. CHANGE: Redirect to login page
        return redirect(url_for('login'))
        
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials.', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    history = StitchingSession.query.filter_by(user_id=current_user.id).order_by(StitchingSession.timestamp.desc()).all()
    return render_template('dashboard.html', history=history)

@app.route('/stitch', methods=['POST'])
@login_required
def stitch():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400
    
    files = request.files.getlist('files[]')
    if not files or files[0].filename == '':
        return jsonify({'error': 'No selected file'}), 400

    session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = os.path.join(app.config['UPLOAD_FOLDER'], f"user_{current_user.id}_{session_timestamp}")
    os.makedirs(session_dir, exist_ok=True)

    saved_paths = []
    for file in files:
        filename = secure_filename(file.filename)
        path = os.path.join(session_dir, filename)
        file.save(path)
        saved_paths.append(path)

    output_filename, error_msg = stitch_images(saved_paths, session_dir)

    if error_msg:
        return jsonify({'error': error_msg}), 500

    rel_path = f"uploads/user_{current_user.id}_{session_timestamp}/{output_filename}"
    new_session = StitchingSession(
        user_id=current_user.id,
        session_name=f"Stitch {datetime.now().strftime('%b %d, %H:%M')}",
        result_image=rel_path
    )
    db.session.add(new_session)
    db.session.commit()

    return jsonify({
        'success': True, 
        'image_url': url_for('static', filename=rel_path),
        'session_id': new_session.id,
        'session_name': new_session.session_name
    })

@app.route('/delete_session/<int:session_id>', methods=['DELETE'])
@login_required
def delete_session(session_id):
    session = StitchingSession.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(session)
    db.session.commit()
    return jsonify({'success': True})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)