from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from supabase import create_client, Client
import os

app = Flask(__name__)
app.secret_key = "your-secret-key"  # replace with a strong key

# Supabase setup
SUPABASE_URL = "https://zqmotxqejqnjhtdjxbik.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpxbW90eHFlanFuamh0ZGp4YmlrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU2ODQ4ODIsImV4cCI6MjA3MTI2MDg4Mn0.2sYGb7X0uDAihr8xyDzHOJFEdAX-zeDa-LJ81VhYSJs"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.route("/")
def index():
    if "user" not in session:
        return redirect(url_for("login"))

    songs = supabase.table("songs").select("*").order("id", desc=True).execute()
    return render_template("index.html", songs=songs.data)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        auth = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if auth.user:
            session["user"] = auth.user.email
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Invalid login")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        auth = supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        if auth.user:
            session["user"] = auth.user.email
            return redirect(url_for("index"))
        else:
            return render_template("signup.html", error="Signup failed")

    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form["title"]
        artist = request.form["artist"]
        file = request.files["file"]
        cover = request.files["cover"]

        # Upload song
        song_path = f"songs/{file.filename}"
        supabase.storage.from_("music").upload(song_path, file.read())

        # Upload cover
        cover_path = f"covers/{cover.filename}"
        supabase.storage.from_("music").upload(cover_path, cover.read())

        # Insert into DB
        supabase.table("songs").insert({
            "title": title,
            "artist": artist,
            "song_url": f"{SUPABASE_URL}/storage/v1/object/public/music/{song_path}",
            "cover_url": f"{SUPABASE_URL}/storage/v1/object/public/music/{cover_path}"
        }).execute()

        return redirect(url_for("index"))

    return render_template("upload.html")


@app.route("/player/<int:song_id>")
def player(song_id):
    song = supabase.table("songs").select("*").eq("id", song_id).single().execute()
    return render_template("player.html", song=song.data)


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("q", "")
    if query:
        songs = supabase.table("songs").select("*").ilike("title", f"%{query}%").execute()
    else:
        songs = {"data": []}
    return render_template("search.html", songs=songs["data"], query=query)


if __name__ == "__main__":
    app.run(debug=True)
