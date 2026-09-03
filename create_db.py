import sqlite3
from werkzeug.security import generate_password_hash
DB_PATH = 'database.db'
def build_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS users;')
    cursor.execute('DROP TABLE IF EXISTS technicians;')
    cursor.execute('DROP TABLE IF EXISTS bookings;')
    cursor.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, phone TEXT NOT NULL, password TEXT NOT NULL, role TEXT DEFAULT 'customer');''')
    cursor.execute('''CREATE TABLE technicians (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, rating REAL DEFAULT 4.8, repairs_completed INTEGER DEFAULT 0, distance_km REAL DEFAULT 2.5, warranty_days INTEGER DEFAULT 90, specialty TEXT, verified INTEGER DEFAULT 1);''')
    cursor.execute('''CREATE TABLE bookings (id INTEGER PRIMARY KEY AUTOINCREMENT, booking_code TEXT UNIQUE NOT NULL, user_id INTEGER, user_name TEXT, phone TEXT, city TEXT, device_type TEXT, brand TEXT, problem TEXT, description TEXT, service_mode TEXT, delivery_charge INTEGER DEFAULT 150, estimated_cost TEXT, status TEXT DEFAULT 'Booking Confirmed', technician_id INTEGER, payment_status TEXT DEFAULT 'Pending', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);''')
    hashed_password = generate_password_hash('password123')
    cursor.execute('''INSERT INTO users (name, email, phone, password, role) VALUES ('Ayaan Shaikh', 'ayaan@fixmitra.com', '+919876543210', ?, 'admin')''', (hashed_password,))
    demo_techs = [("Aarav Electronics ^& Tech", 4.9, 1420, 1.8, 90, "Mobile ^& Laptop Expert", 1), ("Precision Micro-Fix Services", 4.8, 980, 2.4, 90, "PC ^& Laptop Specialist", 1), ("NexGen Hardware Solutions", 4.7, 650, 3.1, 60, "Chip Level Repair", 1), ("QuickCare Mobile Lab", 4.6, 1120, 4.0, 30, "Screen ^& Battery Fast Service", 1)]
    cursor.executemany('''INSERT INTO technicians (name, rating, repairs_completed, distance_km, warranty_days, specialty, verified) VALUES (?, ?, ?, ?, ?, ?, ?)''', demo_techs)
    conn.commit()
    conn.close()
    print("Database database.db successfully generated and seeded.")
if __name__ == '__main__':
    build_database()
