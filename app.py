import os
import sqlite3
from datetime import datetime
from flask import (Flask, render_template, request, redirect, 
                   url_for, session, jsonify)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
DB_PATH = 'fixmitra.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Create bookings table with payment columns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            service_type TEXT,
            status TEXT DEFAULT 'Pending',
            payment_method TEXT,
            payment_status TEXT DEFAULT 'Unpaid'
        )
    ''')

    # 2. Create technicians table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS technicians (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            rating REAL,
            repairs_completed INTEGER,
            distance_km REAL,
            warranty_days INTEGER,
            specialty TEXT,
            verified INTEGER
        )
    ''')

    # 3. Clear old technician data so new values insert cleanly
    cursor.execute("DELETE FROM technicians")

    # 4. Seed updated technicians list
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

# Run database setup on startup
init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/technicians')
def technicians_page():
    conn = get_db()
    techs = conn.execute('SELECT * FROM technicians').fetchall()
    conn.close()
    return render_template('technicians.html', technicians=techs)

@app.route('/book-service', methods=['POST'])
def book_service():
    name = request.form.get('customer_name')
    service = request.form.get('service_type')
    payment_method = request.form.get('payment_method')

    # Set initial payment status based on user selection
    if payment_method == 'pay_after':
        payment_status = "Unpaid (Pay After Service)"
    else:
        payment_status = "Paid Online"

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO bookings (customer_name, service_type, payment_method, payment_status)
        VALUES (?, ?, ?, ?)
    ''', (name, service, payment_method, payment_status))
    conn.commit()
    booking_id = cursor.lastrowid
    conn.close()

    return redirect(f'/track-order/{booking_id}')

@app.route('/track-order/<int:booking_id>')
def track_order(booking_id):
    conn = get_db()
    booking = conn.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,)).fetchone()
    conn.close()
    if not booking:
        return "Booking not found", 404
    return render_template('track_order.html', booking=booking)

@app.route('/receipt/<int:booking_id>')
def receipt(booking_id):
    conn = get_db()
    booking = conn.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,)).fetchone()
    conn.close()
    if not booking:
        return "Receipt not found", 404
    return render_template('receipt.html', booking=booking)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    conn = get_db()
    if request.method == 'POST':
        booking_id = request.form.get('booking_id')
        new_status = request.form.get('status')
        conn.execute('UPDATE bookings SET status = ? WHERE id = ?', (new_status, booking_id))
        conn.commit()

    bookings = conn.execute('SELECT * FROM bookings ORDER BY id DESC').fetchall()
    techs = conn.execute('SELECT * FROM technicians').fetchall()
    conn.close()
    return render_template('admin.html', bookings=bookings, technicians=techs)

@app.route('/admin/complete-payment', methods=['POST'])
def complete_payment():
    booking_id = request.form.get('booking_id')
    conn = get_db()
    conn.execute('''
        UPDATE bookings 
        SET payment_status = 'Paid (Cash/UPI on Delivery)', status = 'Completed' 
        WHERE id = ?
    ''', (booking_id,))
    conn.commit()
    conn.close()
    return redirect('/admin')

@app.route('/admin-db-access')
def admin_db_access():
    key = request.args.get('key')
    if key != "fixmitra123":
        return "Unauthorized Access", 403

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = cursor.fetchall()
        
        content_html = ""
        for (table_name,) in tables:
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = [col[1] for col in cursor.fetchall()]
            
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()

            headers = "".join([f"<th>{col}</th>" for col in columns])
            body_rows = "".join([f"<tr>{''.join([f'<td>{cell}</td>' for cell in row])}</tr>" for row in rows])

            content_html += f"""
            <h3>Table: {table_name} ({len(rows)} rows)</h3>
            <div style="overflow-x:auto; margin-bottom:20px;">
                <table><tr>{headers}</tr>{body_rows if body_rows else '<tr><td colspan="' + str(len(columns)) + '">Empty</td></tr>'}</table>
            </div>
            """
    except Exception as e:
        conn.close()
        return f"Database error: {str(e)}"

    conn.close()

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>FixMitra DB View</title>
        <style>
            body {{ background: #121212; color: #fff; font-family: sans-serif; padding: 20px; }}
            table {{ width: 100%; border-collapse: collapse; background: #1e1e1e; }}
            th, td {{ padding: 8px; border: 1px solid #333; font-size: 13px; }}
            th {{ color: #00bcd4; background: #252525; }}
        </style>
    </head>
    <body>
        <h2>FixMitra Production Database</h2>
        {content_html if content_html else '<p>No tables found.</p>'}
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=True)