# /home/shallarr/Projects/music/app.py
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersecretkey"

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
            filename TEXT NOT NULL,
            cover TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()


@app.route("/")
def index():
    conn = get_db()
    songs = conn.execute("SELECT * FROM songs").fetchall()
    conn.close()
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


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "user" not in session or session["user"] != "adrimarsh898@gmail.com":
        flash("You are not allowed to upload music.")
        return redirect(url_for("index"))

    if request.method == "POST":
        title = request.form["title"]
        artist = request.form["artist"]
        file = request.files["file"]
        cover = request.files["cover"]

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            cover_filename = None
            if cover:
                cover_filename = secure_filename(cover.filename)
                cover.save(os.path.join(app.config["COVER_FOLDER"], cover_filename))

            conn = get_db()
            conn.execute("INSERT INTO songs (title, artist, filename, cover) VALUES (?, ?, ?, ?)",
                         (title, artist, filename, cover_filename))
            conn.commit()
            conn.close()
            flash("Song uploaded successfully!")
            return redirect(url_for("index"))

    return render_template("upload.html")


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
