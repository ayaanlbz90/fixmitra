# 🔧 FixMitra — Startup MVP Prototype

**Tagline:** *Aapka Device, Hamari Zimmedari*
**Founder:** Ayaan Shaikh

FixMitra is an interactive, on-demand electronics repair marketplace that lets users select devices, diagnose common hardware/software problems, estimate service costs, choose verified local technicians, and schedule home visits or pickup services.

---

## 🚀 Key Features

- **User Authentication**: Secure signup and login with hashed passwords (`werkzeug.security`).
- **Dynamic Repair Wizard**: Choose device type, brand, problem, and service mode (Home Repair or Pickup), with a live price estimate and a step-progress indicator.
- **City-Based Service Lock**: Home repair visits are restricted to supported cities (Ahmedabad, Kapadvanj, Nadiad, Mahudha, Kathlal, Anand).
- **Safe Delivery Charge**: Automatic ₹150 charge for transit insurance and transport handling.
- **Live Price Estimation**: Real-time pricing feedback for repairs via `/estimate-price`.
- **Technician Selection**: Browse verified specialists, filter by specialty, see ratings, warranty, and repair history.
- **Ratings & Reviews**: Customers can leave a star rating and comment on completed repairs; technician ratings update from real review averages.
- **Service Status Dashboard**: Booking stats (total / active / completed / reviews pending) plus a live status tracker via booking codes (`FM-XXXXXX`).
- **Digital Receipts**: Printable receipts with warranty info.
- **Secured Admin Panel**: Booking + technician management, now gated behind an authenticated `admin` role (previously publicly accessible — fixed).
- **Direct Query Support**: Floating WhatsApp integration for customer queries.
- **Consistent Design System**: Every page (including admin, receipts, and the refurb shop) now shares one design system instead of a mix of custom CSS and unrelated Bootstrap pages.

---

## 🔒 Security Notes (fixed in this revision)

- `/admin` previously had **no authentication check** — it is now behind an `admin_required` decorator that checks for a logged-in user with `role == 'admin'`.
- `SECRET_KEY` now falls back to a securely generated random value per process start instead of a hardcoded string. **Set a real `SECRET_KEY` environment variable in production** so sessions survive restarts.
- `create_db.py` had a bug where the seeded admin account's password column stored the plaintext value (`2007`) instead of the intended hash, because the hashed value was passed as an unused extra bind parameter. This is fixed — the seeded admin login is now `ayaan@fixmitra.com` / `password123`.

---

## 📂 Project Architecture

```text
fixmitra/
│
├── static/
│   ├── css/
│   │   └── style.css        # Unified design system (indigo/teal, light theme)
│   └── js/
│       └── main.js
│
├── templates/
│   ├── base.html
│   ├── index.html            # Full landing page: hero, stats, how-it-works, testimonials, FAQ
│   ├── wizard.html
│   ├── technicians.html       # Now supports specialty filtering + review counts
│   ├── booking.html
│   ├── payment.html
│   ├── track.html
│   ├── dashboard.html         # Now shows stats + lets users leave reviews
│   ├── admin.html             # Restyled + secured + shows stats
│   ├── receipt.html
│   ├── login.html
│   ├── register.html
│   ├── about.html
│   └── shop.html
│
├── app.py
├── create_db.py
├── database.db
├── requirements.txt
└── README.md
```

## Getting Started

```bash
pip install -r requirements.txt
python create_db.py   # (re)creates database.db with seed data
python app.py          # runs on http://127.0.0.1:5000
```

Admin login: `ayaan@fixmitra.com` / `password123`
