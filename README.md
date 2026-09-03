# 🔧 FixMitra — Startup MVP Prototype

**Tagline:** *Aapka Device, Hamari Zimmedari* **Founder:** Ayaan Shaikh  

FixMitra is an interactive, on-demand electronics repair marketplace that allows users to select devices, diagnose common hardware/software problems, estimate service costs, select verified local technicians, and schedule home visits or pickup services.

---

## 🚀 Key Features

- **User Authentication**: Secure signup and login with hashed passwords (`werkzeug.security`).
- **Dynamic Repair Wizard**: Choose device type, brand, problem, and service mode (Home Repair or Pickup).
- **City-Based Service Lock**: Home repair visits are restricted to supported tier-1 cities (e.g., Ahmedabad, Mumbai, Delhi, Bengaluru, Pune, Hyderabad).
- **Safety Delivery Charge**: Automatic calculation for safe transit, courier insurance, and transport handling (₹150).
- **Live Price Estimation**: Real-time pricing feedback for repairs.
- **Technician Selection**: Browse verified repair specialists, ratings, warranty offers, and completed repair history.
- **Service Status Dashboard**: Real-time status tracker using unique booking codes (`FM-XXXXXX`).
- **Digital Receipts**: Integrated printable receipts complete with digital warranty info.
- **Direct Query Support**: Floating WhatsApp integration for direct user queries.

---

## 📂 Project Architecture

```text
fixmitra/
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── wizard.html
│   ├── technicians.html
│   ├── booking.html
│   ├── payment.html
│   ├── track.html
│   ├── dashboard.html
│   ├── admin.html
│   ├── receipt.html
│   ├── login.html
│   └── register.html
│
├── app.py
├── create_db.py
├── database.db
├── requirements.txt
└── README.md