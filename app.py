import os
import sqlite3
from datetime import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, 
    url_for, session, jsonify, flash
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fixmitra_secure_key_production")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max limit

DB_PATH = 'database.db'
ALLOWED_CITIES = ["Ahmedabad", "Kapadvanj", "Nadiad", "Mahudha", "Kathlal", "Anand"]

PRICE_DATABASE = {
    'Mobile': {
        'Screen Damage': '₹1,000 - ₹4,500',
        'Battery Problem': '₹800 - ₹2,200',
        'Charging Problem': '₹350 - ₹500',
        'Software Issue': '₹400 - ₹1,000'
    },
    'Laptop': {
        'Screen Damage': '₹2,500 - ₹7,500',
        'Battery Problem': '₹1,500 - ₹4,000',
        'SSD/RAM Upgrade': '₹1,800 - ₹6,000',
        'Overheating': '₹600 - ₹1,200'
    },
    'PC': {
        'Windows Problem': '₹500 - ₹1,200',
        'Hardware Issue': '₹1,000 - ₹5,000',
        'SSD/RAM Upgrade': '₹1,500 - ₹8,000',
        'Data Recovery': '₹2,000 - ₹10,000'
    }
}

# --- DATABASE HELPERS ---

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Create Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'customer'
        )
    ''')
    
    # Create Technicians Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS technicians (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            rating REAL DEFAULT 4.8,
            repairs_completed INTEGER DEFAULT 0,
            distance_km REAL DEFAULT 2.5,
            warranty_days INTEGER DEFAULT 90,
            specialty TEXT,
            verified INTEGER DEFAULT 1
        )
    ''')

    # Create Bookings Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_code TEXT UNIQUE NOT NULL,
            user_id INTEGER,
            user_name TEXT,
            phone TEXT,
            city TEXT,
            device_type TEXT,
            brand TEXT,
            problem TEXT,
            description TEXT,
            service_mode TEXT,
            delivery_charge INTEGER DEFAULT 150,
            estimated_cost TEXT,
            status TEXT DEFAULT 'Booking Confirmed',
            technician_id INTEGER,
            payment_status TEXT DEFAULT 'Unpaid (Pay After Service)',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (technician_id) REFERENCES technicians (id)
        )
    ''')

    # Seed Default Technicians if table is empty
    cursor.execute("SELECT COUNT(*) FROM technicians")
    if cursor.fetchone()[0] == 0:
        demo_techs = [
            ("Milan Mobile", 4.9, 1420, 1.8, 90, "Mobile & accessories Expert", 1),
            ("Precision Micro-Fix Services", 4.8, 980, 2.4, 90, "PC & Laptop Specialist", 1),
            ("Gadget Guru", 4.7, 650, 3.1, 60, "Chip Level Repair", 1),
            ("Khadim Mobile", 4.6, 1120, 4.0, 30, "Screen & Battery Fast Service", 1)
        ]
        cursor.executemany('''
            INSERT INTO technicians (name, rating, repairs_completed, distance_km, warranty_days, specialty, verified)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', demo_techs)

    conn.commit()
    conn.close()

# Initialize DB structure on startup
init_db()

# --- AUTH DECORATOR ---

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# --- AUTHENTICATION ROUTES ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        raw_password = request.form.get('password', '')

        if not name or not email or not raw_password:
            return render_template('register.html', error="All fields are required.")

        hashed_password = generate_password_hash(raw_password)

        conn = get_db()
        try:
            conn.execute('INSERT INTO users (name, email, phone, password) VALUES (?, ?, ?, ?)',
                         (name, email, phone, hashed_password))
            conn.commit()
            conn.close()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('register.html', error="Email is already registered.")

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['user_role'] = user['role']
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid email or password.")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

# --- CORE APPLICATION ROUTES ---

@app.route('/')
def home():
    return render_template('index.html', cities=ALLOWED_CITIES)

@app.route('/wizard')
def wizard():
    return render_template('wizard.html', cities=ALLOWED_CITIES)

@app.route('/estimate-price', methods=['POST'])
def estimate_price():
    data = request.get_json() or {}
    device = data.get('device')
    problem = data.get('problem')
    estimate = PRICE_DATABASE.get(device, {}).get(problem, '₹800 - ₹3,500')
    return jsonify({'estimate': estimate})

@app.route('/technicians', methods=['GET', 'POST'])
@login_required
def technicians():
    conn = get_db()
    techs = conn.execute('SELECT * FROM technicians').fetchall()
    conn.close()

    if request.method == 'POST':
        city = request.form.get('city')
        service_mode = request.form.get('service_mode')

        if service_mode == 'Home Repair' and city not in ALLOWED_CITIES:
            return render_template('wizard.html', cities=ALLOWED_CITIES,
                                   error=f"Home Repair service is currently unavailable in {city}. Please choose Pickup & Repair or select a supported city.")

        session['repair_data'] = {
            'city': city,
            'device': request.form.get('device', 'Mobile'),
            'brand': request.form.get('brand', 'Generic'),
            'problem': request.form.get('problem', 'General Diagnosis'),
            'description': request.form.get('description', ''),
            'service_mode': service_mode,
            'delivery_charge': 150,
            'estimate': request.form.get('estimate', '₹1,000 - ₹3,000')
        }
    return render_template('technicians.html', technicians=techs)

