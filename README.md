# CSV Viewer

A full-stack Flask web application that allows authenticated users to upload CSV files and view their data in a clean and organized table.

## Features

- Username and password authentication
- Secure password hashing using Werkzeug
- Google Sign-In using OAuth 2.0 / OpenID Connect
- PostgreSQL database integration
- Login timestamp tracking
- CSV file upload
- CSV processing using Pandas
- Session-based authentication
- Logout functionality
- Responsive and professional dark-themed interface
- Environment variables for sensitive credentials

## Technologies Used

- Python
- Flask
- Pandas
- PostgreSQL
- Psycopg
- Authlib
- Werkzeug
- HTML
- CSS
- Git
- GitHub

## Project Structure

CSV_VIEWER/
│
├── app.py
├── .gitignore
│
├── static/
│   └── style.css
│
└── templates/
    ├── index.html
    ├── login.html
    └── register.html

The `.env` file is intentionally excluded from the repository because it contains sensitive credentials.

## How It Works

### User Authentication

Users can access the application through two authentication methods:

1. Username and password
2. Google Sign-In

Passwords are securely hashed before being stored in PostgreSQL.

### Google Authentication

The application uses Google OAuth 2.0 / OpenID Connect for Google Sign-In.

The authentication flow is:

Login Page
    ↓
Continue with Google
    ↓
Google Authentication
    ↓
Flask Callback
    ↓
Find or Create User
    ↓
Create Flask Session
    ↓
Dashboard

Google handles the user's Google credentials. The application does not receive or store the user's Google password.

### CSV Processing

Once authenticated, users can upload a CSV file.

The processing flow is:

Select CSV File
    ↓
Flask receives the uploaded file
    ↓
Pandas reads the CSV
    ↓
Pandas DataFrame
    ↓
DataFrame converted to HTML
    ↓
Data displayed in the dashboard

## Running with Docker

### Prerequisites
- Docker Desktop installed
- PostgreSQL running
- Existing `csv_viewer` database configured

### Run the application

```bash
docker compose up --build
## Local Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Atreyee2005/CSV_VIEWER.git
cd CSV_VIEWER
