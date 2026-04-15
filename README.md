# HostelGrid — Hostel Management System

A full-stack Django web application for managing student hostels. It handles student records, room and hostel management, room allocations, fee tracking, and complaint handling — with separate role-based portals for admins and students.

---

## Table of Contents

1. [Tech Stack](#tech-stack)
2. [Project Structure](#project-structure)
3. [Data Models](#data-models)
4. [Authentication & Roles](#authentication--roles)
5. [Features by Module](#features-by-module)
6. [URL Reference](#url-reference)
7. [Forms](#forms)
8. [Email Notifications](#email-notifications)
9. [Admin Panel](#admin-panel)
10. [UI & Templates](#ui--templates)
11. [Setup & Local Development](#setup--local-development)
12. [Environment Variables](#environment-variables)
13. [Deployment (Render)](#deployment-render)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Django 5.2 |
| Database | PostgreSQL (Supabase or any Postgres instance) |
| ORM | Django ORM with `managed = False` for Supabase-synced tables |
| Frontend | Bootstrap 5.3, Bootstrap Icons, Geist Mono + Major Mono Display (Google Fonts) |
| Forms | django-crispy-forms + crispy-bootstrap5 |
| Static files | WhiteNoise (compressed + manifest) |
| Production server | Gunicorn |
| Email | Gmail SMTP via Django's `send_mail` |
| Config | python-decouple + python-dotenv |
| DB URL parsing | dj-database-url |

---

## Project Structure

```
hostel_management/        # Core Django project
  settings.py             # All configuration (DB, email, static, auth)
  urls.py                 # Root URL dispatcher
  views.py                # Home, login, logout, register, dashboard
  email_utils.py          # HTML + plain-text email helpers

students/                 # Student, UserProfile, Allocation app
  models.py               # UserProfile, Student, StudentProfile, Allocation
  views.py                # CRUD for students, allocations, profile editing
  forms.py                # StudentForm, AllocationForm, StudentProfileForm
  urls.py                 # /students/* routes
  admin.py                # Django admin registrations

rooms/                    # Hostel and Room app
  models.py               # Hostel, Room
  views.py                # CRUD for hostels and rooms
  forms.py                # HostelForm, RoomForm
  urls.py                 # /rooms/* routes
  admin.py                # Django admin registrations

complaints/               # Complaint app
  models.py               # Complaint
  views.py                # Submit, view, update, resolve, delete complaints
  forms.py                # ComplaintForm, ComplaintUpdateForm
  urls.py                 # /complaints/* routes
  admin.py                # Django admin registrations

payments/                 # Fee and Payment app
  models.py               # Fee, PaymentRecord, Payment (proxy)
  views.py                # CRUD for fees, student payment interface
  forms.py                # FeeForm, FeeUpdateForm
  urls.py                 # /payments/* routes
  admin.py                # Django admin registrations

templates/
  base.html               # Legacy base (gradient navbar, Bootstrap)
  base_admin.html         # Admin portal base (glassmorphism sidebar, dark/light theme)
  base_student.html       # Student portal base (glassmorphism sidebar, dark/light theme)
  login.html              # Split-screen login (Admin / Student toggle)
  register.html           # Student registration page
  dashboard_admin.html    # Admin dashboard with stats and quick actions
  dashboard_student.html  # Student dashboard with profile, room, payments, complaints
  students/               # Student CRUD + allocation + profile templates
  rooms/                  # Hostel and room CRUD templates
  complaints/             # Complaint templates (admin and student variants)
  payments/               # Payment templates (admin and student variants)

static/
  css/style.css           # Custom styles
  js/main.js              # Custom JS
  images/doodle.jpg       # Login/register page background
  favicon_io/             # Favicon assets (all sizes + webmanifest)
```

---

## Data Models

### `students` app

**UserProfile**
Extends Django's built-in `User` with a role field. Stored in the `user_profile` table (Django-managed).

| Field | Type | Notes |
|---|---|---|
| user | OneToOneField(User) | Links to Django auth user |
| role | CharField | `admin`, `student`, or `staff` |
| phone | CharField | Optional |

**Student**
Maps directly to the Supabase `student` table (`managed = False`).

| Field | Type | Notes |
|---|---|---|
| studentid | AutoField (PK) | |
| name | CharField | Required |
| gender | CharField | `Male` or `Female` |
| department | CharField | CSE, ECE, EE, ME, CE, IT, CHE, BT |
| phone | CharField | Optional |

**StudentProfile**
Extended personal details for a student. Django-managed table.

| Field | Type | Notes |
|---|---|---|
| student | OneToOneField(Student) | |
| address | TextField | Permanent address |
| father_name / mother_name | CharField | |
| father_phone / mother_phone | CharField | |
| emergency_contact / emergency_phone | CharField | |
| date_of_birth | DateField | |
| hostel_mess | CharField | Auto-assigned randomly if not set: Buddies & Bites, Eat n' Chill, The Late Plate |

**Allocation**
Maps to the Supabase `allocation` table (`managed = False`).

| Field | Type | Notes |
|---|---|---|
| allocationid | AutoField (PK) | |
| student | ForeignKey(Student) | |
| room | ForeignKey(Room) | |
| date_of_allocation | DateField | Auto-set to today on creation |

---

### `rooms` app

**Hostel**
Maps to the Supabase `hostel` table (`managed = False`).

| Field | Type | Notes |
|---|---|---|
| hostelid | AutoField (PK) | |
| name | CharField | |
| location | CharField | |
| totalrooms | IntegerField | |

**Room**
Maps to the Supabase `room` table (`managed = False`).

| Field | Type | Notes |
|---|---|---|
| roomid | AutoField (PK) | |
| hostelid | ForeignKey(Hostel) | |
| roomnumber | CharField | |
| capacity | IntegerField | |
| type | CharField | e.g., Single, Double, Triple |

Room has helper methods: `current_occupancy()`, `available_spaces()`, `is_full()`, `occupancy_percentage()`.

---

### `complaints` app

**Complaint**
Django-managed table (not in original Supabase schema).

| Field | Type | Notes |
|---|---|---|
| student | ForeignKey(Student) | |
| category | CharField | maintenance, cleanliness, electricity, water, security, other |
| subject | CharField | Max 200 chars |
| description | TextField | |
| status | CharField | `pending`, `in_progress`, `resolved` |
| created_at / updated_at | DateTimeField | Auto-set |
| resolved_at | DateTimeField | Set when admin resolves |
| admin_remarks | TextField | Optional admin notes |

---

### `payments` app

**Fee**
Maps to the Supabase `fee` table (`managed = False`).

| Field | Type | Notes |
|---|---|---|
| feeid | AutoField (PK) | |
| studentid | ForeignKey(Student) | |
| amount | DecimalField | 10 digits, 2 decimal places |
| duedate | DateField | |
| status | CharField | `Paid` or `Not Paid` |

**PaymentRecord**
Django-managed table that adds payment type metadata to a Fee.

| Field | Type | Notes |
|---|---|---|
| fee | OneToOneField(Fee) | |
| payment_type | CharField | Fees, Hostel, Fests, Clubs/Chapters |
| created_at | DateTimeField | Auto-set |

**Payment**
Proxy model of `Fee` kept for backward compatibility.

---

## Authentication & Roles

The login page (`/login/`) has a toggle between **Admin** and **Student** login modes.

- **Admin login**: Requires `user.is_superuser = True` or `user.profile.role == 'admin'`
- **Student login**: Requires `user.profile.role == 'student'`

Students can self-register at `/register/`. Registration creates a Django `User` and a `UserProfile` with `role='student'`.

Superusers are created via `python manage.py createsuperuser` or the Django admin at `/admin/`.

After login, all users land on `/dashboard/`. The view checks the role and renders either `dashboard_admin.html` or `dashboard_student.html`.

Student-to-Student-record matching is done by comparing `request.user.username` against `Student.name` (case-insensitive contains). If no match, it falls back to matching `studentid` against `user.id`.

---

## Features by Module

### Admin Dashboard (`/dashboard/`)
- Total student count
- Occupied vs available room count (a room is "occupied" only when `current_occupancy >= capacity`)
- Pending complaint count
- Total fees collected (sum of all `Fee` records with `status = 'Paid'`, case-insensitive)
- Table of 5 most recent complaints with status badges
- Table of up to 5 rooms with available beds, showing bed count
- Quick action buttons: Add Student, Add Room, Add Payment, Add Hostel
- Fees amount auto-scales font size to fit the card using JavaScript

### Student Dashboard (`/dashboard/`)
- Profile completion alert if address, father name, or mother name is missing
- Personal information card: name, student ID, gender, department, DOB, phone, email, address
- Parent information section (shown if at least one parent name is filled)
- Combined stat card: pending payment count + complaint count
- Room allocation card: room number, hostel, type, capacity, allocation date, mess assignment
- Pending payment dues table with payment type, amount, due date, status
- Recent complaints table with subject, status, date
- Recent paid payments table
- Quick actions: Submit Complaint, View Complaints, Make Payment, Payment History

### Students (`/students/`)
- List all students (admin only)
- Add student: name, gender, department, phone (admin only)
- Edit student details (admin only)
- Delete student with confirmation (admin only)
- View student detail: personal info, all allocations, current room, profile (admin or own student)
- Edit student profile: address, parent details, emergency contact, DOB, mess preference (student only)

### Room Allocations (`/students/allocations/`)
- List all allocations with student and room info (admin only)
- Add allocation: student dropdown, room dropdown (only shows rooms with available beds, with availability count shown), date picker — date auto-set to today (admin only)
- Delete allocation with confirmation (admin only)

### Rooms (`/rooms/`)
- List all rooms grouped by hostel, sorted numerically by room number (all authenticated users)
- Shows total rooms, occupied rooms, available rooms counts
- Add / edit / delete rooms (admin only)
- Room detail: shows all current allocations and students in that room

### Hostels (`/rooms/hostels/`)
- List all hostels (all authenticated users)
- Add / edit / delete hostels (admin only)
- Hostel detail: shows all rooms in that hostel

### Complaints (`/complaints/`)
- Admin sees all complaints; students see only their own
- Submit complaint: category, subject, description — triggers confirmation email to student
- View complaint detail (admin sees admin template, student sees student template)
- Update complaint status and add admin remarks (admin only)
- Resolve complaint: marks as resolved and deletes the record (admin only)
- Delete complaint: students can delete their own; admins can delete any

### Payments (`/payments/`)
- Admin sees all fee records; students see only their own
- Add fee record: student, amount, due date, status, optional payment type (admin only)
- Edit fee record and update/create/delete associated PaymentRecord (admin only)
- Update payment status only (admin only)
- Delete fee record (admin only)
- Student payment interface (`/payments/make/`): dropdown for payment type (Fees, Hostel, Fests, Clubs/Chapters), amount input — creates a `Fee` record with `status='Paid'` and a `PaymentRecord`, then sends confirmation email

---

## URL Reference

### Core (`hostel_management/urls.py`)

| URL | Name | View |
|---|---|---|
| `/` | `home` | Redirects to dashboard or login |
| `/login/` | `login` | Login page |
| `/logout/` | `logout` | Logout |
| `/register/` | `register` | Student registration |
| `/dashboard/` | `dashboard` | Role-based dashboard |
| `/admin/` | — | Django admin panel |

### Students (`/students/`)

| URL | Name | Access |
|---|---|---|
| `/students/` | `student_list` | Admin |
| `/students/add/` | `student_add` | Admin |
| `/students/<pk>/` | `student_detail` | Admin or own student |
| `/students/<pk>/edit/` | `student_edit` | Admin |
| `/students/<pk>/delete/` | `student_delete` | Admin |
| `/students/allocations/` | `allocation_list` | Admin |
| `/students/allocations/add/` | `allocation_add` | Admin |
| `/students/allocations/<pk>/delete/` | `allocation_delete` | Admin |
| `/students/profile/edit/` | `student_profile_edit` | Student |

### Rooms (`/rooms/`)

| URL | Name | Access |
|---|---|---|
| `/rooms/` | `room_list` | All authenticated |
| `/rooms/add/` | `room_add` | Admin |
| `/rooms/<pk>/` | `room_detail` | All authenticated |
| `/rooms/<pk>/edit/` | `room_edit` | Admin |
| `/rooms/<pk>/delete/` | `room_delete` | Admin |
| `/rooms/hostels/` | `hostel_list` | All authenticated |
| `/rooms/hostels/add/` | `hostel_add` | Admin |
| `/rooms/hostels/<pk>/` | `hostel_detail` | All authenticated |
| `/rooms/hostels/<pk>/edit/` | `hostel_edit` | Admin |
| `/rooms/hostels/<pk>/delete/` | `hostel_delete` | Admin |

### Complaints (`/complaints/`)

| URL | Name | Access |
|---|---|---|
| `/complaints/` | `complaint_list` | All authenticated |
| `/complaints/add/` | `complaint_add` | Student |
| `/complaints/<pk>/` | `complaint_detail` | Admin or complaint owner |
| `/complaints/<pk>/update/` | `complaint_update` | Admin |
| `/complaints/<pk>/resolve/` | `complaint_resolve` | Admin |
| `/complaints/<pk>/delete/` | `complaint_delete` | Admin or complaint owner |

### Payments (`/payments/`)

| URL | Name | Access |
|---|---|---|
| `/payments/` | `payment_list` | All authenticated |
| `/payments/add/` | `payment_add` | Admin |
| `/payments/<pk>/` | `payment_detail` | Admin or payment owner |
| `/payments/<pk>/edit/` | `payment_edit` | Admin |
| `/payments/<pk>/update-status/` | `payment_update_status` | Admin |
| `/payments/<pk>/delete/` | `payment_delete` | Admin |
| `/payments/make/` | `student_payment_make` | Student |

---

## Forms

**StudentForm** — Admin adds/edits a student. Fields: name (required), gender, department, phone. All use Bootstrap `form-control` widgets.

**AllocationForm** — Admin allocates a room. Room dropdown is filtered to only show rooms with available beds. Each option shows `Hostel - Room X (Y/Z available)`. Date field uses an HTML date picker.

**StudentProfileForm** — Student edits their own profile. Fields: address, father_name, mother_name, father_phone, mother_phone, date_of_birth, hostel_mess. All fields are marked required on first save.

**HostelForm** — Admin creates/edits a hostel. Fields: name, location, totalrooms.

**RoomForm** — Admin creates/edits a room. Fields: hostelid (hostel dropdown), roomnumber, capacity, type.

**ComplaintForm** — Student submits a complaint. Fields: category (dropdown), subject, description.

**ComplaintUpdateForm** — Admin updates a complaint. Fields: status (dropdown), admin_remarks.

**FeeForm** — Admin creates/edits a fee record. Fields: studentid (dropdown showing ID + name), amount, duedate, status (Paid/Not Paid), payment_type (optional, from PaymentRecord choices). On edit, pre-populates payment_type from the linked PaymentRecord.

**FeeUpdateForm** — Admin updates only the status of a fee. Fields: status.

---

## Email Notifications

Email is sent via Gmail SMTP. Two notification types are implemented in `hostel_management/email_utils.py`:

**Complaint confirmation** (`send_complaint_confirmation_email`)
Triggered when a student submits a complaint. Sends to `request.user.email`. Contains complaint ID, subject, description, status, and submission timestamp. Includes both HTML (styled with inline CSS, gold/orange brand colors) and plain-text versions.

**Payment confirmation** (`send_payment_confirmation_email`)
Triggered when a student makes a payment via the student payment interface. Sends to `request.user.email`. Contains payment ID, payment type, amount (in ₹), status (PAID), and date. Includes both HTML (green brand colors) and plain-text versions.

Both functions use `fail_silently=False` internally but are wrapped in try/except in the views so a failed email never blocks the user action.

To switch to console output during development, change in `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

---

## Admin Panel

The Django admin at `/admin/` has the following registrations:

**students app**
- `UserProfile` — list: user, role, phone; filter by role; search by username/email
- `Student` — list: name, gender, department, phone; filter by gender/department; search by name/phone
- `Allocation` — list: student, room, date; filter by date and hostel; search by student name/room number; date hierarchy on `date_of_allocation`

**rooms app**
- `Hostel` — list: name, location, totalrooms; search by name/location
- `Room` — list: room number, hostel, type, capacity, occupancy (custom `current_occupancy_display` column showing `current/capacity`); filter by hostel and type; search by room number/hostel name

**complaints app**
- `Complaint` — list: subject, student, category, status, created_at; filter by status/category/date; search by subject/description/student name; inline status editing; date hierarchy on `created_at`

**payments app**
- `Fee` — list: student, amount, due date, status; filter by status/due date; search by student name; inline status editing; date hierarchy on `duedate`

---

## UI & Templates

The app has two distinct visual themes depending on the user role:

**Admin portal** (`base_admin.html`)
- Dark/light theme toggle (persisted via `data-theme` attribute on `<html>`)
- Fixed glassmorphism sidebar (280px wide, 20px from edges, frosted glass effect with `backdrop-filter: blur`)
- Grid dot background pattern using CSS `background-image` gradients
- Geist Mono font for all body text, Major Mono Display for the brand wordmark
- Staggered card slide-up animations on page load (`slideUpFade` keyframes with per-child delays)
- Brand colors: `#FFD700` (gold) as primary accent, `#1a1a2e` as dark base
- Sidebar nav items highlight with gold gradient when active
- User avatar shows first letter of username in a gold circle

**Student portal** (`base_student.html`)
- Same dark/light theme toggle and grid background
- Same glassmorphism sidebar with a left-border indicator on active nav items
- Slightly different button color scheme (dark navy primary instead of gold)
- Card hover effect: white outline glow + lift

**Login page** (`login.html`)
- Split-screen layout: left side (gold-to-white gradient) contains the form; right side shows a doodle background image
- Admin / Student toggle buttons switch the `login_type` hidden input and show/hide the student registration link
- Password visibility toggle
- Auto-dismissing error/success notification overlay (slides down from top, auto-hides after 5 seconds)
- Responsive: right section hidden on mobile

**Register page** (`register.html`)
- Same split-screen layout as login
- Client-side validation: all fields required, passwords must match, minimum 8 characters

**Dashboard (Admin)**
- 4 stat cards: Total Students, Occupied Rooms (X/total), Pending Complaints, Fees Collected
- Fees amount uses JavaScript to dynamically shrink font size if the number is too wide for the card
- Recent Complaints table (last 5) with status badges
- Empty Rooms table (up to 5 rooms with available beds)
- Quick action buttons

**Dashboard (Student)**
- Profile completion warning banner if address/parent info is missing
- Personal info card with parent details section
- Combined stat card (pending payments + complaint count)
- Room allocation card with mess assignment badge
- Pending dues table
- Recent complaints and recent paid payments tables
- Quick action buttons

---

## Setup & Local Development

### 1. Clone and create virtual environment

```bash
git clone <repo-url>
cd hostel-management
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your values (see [Environment Variables](#environment-variables) below).

### 4. Run migrations

```bash
python manage.py migrate
```

Note: `Student`, `Room`, `Hostel`, `Allocation`, and `Fee` tables have `managed = False` — Django will not create or alter them. They must already exist in your database (e.g., created via Supabase). Django-managed tables (`UserProfile`, `StudentProfile`, `Complaint`, `PaymentRecord`) will be created by migrations.

### 5. Create a superuser

```bash
python manage.py createsuperuser
```

### 6. Collect static files (optional for dev)

```bash
python manage.py collectstatic
```

### 7. Run the development server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` — you'll be redirected to the login page.

---

## Environment Variables

All variables are read via `python-decouple` (`.env` file or system environment).

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | Yes | Django secret key |
| `DEBUG` | Yes | `True` for development, `False` for production |
| `ALLOWED_HOSTS` | Yes | Comma-separated list of allowed hostnames |
| `DATABASE_URL` | Option A | Full Postgres connection string (used if set) |
| `SUPABASE_HOST` | Option B | Supabase DB host |
| `SUPABASE_DB_NAME` | Option B | Database name (usually `postgres`) |
| `SUPABASE_USER` | Option B | Database user |
| `SUPABASE_PASSWORD` | Option B | Database password |
| `SUPABASE_PORT` | Option B | Database port (usually `5432`) |
| `SUPABASE_URL` | Optional | Supabase project URL (for client SDK use) |
| `SUPABASE_KEY` | Optional | Supabase anon key (for client SDK use) |
| `EMAIL_HOST_USER` | Optional | Gmail address for sending emails |
| `EMAIL_HOST_PASSWORD` | Optional | Gmail App Password |
| `DEFAULT_FROM_EMAIL` | Optional | From address in outgoing emails |
| `SERVER_EMAIL` | Optional | Server error email address |

If `DATABASE_URL` is set, it takes priority over the individual `SUPABASE_*` variables. The `DATABASE_URL` connection is configured with `conn_max_age=600` and `conn_health_checks=True`.

---

## Deployment (Render)

The project is pre-configured for Render.

**`Procfile`**
```
web: gunicorn hostel_management.wsgi --log-file -
```

**`build.sh`** (set as the Build Command in Render)
```bash
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
```

**`runtime.txt`**
```
python-3.11.0
```

**Steps:**
1. Create a new Web Service on Render, connect your repo
2. Set Build Command to `./build.sh`
3. Set Start Command to `gunicorn hostel_management.wsgi --log-file -`
4. Add all environment variables in the Render dashboard
5. Set `DEBUG=False` and add your Render domain to `ALLOWED_HOSTS`
6. Static files are served automatically by WhiteNoise — no separate static hosting needed

---

## Python Version

Python 3.11.0 (see `runtime.txt`)

---

## License

MIT