@app.route('/book/<int:tech_id>', methods=['GET', 'POST'])
@login_required
def book(tech_id):
    conn = get_db()
    tech = conn.execute('SELECT * FROM technicians WHERE id = ?', (tech_id,)).fetchone()
    conn.close()

    if not tech:
        flash("Selected technician not found.", "danger")
        return redirect(url_for('technicians'))

    if request.method == 'POST':
        repair_info = session.get('repair_data', {})
        booking_code = f"FM-{datetime.now().strftime('%d%H%M%S')}"

        name = request.form.get('name')
        phone = request.form.get('phone')

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO bookings (
                booking_code, user_id, user_name, phone, city, 
                device_type, brand, problem, description, service_mode, 
                delivery_charge, estimated_cost, technician_id, payment_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            booking_code,
            session.get('user_id'),
            name,
            phone,
            repair_info.get('city', 'Selected City'),
            repair_info.get('device', 'Mobile'),
            repair_info.get('brand', 'Generic'),
            repair_info.get('problem', 'Diagnosis'),
            repair_info.get('description', ''),
            repair_info.get('service_mode', 'Pickup & Repair'),
            repair_info.get('delivery_charge', 150),
            repair_info.get('estimate', '₹1,000 - ₹3,000'),
            tech_id,
            'Unpaid (Pay After Service)'
        ))
        conn.commit()
        conn.close()

        return redirect(url_for('payment', code=booking_code))

    return render_template('booking.html', tech=tech, info=session.get('repair_data', {}))

@app.route('/payment/<code>', methods=['GET', 'POST'])
@login_required
def payment(code):
    conn = get_db()
    booking = conn.execute('SELECT * FROM bookings WHERE booking_code = ? AND user_id = ?', 
                           (code, session['user_id'])).fetchone()

    if not booking:
        conn.close()
        flash("Booking not found.", "danger")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        
        if payment_method == 'pay_later':
            new_payment_status = 'Unpaid (Pay After Service)'
        else:
            new_payment_status = 'Paid'

        conn.execute('UPDATE bookings SET payment_status = ? WHERE booking_code = ?', 
                     (new_payment_status, code))
        conn.commit()
        booking = conn.execute('SELECT * FROM bookings WHERE booking_code = ?', (code,)).fetchone()
        conn.close()
        
        return render_template('payment.html', booking=booking, success=True)

    conn.close()
    return render_template('payment.html', booking=booking, success=False)

@app.route('/track', methods=['GET'])
def track():
    code = request.args.get('code', '').strip()
    booking = None
    if code:
        conn = get_db()
        booking = conn.execute('''
            SELECT b.*, t.name as tech_name, t.warranty_days 
            FROM bookings b 
            LEFT JOIN technicians t ON b.technician_id = t.id 
            WHERE b.booking_code = ?
        ''', (code,)).fetchone()
        conn.close()
    return render_template('track.html', booking=booking, query_code=code)

@app.route('/receipt/<code>')
@login_required
def receipt(code):
    conn = get_db()
    booking = conn.execute('''
        SELECT b.*, t.name as tech_name, t.warranty_days 
        FROM bookings b 
        LEFT JOIN technicians t ON b.technician_id = t.id 
        WHERE b.booking_code = ? AND b.user_id = ?
    ''', (code, session['user_id'])).fetchone()
    conn.close()

    if not booking:
        flash("Receipt not found or permission denied.", "danger")
        return redirect(url_for('dashboard'))

    return render_template('receipt.html', booking=booking)

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    bookings = conn.execute('''
        SELECT b.*, t.name as tech_name 
        FROM bookings b 
        LEFT JOIN technicians t ON b.technician_id = t.id 
        WHERE b.user_id = ?
        ORDER BY b.id DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('dashboard.html', bookings=bookings)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if session.get('user_role') != 'admin':
        flash("Admin privileges required to access this portal.", "danger")
        return redirect(url_for('dashboard'))

    conn = get_db()
    if request.method == 'POST':
        booking_id = request.form.get('booking_id')
        new_status = request.form.get('status')
        new_payment_status = request.form.get('payment_status')
        
        conn.execute('''
            UPDATE bookings 
            SET status = ?, payment_status = ? 
            WHERE id = ?
        ''', (new_status, new_payment_status, booking_id))
        conn.commit()

    bookings = conn.execute('SELECT * FROM bookings ORDER BY id DESC').fetchall()
    techs = conn.execute('SELECT * FROM technicians').fetchall()
    conn.close()
    return render_template('admin.html', bookings=bookings, technicians=techs)

@app.route('/receipt/<code>')
@login_required
def receipt(code):
    conn = get_db()
    # Allow admins to view any receipt, but restrict regular users to their own
    if session.get('user_role') == 'admin':
        booking = conn.execute('''
            SELECT b.*, t.name as tech_name, t.warranty_days 
            FROM bookings b 
            LEFT JOIN technicians t ON b.technician_id = t.id 
            WHERE b.booking_code = ?
        ''', (code,)).fetchone()
    else:
        booking = conn.execute('''
            SELECT b.*, t.name as tech_name, t.warranty_days 
            FROM bookings b 
            LEFT JOIN technicians t ON b.technician_id = t.id 
            WHERE b.booking_code = ? AND b.user_id = ?
        ''', (code, session['user_id'])).fetchone()
    conn.close()

    if not booking:
        flash("Receipt not found or permission denied.", "danger")
        return redirect(url_for('dashboard'))

    return render_template('receipt.html', booking=booking)

if __name__ == '__main__':
    app.run(debug=True, port=5000)