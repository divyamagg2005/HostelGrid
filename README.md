# HostelGrid

A full-stack hostel management system built with Django 5 and Supabase PostgreSQL. Designed for educational institutions to manage students, rooms, fees, and complaints through role-based dashboards.

Live demo: [https://hostelgrid-x2mo.onrender.com/login/](https://hostelgrid-x2mo.onrender.com/login/)

---

## What it does

HostelGrid has two user roles — Admin/Warden and Student — each with their own dashboard and access level.

Admins can:
- Add, edit, and delete students and their room allocations
- Manage hostels and rooms with real-time occupancy tracking
- Record and update fee/payment entries
- View, update, and resolve student complaints

Students can:
- View their room and hostel details
- Submit and track complaints
- View their payment history and make payments
- Edit their personal profile (address, emergency contacts, etc.)

---

## Tech stack

- Python 3.11 / Django 5.2
- PostgreSQL via Supabase (cloud-hosted)
- Bootstrap 5 + Bootstrap Icons
- Django Crispy Forms
- WhiteNoise (static files)
- Gunicorn (production server)
- Deployed on Render

---

## Project structure

```
hostelocity/
├── hostel_management/      # Django project config (settings, urls, main views)
├── students/               # Student, UserProfile, Allocation models + views
├── rooms/                  # Hostel and Room models + views
├── complaints/             # Complaint model + views
├── payments/               # Fee and PaymentRecord models + views
├── templates/              # All HTML templates (role-specific)
│   ├── base.html
│   ├── dashboard_admin.html
│   ├── dashboard_student.html
│   ├── students/
│   ├── rooms/
│   ├── complaints/
│   └── payments/
├── static/                 # CSS and JS
├── manage.py
├── requirements.txt
├── Procfile
├── build.sh
└── .env.example
```

---

## Local setup

### Prerequisites

- Python 3.11+
- pip
- A [Supabase](https://supabase.com) account (free tier works)

### 1. Clone the repo

```bash
git clone <repository-url>
cd hostelocity
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up Supabase

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Navigate to **Project Settings → Database**
3. Copy your connection credentials (host, user, password, port)

The app uses Django ORM with `managed = False` on the core tables (`student`, `room`, `hostel`, `allocation`, `fee`), meaning those tables must already exist in Supabase. Run the SQL below in the Supabase SQL Editor to create them:

```sql
CREATE TABLE IF NOT EXISTS hostel (
    hostelid SERIAL PRIMARY KEY,
    name VARCHAR(100),
    location VARCHAR(100),
    totalrooms INTEGER
);

CREATE TABLE IF NOT EXISTS room (
    roomid SERIAL PRIMARY KEY,
    hostelid INTEGER REFERENCES hostel(hostelid),
    roomnumber VARCHAR(10),
    capacity INTEGER,
    type VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS student (
    studentid SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    gender VARCHAR(10),
    department VARCHAR(50),
    phone VARCHAR(15)
);

CREATE TABLE IF NOT EXISTS allocation (
    allocationid SERIAL PRIMARY KEY,
    studentid INTEGER REFERENCES student(studentid),
    roomid INTEGER REFERENCES room(roomid),
    date_of_allocation DATE
);

CREATE TABLE IF NOT EXISTS fee (
    feeid SERIAL PRIMARY KEY,
    studentid INTEGER REFERENCES student(studentid),
    amount DECIMAL(10, 2),
    duedate DATE,
    status VARCHAR(20)
);
```

### 5. Configure environment variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

```env
SECRET_KEY=your-django-secret-key
DEBUG=True

SUPABASE_HOST=db.xxxxxxxxx.supabase.co
SUPABASE_DB_NAME=postgres
SUPABASE_USER=postgres
SUPABASE_PASSWORD=your-supabase-password
SUPABASE_PORT=5432

ALLOWED_HOSTS=localhost,127.0.0.1
```

To generate a `SECRET_KEY`:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

> Note: If using Supabase connection pooling, the port is typically `6543` and the user format is `postgres.<project-id>`.

### 6. Run migrations

This creates the Django-managed tables (`user_profile`, `complaint`, `paymentrecord`, `studentprofile`, etc.):

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create a superuser (admin account)

```bash
python manage.py createsuperuser
```

### 8. Collect static files

```bash
python manage.py collectstatic --noinput
```

### 9. Start the development server

```bash
python manage.py runserver
```

Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## First-time usage

### Logging in as Admin

Go to [http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/), select the Admin tab, and log in with your superuser credentials.

The admin dashboard shows:
- Total students, occupied/available rooms, pending complaints, fees collected
- Recent complaints and available rooms with bed counts
- Quick links to add students, rooms, and payments

### Setting up data (recommended order)

1. Add a Hostel — go to Rooms → Hostels → Add Hostel
2. Add Rooms — go to Rooms → Add Room, select the hostel, set capacity and type
3. Add Students — go to Students → Add Student
4. Allocate rooms — go to Students → Allocations → Allocate Room
5. Add fee entries — go to Payments → Add Payment

### Student login

Students register at [/register/](http://127.0.0.1:8000/register/) or are created by the admin. On the login page, they select the Student tab.

The student dashboard shows their room details, pending payments, and recent complaints. Students can submit complaints, make payments, and edit their profile.

---

## URL reference

| URL | Description | Access |
|-----|-------------|--------|
| `/` | Redirects to dashboard or login | All |
| `/login/` | Login (Admin or Student tab) | Public |
| `/logout/` | Logout | Authenticated |
| `/register/` | Student self-registration | Public |
| `/dashboard/` | Role-based dashboard | Authenticated |
| `/students/` | Student list | Admin |
| `/students/add/` | Add student | Admin |
| `/students/<id>/edit/` | Edit student | Admin |
| `/students/<id>/delete/` | Delete student | Admin |
| `/students/allocations/` | Room allocation list | Admin |
| `/students/allocations/add/` | Allocate room to student | Admin |
| `/students/profile/edit/` | Edit own profile | Student |
| `/rooms/` | Room list (grouped by hostel) | Authenticated |
| `/rooms/add/` | Add room | Admin |
| `/rooms/hostels/` | Hostel list | Authenticated |
| `/rooms/hostels/add/` | Add hostel | Admin |
| `/complaints/` | Complaint list (filtered by role) | Authenticated |
| `/complaints/add/` | Submit complaint | Student |
| `/complaints/<id>/update/` | Update complaint status | Admin |
| `/complaints/<id>/resolve/` | Resolve and remove complaint | Admin |
| `/payments/` | Payment list (filtered by role) | Authenticated |
| `/payments/add/` | Add fee entry | Admin |
| `/payments/<id>/update-status/` | Update payment status | Admin |
| `/payments/make/` | Student payment interface | Student |
| `/admin/` | Django admin panel | Superuser |

---

## Database schema

The app maps to these Supabase tables (unmanaged by Django):

- `student` — studentid, name, gender, department, phone
- `hostel` — hostelid, name, location, totalrooms
- `room` — roomid, hostelid (FK), roomnumber, capacity, type
- `allocation` — allocationid, studentid (FK), roomid (FK), date_of_allocation
- `fee` — feeid, studentid (FK), amount, duedate, status

Django manages these additional tables:

- `user_profile` — links Django User to a role (admin/student/staff)
- `students_studentprofile` — extended student info (address, parents, emergency contact, mess)
- `complaint` — category, subject, description, status, admin_remarks, timestamps
- `payments_paymentrecord` — payment type linked to a fee entry

---

## Deployment on Render

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "initial commit"
git remote add origin <your-repo-url>
git push -u origin main
```

### 2. Create a Web Service on Render

1. Go to [render.com](https://render.com) → New → Web Service
2. Connect your GitHub repository
3. Set the following:
   - Build Command: `./build.sh`
   - Start Command: `gunicorn hostel_management.wsgi --log-file -`
   - Environment: Python 3

### 3. Add environment variables on Render

```
SECRET_KEY=your-production-secret-key
DEBUG=False
SUPABASE_HOST=your-supabase-host
SUPABASE_DB_NAME=postgres
SUPABASE_USER=postgres.your-project-id
SUPABASE_PASSWORD=your-password
SUPABASE_PORT=6543
ALLOWED_HOSTS=your-app.onrender.com
```

### 4. Deploy

Click "Create Web Service". Render will run `build.sh` which installs dependencies, collects static files, and runs migrations automatically.

---

## Troubleshooting

**Database connection error**
- Double-check all `SUPABASE_*` values in `.env`
- Make sure your IP is whitelisted in Supabase under Settings → Database → Connection Pooling
- For pooled connections use port `6543`; for direct connections use `5432`

**Static files not loading**
```bash
python manage.py collectstatic --noinput
```

**Migration errors about missing relations**
- The core tables (`student`, `room`, etc.) must be created manually in Supabase first (see step 4 above)
- Django only manages its own tables; it won't create the Supabase-side tables

**Student dashboard shows "profile not found"**
- The student's Django username must partially match their name in the `student` table
- Admin can verify this by checking Students list and the Django admin panel

**Port already in use**
```bash
python manage.py runserver 8001
```

---

## License

MIT
