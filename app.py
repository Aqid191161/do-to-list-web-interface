from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = 'secretkey123'  # Ganti dengan yang lebih aman
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Model User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Model Task dengan Kategori
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    time = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Tambah kategori

# Buat database dan akun default
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        hashed_password = bcrypt.generate_password_hash('2341').decode('utf-8')
        db.session.add(User(username='admin', password=hashed_password))
        db.session.commit()

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('todo'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    
    if user and bcrypt.check_password_hash(user.password, password):
        session['user_id'] = user.id
        session.permanent = False  # Sesi akan hilang setelah browser ditutup
        return redirect(url_for('todo'))
    
    return "Login gagal! Coba lagi."

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/todo')
def todo():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    category_filter = request.args.get('category')
    
    if category_filter:
        tasks = Task.query.filter_by(user_id=session['user_id'], category=category_filter).all()
    else:
        tasks = Task.query.filter_by(user_id=session['user_id']).all()
    
    categories = ["Pekerjaan", "Pribadi", "Pendidikan", "Kesehatan", "Lainnya"]
    
    return render_template('todo.html', tasks=tasks, categories=categories, selected_category=category_filter)

@app.route('/add_task', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    title = request.form['title']
    description = request.form['description']
    time = request.form['time']
    category = request.form['category']
    
    new_task = Task(user_id=session['user_id'], title=title, description=description, time=time, category=category)
    db.session.add(new_task)
    db.session.commit()
    
    return redirect(url_for('todo'))

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    task = Task.query.get(task_id)
    if task and task.user_id == session['user_id']:
        db.session.delete(task)
        db.session.commit()
    
    return redirect(url_for('todo'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
