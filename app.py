# /home/shallarr/Projects/music/app.py
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from supabase import create_client, Client


app = Flask(__name__)
app.secret_key = "supersecretkey"

SUPABASE_URL = "https://zqmotxqejqnjhtdjxbik.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpxbW90eHFlanFuamh0ZGp4YmlrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTY4NDg4MiwiZXhwIjoyMDcxMjYwODgyfQ.t8ZUJRkbSa6g0h7e8wIZGXCoK_nR1_mZ7iLXXE4_7HQ"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

UPLOAD_FOLDER = "uploads"
COVER_FOLDER = "uploads/covers"
DB_FILE = "music.db"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COVER_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["COVER_FOLDER"] = COVER_FOLDER


def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


# Initialize DB
def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            audio_url TEXT NOT NULL,
            cover_url TEXT
        )

    """)
    conn.commit()
    conn.close()

init_db()


@app.route("/")
def index():
    songs, error = supabase.table("songs").select("*").order("id", desc=True).execute()
    if error:
        songs = []
    else:
        songs = songs.data

    return render_template("index.html", songs=songs)

@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("q", "")
    conn = get_db()
    songs = conn.execute("SELECT * FROM songs WHERE title LIKE ? OR artist LIKE ?",
                         (f"%{query}%", f"%{query}%")).fetchall()
    conn.close()
    return render_template("search.html", songs=songs, query=query)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user"] = user["email"]
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials")
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = generate_password_hash(request.form["password"], method="pbkdf2:sha256")

        try:
            conn = get_db()
            conn.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
            conn.commit()
            conn.close()
            flash("Signup successful, please login.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Email already exists")
    return render_template("signup.html")


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not session.get('user') or session['user'] != 'adrimarsh898@gmail.com':
        flash("You must be logged in as admin to upload.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        artist = request.form['artist']
        audio_file = request.files['file']
        cover_file = request.files['cover']

        if not audio_file or not cover_file:
            flash("Both audio and cover files are required.")
            return redirect('/upload')

        try:
            # --- Upload audio ---
            audio_path = f"audio/{secure_filename(audio_file.filename)}"
            supabase.storage.from_("songs").upload(audio_path, audio_file.read())
            audio_url = supabase.storage.from_("songs").get_public_url(audio_path)

            # --- Upload cover ---
            cover_path = f"covers/{secure_filename(cover_file.filename)}"
            supabase.storage.from_("songs").upload(cover_path, cover_file.read())
            cover_url = supabase.storage.from_("songs").get_public_url(cover_path)
            
            # Save metadata in songs table
            supabase.table("songs").insert({
                "title": title,
                "artist": artist,
                "song_url": audio_url,
                "cover_url": cover_url
            }).execute()

            # --- Save in SQLite DB ---
            conn = get_db()
            conn.execute(
                "INSERT INTO songs (title, artist, audio_url, cover_url) VALUES (?, ?, ?, ?)",
                (title, artist, audio_url, cover_url)
            )
            conn.commit()
            conn.close()

            flash('Song uploaded successfully!', 'success')
            return redirect('/upload')

        except Exception as e:
            flash(f'Upload failed: {e}', 'danger')
            return redirect('/upload')

    return render_template('upload.html')

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/covers/<path:filename>")
def cover_file(filename):
    return send_from_directory(app.config["COVER_FOLDER"], filename)


# ✅ NEW: Full Player Route
@app.route("/player")
def player():
    song_id = request.args.get("id")
    if not song_id:
        flash("No song selected")
        return redirect(url_for("index"))

    conn = get_db()
    song = conn.execute("SELECT * FROM songs WHERE id=?", (song_id,)).fetchone()
    conn.close()

    if not song:
        flash("Song not found")
        return redirect(url_for("index"))

    return render_template("player.html", song=song)


if __name__ == "__main__":
    app.run(debug=True)
