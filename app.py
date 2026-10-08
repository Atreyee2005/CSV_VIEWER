import os

import pandas as pd
import psycopg

from dotenv import load_dotenv
from flask import Flask, request, render_template, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.integrations.flask_client import OAuth


# Load variables from .env
load_dotenv()


# Create Flask application
app = Flask(__name__)

# Flask session secret key
app.secret_key = os.getenv("FLASK_SECRET_KEY")


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

conn = psycopg.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)


# --------------------------------------------------
# GOOGLE OAUTH SETUP
# --------------------------------------------------

oauth = OAuth(app)

google = oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile"
    }
)


# --------------------------------------------------
# GOOGLE LOGIN
# --------------------------------------------------

@app.route("/signin/google")
def google_login():

    redirect_uri = "http://127.0.0.1:5000/auth/google"

    return google.authorize_redirect(
        redirect_uri,
        prompt="select_account"
    )


# --------------------------------------------------
# GOOGLE CALLBACK
# --------------------------------------------------

@app.route("/auth/google")
def google_callback():

    # Get the access token from Google
    token = google.authorize_access_token()

    # Get information about the Google account
    user_info = google.userinfo()

    # Google's unique ID for this user
    google_id = user_info["sub"]

    cur = conn.cursor()

    # Check whether this Google user already exists
    cur.execute(
        "SELECT id FROM users WHERE google_id = %s",
        (google_id,)
    )

    user = cur.fetchone()

    # Existing Google user
    if user:

        cur.execute(
            """
            UPDATE users
            SET login_timestamp = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (user[0],)
        )

        conn.commit()

        session["user_id"] = user[0]

        return redirect("/dashboard")

    # New Google user
    cur.execute(
        """
        INSERT INTO users
        (username, google_id, login_timestamp)
        VALUES (%s, %s, CURRENT_TIMESTAMP)
        RETURNING id
        """,
        (user_info["email"], google_id)
    )

    user_id = cur.fetchone()[0]

    conn.commit()

    # Store our own database user ID in the Flask session
    session["user_id"] = user_id

    return redirect("/dashboard")


# --------------------------------------------------
# HOME / LOGIN PAGE
# --------------------------------------------------

@app.route("/")
def home():

    return render_template("login.html")


# --------------------------------------------------
# NORMAL LOGIN
# --------------------------------------------------

@app.route("/login", methods=["POST"])
def login():

    username = request.form.get("username")
    password = request.form.get("password")

    cur = conn.cursor()

    # Find the user
    cur.execute(
        """
        SELECT id, password_hash
        FROM users
        WHERE username = %s
        """,
        (username,)
    )

    user = cur.fetchone()

    # Username doesn't exist
    if user is None:

        return "Invalid username or password"

    # Check entered password against stored password hash
    if check_password_hash(user[1], password):

        # Update login time
        cur.execute(
            """
            UPDATE users
            SET login_timestamp = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (user[0],)
        )

        conn.commit()

        # Remember logged-in user
        session["user_id"] = user[0]

        return redirect("/dashboard")

    return "Invalid username or password"


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

@app.route("/dashboard")
def dashboard():

    # User must be logged in
    if "user_id" not in session:

        return "Please login first"

    return render_template("index.html")


# --------------------------------------------------
# REGISTER PAGE
# --------------------------------------------------

@app.route("/register")
def register_page():

    return render_template("register.html")


# --------------------------------------------------
# REGISTER USER
# --------------------------------------------------

@app.route("/register", methods=["POST"])
def register():

    username = request.form.get("username")
    password = request.form.get("password")

    # Convert password into a secure hash
    password_hash = generate_password_hash(password)

    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO users
        (username, password_hash)
        VALUES (%s, %s)
        """,
        (username, password_hash)
    )

    conn.commit()

    return redirect("/")


# --------------------------------------------------
# CSV UPLOAD
# --------------------------------------------------

@app.route("/upload", methods=["POST"])
def upload():

    # User must be logged in
    if "user_id" not in session:

        return "Please login first"

    # Get the uploaded file
    file = request.files.get("csv_file")

    # Check whether a file was uploaded
    if file is None:

        return "No file uploaded"

    # Check file extension
    if not file.filename.endswith(".csv"):

        return "File type not supported"

    # Read CSV using pandas
    df = pd.read_csv(file)

    # Convert DataFrame into HTML table
    table = df.to_html()

    # Send table to dashboard
    return render_template(
        "index.html",
        data=table
    )


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@app.route("/logout")
def logout():

    # Remove user ID from session
    session.pop("user_id", None)

    return redirect("/")


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000,debug=True)