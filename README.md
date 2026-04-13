# TaskMatch (Fixr)

**CS/SE 4347 Database Systems — Spring 2026**

A full-stack web application that connects clients with service providers using AI-powered problem classification. Users describe their home repair issue in natural language, and the system uses a Gemini LLM to identify the correct service category and match them with qualified local providers.

## Team

| Name | NetID |
|------|-------|
| Daniel Nguyen | dxn230012 |
| Oluwadamilare Sunmola | oas222005 |
| Steven Martinez Sanchez | sxm200191 |
| Rovin Raj | rvr220000 |

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript (Jinja2 templates)
- **Backend:** Python / Flask
- **Database:** MySQL
- **AI Classification:** Google Gemini API (with keyword fallback)
- **Auth:** Werkzeug password hashing, Flask sessions

## Prerequisites

- Python 3.10+
- MySQL 8.0+
- A Google Gemini API key (optional — keyword fallback works without one)

## Installation & Setup

### 1. Clone and install dependencies

```bash
cd taskmatch
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your MySQL credentials and (optionally) your Gemini API key:

```
SECRET_KEY=change-this-to-a-random-secret-key
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=taskmatch
MYSQL_PORT=3306
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Create and seed the database

```bash
mysql -u root -p < sql/create.sql
mysql -u root -p --local-infile=1 taskmatch < sql/load.sql
```

> **Note:** If `LOAD DATA LOCAL INFILE` is disabled, you may need to add
> `--local-infile=1` to both the client and set `local_infile=1` in your MySQL config.
>
> Alternative: run `create.sql` first, then use the Python seed script:
> ```bash
> python scripts/seed_db.py
> ```

### 4. Run the application

```bash
python run.py
```

Visit **http://localhost:5000** in your browser.

## Test Accounts

All seed accounts use the password **`password123`**.

| Email | Role | Name |
|-------|------|------|
| jordan@email.com | Client | Jordan Smith |
| marcus@email.com | Provider | Marcus Rivera (Plumbing) |
| sandra@email.com | Provider | Sandra Chen (Electrical) |
| james@email.com | Provider | James Thornton (Carpentry) |
| diane@email.com | Provider | Diane Kim (Plumbing) |
| admin@taskmatch.com | Admin | Admin User |

## Features

### For Clients
- **AI Problem Matching:** Describe your issue in natural language → system classifies the trade → shows matching providers
- **Provider Search:** Browse results with provider cards showing ratings, rates, and bios
- **Booking Flow:** 3-step booking wizard (Date/Time → Job Details → Confirmation)
- **Messaging:** Real-time chat with providers
- **Dashboard:** Track active jobs, completed bookings, and past requests
- **Reviews:** Rate and review providers after job completion

### For Providers
- **Dashboard:** View incoming bookings, accept/decline/complete jobs
- **Listing Management:** Create, edit, and delete service listings across categories
- **Profile Page:** Public profile with bio, ratings, reviews, and booking panel
- **Messaging:** Communicate with clients

### For All Users
- **Account Management:** Update profile, change password, delete account
- **Responsive Design:** Works on desktop browsers

## Project Structure

```
taskmatch/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration from .env
│   ├── db.py                # MySQL connection pool
│   ├── models.py            # Data access layer (all CRUD)
│   ├── routes.py            # All Flask routes
│   ├── templates/           # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── login.html
│   │   ├── signup.html
│   │   ├── dashboard.html
│   │   ├── results.html
│   │   ├── provider_profile.html
│   │   ├── booking.html
│   │   ├── messages.html
│   │   ├── account.html
│   │   └── new_listing.html
│   └── static/
│       ├── css/styles.css
│       ├── js/main.js
│       └── images/
├── data/                    # CSV seed data (10 files)
├── sql/
│   ├── create.sql           # DDL — creates all 10 tables
│   └── load.sql             # Bulk loads CSV data
├── scripts/
│   ├── classify_service.py  # Standalone LLM classifier
│   └── seed_db.py           # Python-based DB seeder
├── run.py                   # Entry point
├── requirements.txt
├── .env.example
└── README.md
```

## Database Schema (10 Tables)

1. **users** — All accounts (clients, providers, admins)
2. **locations** — User addresses for proximity matching
3. **service_categories** — Standardized trade categories
4. **provider_profiles** — Provider bios, rates, ratings
5. **service_listings** — Individual services offered by providers
6. **listing_images** — Photos for listings
7. **job_requests** — Client problem submissions with LLM-matched category
8. **bookings** — Scheduled jobs linking requests to providers
9. **reviews** — Post-completion ratings and comments
10. **messages** — Client-provider communication

## How the LLM Integration Works

1. Client enters a problem description on the home page
2. The `/search` route sends the description to the Gemini API with the list of service categories
3. Gemini returns exactly one category name (e.g., "Plumbing")
4. The system queries the database for providers with active listings in that category
5. Results are displayed ranked by rating
6. If the Gemini API is unavailable, a keyword-based fallback classifier is used

## CRUD Operations

| Operation | Route | Method |
|-----------|-------|--------|
| Create User | `/signup` | POST |
| Read User | `/account` | GET |
| Update User | `/account` | POST |
| Delete User | `/account/delete` | POST |
| Create Booking | `/book/<id>` | POST |
| Read Bookings | `/dashboard` | GET |
| Update Booking Status | `/booking/<id>/status` | POST |
| Create Review | `/review/<id>` | POST |
| Create Listing | `/listings/new` | POST |
| Update Listing | `/listings/<id>/edit` | POST |
| Delete Listing | `/listings/<id>/delete` | POST |
| Send Message | `/api/messages/send` | POST |
| Read Messages | `/messages/<id>` | GET |
| Search Providers | `/search` | POST |
