from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'school.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_EXT = {'png','jpg','jpeg','gif'}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change_this_to_a_random_secret'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS notices (
        id INTEGER PRIMARY KEY,
        title TEXT,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY,
        roll_no TEXT,
        name TEXT,
        class TEXT,
        marks TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS admissions (
        id INTEGER PRIMARY KEY,
        student_name TEXT,
        class_applied TEXT,
        parent_phone TEXT,
        message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    # create default admin if not exists
    cur.execute('SELECT * FROM admin WHERE username=?', ('admin',))
    if not cur.fetchone():
        pwd = generate_password_hash('admin123')
        cur.execute('INSERT INTO admin (username,password) VALUES (?,?)', ('admin', pwd))
        conn.commit()
    conn.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXT

@app.before_first_request
def setup():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    init_db()

@app.route('/')
def index():
    conn = get_db()
    notices = conn.execute('SELECT * FROM notices ORDER BY created_at DESC LIMIT 5').fetchall()
    conn.close()
    return render_template('index.html', notices=notices)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/gallery', methods=['GET','POST'])
def gallery():
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No file part'); return redirect(request.url)
        file = request.files['image']
        if file.filename == '':
            flash('No selected file'); return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('Image uploaded')
            return redirect(url_for('gallery'))
    images = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('gallery.html', images=images)

@app.route('/admission', methods=['GET','POST'])
def admission():
    if request.method == 'POST':
        name = request.form.get('name')
        c = request.form.get('class_applied')
        phone = request.form.get('parent_phone')
        msg = request.form.get('message')
        conn = get_db()
        conn.execute('INSERT INTO admissions (student_name,class_applied,parent_phone,message) VALUES (?,?,?,?)',
                     (name,c,phone,msg))
        conn.commit()
        conn.close()
        flash('Admission form submitted. We will contact you.')
        return redirect(url_for('admission'))
    return render_template('admission.html')

@app.route('/contact', methods=['GET','POST'])
def contact():
    if request.method == 'POST':
        # for simplicity just flash
        flash('Thank you for contacting us. We will reply soon.')
        return redirect(url_for('contact'))
    return render_template('contact.html')

# Admin
@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = get_db()
        admin = conn.execute('SELECT * FROM admin WHERE username=?', (username,)).fetchone()
        conn.close()
        if admin and check_password_hash(admin['password'], password):
            session['admin'] = username
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

def admin_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get('admin'):
            return redirect(url_for('admin_login'))
        return func(*args, **kwargs)
    return wrapper

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    conn = get_db()
    notices = conn.execute('SELECT * FROM notices ORDER BY created_at DESC').fetchall()
    results = conn.execute('SELECT * FROM results ORDER BY id DESC').fetchall()
    admissions = conn.execute('SELECT * FROM admissions ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin_dashboard.html', notices=notices, results=results, admissions=admissions)

@app.route('/admin/add_notice', methods=['POST'])
@admin_required
def add_notice():
    title = request.form.get('title')
    content = request.form.get('content')
    conn = get_db()
    conn.execute('INSERT INTO notices (title,content) VALUES (?,?)', (title,content))
    conn.commit(); conn.close()
    flash('Notice added')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_result', methods=['POST'])
@admin_required
def add_result():
    roll = request.form.get('roll_no')
    name = request.form.get('name')
    cls = request.form.get('class')
    marks = request.form.get('marks')
    conn = get_db()
    conn.execute('INSERT INTO results (roll_no,name,class,marks) VALUES (?,?,?,?)', (roll,name,cls,marks))
    conn.commit(); conn.close()
    flash('Result added')
    return redirect(url_for('admin_dashboard'))

# Student
@app.route('/student/result', methods=['GET','POST'])
def student_result():
    result = None
    if request.method == 'POST':
        roll = request.form.get('roll_no')
        conn = get_db()
        result = conn.execute('SELECT * FROM results WHERE roll_no=?', (roll,)).fetchone()
        conn.close()
        if not result:
            flash('Result not found for this roll number')
    return render_template('student_result.html', result=result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
