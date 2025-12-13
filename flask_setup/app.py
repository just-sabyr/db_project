from flask import Flask, jsonify, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# load the variables from the .env file 
load_dotenv()


def create_app():
    app = Flask(__name__)

    # secret key for login and logout
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-me")

    # basic database settings (taken from .env or the default values)
    app.config["DB_HOST"] = os.getenv("DB_HOST", "localhost")
    app.config["DB_USER"] = os.getenv("DB_USER", "KATCHAW")
    app.config["DB_PASSWORD"] = os.getenv("DB_PASSWORD", "KATCHAW")
    app.config["DB_NAME"] = os.getenv("DB_NAME", "db_project")

    def get_db_connection():
        try:
            conn = mysql.connector.connect(
                host=app.config["DB_HOST"],
                user=app.config["DB_USER"],
                password=app.config["DB_PASSWORD"],
                database=app.config["DB_NAME"]
            )
            return conn
        except Error as e:
            print("MySQL error:", e)
            return None

    def execute_safe_query(query, params=None):
        try:
            conn = get_db_connection()
            if conn is None:
                return False, "Database connection failed"

            cursor = conn.cursor()
            cursor.execute(query, params or ())
            conn.commit()

            cursor.close()
            conn.close()
            return True, None

        except mysql.connector.Error as e:
            return False, f"MySQL Error: {e}"

    def get_genres_and_artists():
        conn = get_db_connection()
        if conn is None:
            return [], []

        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT genre_id, genre_name FROM Genres ORDER BY genre_name;")
        genres = cursor.fetchall()

        cursor.execute("SELECT artist_id, artist_name FROM Artists ORDER BY artist_name;")
        artists = cursor.fetchall()

        cursor.close()
        conn.close()

        return genres, artists

    def login_required(view_func):
        def wrapped(*args, **kwargs):
            if not session.get("logged_in"):
                return redirect(url_for("login"))
            return view_func(*args, **kwargs)

        wrapped.__name__ = view_func.__name__
        return wrapped

    @app.route("/debug/templates")
    def debug_templates():
        folder = os.path.join(os.path.dirname(__file__), "templates")
        try:
            files = os.listdir(folder)
        except FileNotFoundError:
            return f"Templates folder not found at: {folder}"
        return "<br>".join(files)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/ping")
    def ping():
        return {"message": "Flask is running!"}

    @app.route("/genres")
    def get_genres():
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Cannot connect to database"}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT genre_id, parent_genre, genre_name, genre_description FROM Genres;")
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template("genres.html", genres=rows)

    @app.route("/artists")
    def get_artists():
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Cannot connect to database"}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT artist_id, artist_name, country, genre_id, artist_popularity FROM Artists LIMIT 20;")
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template("artists.html", artists=rows)

    @app.route("/albums")
    def get_albums():
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Cannot connect to database"}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT album_id, album_name, release_year, artist_id, genre_id, cover_url FROM Albums LIMIT 20;")
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template("albums.html", albums=rows)

    @app.route("/tracks")
    def get_tracks():
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Cannot connect to database"}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT track_id, track_name, album_id, artist_id, genre_id, duration, explicit, popularity
            FROM Tracks LIMIT 20;
        """)
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template("tracks.html", tracks=rows)

    @app.route("/audiofeatures")
    def get_audio_features():
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Cannot connect to database"}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT feature_id, track_id, danceability, energy, valence, tempo, loudness, acousticness
            FROM AudioFeatures LIMIT 20;
        """)
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template("audiofeatures.html", features=rows)

     # Users API Route

    @app.route("/users")
    @login_required
    def get_users():
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Cannot connect to database"}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT user_id, username, email, phone_number, dob, genre_id, artist_id
            FROM Users LIMIT 50;
        """)
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template("users.html", users=rows)

    @app.route("/users/new", methods=["GET", "POST"])
    @login_required
    def create_user():
        if request.method == "POST":
            username = request.form.get("username")
            email = request.form.get("email") or None
            phone_number = request.form.get("phone_number") or None
            dob = request.form.get("dob") or None
            genre_id = request.form.get("genre_id") or None
            artist_id = request.form.get("artist_id") or None

            query = """
                INSERT INTO Users (username, email, phone_number, dob, genre_id, artist_id)
                VALUES (%s, %s, %s, %s, %s, %s);
            """
            params = (username, email, phone_number, dob, genre_id, artist_id)

            success, error = execute_safe_query(query, params)
            if not success:
                genres, artists = get_genres_and_artists()
                return render_template("add_user.html", genres=genres, artists=artists, error_message=error)

            return redirect(url_for("get_users"))

        genres, artists = get_genres_and_artists()
        return render_template("add_user.html", genres=genres, artists=artists)

    @app.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
    @login_required
    def edit_user(user_id):
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Cannot connect to database"}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users WHERE user_id = %s;", (user_id,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if not user:
            return redirect(url_for("get_users"))

        # format DOB for input type="date"
        if user.get("dob"):
            try:
                user["dob"] = user["dob"].strftime("%Y-%m-%d")
            except AttributeError:
                pass

        if request.method == "POST":
            username = request.form.get("username")
            email = request.form.get("email") or None
            phone_number = request.form.get("phone_number") or None
            dob = request.form.get("dob") or None
            genre_id = request.form.get("genre_id") or None
            artist_id = request.form.get("artist_id") or None

            query = """
                UPDATE Users
                SET username = %s,
                    email = %s,
                    phone_number = %s,
                    dob = %s,
                    genre_id = %s,
                    artist_id = %s
                WHERE user_id = %s;
            """
            params = (username, email, phone_number, dob, genre_id, artist_id, user_id)

            success, error = execute_safe_query(query, params)
            if not success:
                genres, artists = get_genres_and_artists()
                return render_template(
                    "edit_user.html",
                    user=user,
                    genres=genres,
                    artists=artists,
                    error_message=error
                )

            return redirect(url_for("get_users"))

        genres, artists = get_genres_and_artists()
        return render_template("edit_user.html", user=user, genres=genres, artists=artists)

    @app.route("/users/<int:user_id>/delete", methods=["POST"])
    @login_required
    def delete_user(user_id):
        query = "DELETE FROM Users WHERE user_id = %s;"
        success, error = execute_safe_query(query, (user_id,))

        if not success:
            return jsonify({"error": error}), 500

        return redirect(url_for("get_users"))


    @app.route("/stats")
    @login_required
    def stats_page():
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Cannot connect to database"}), 500

        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) AS total FROM Users;")
        total_users = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM Artists;")
        total_artists = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM Albums;")
        total_albums = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM Tracks;")
        total_tracks = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM Genres;")
        total_genres = cursor.fetchone()["total"]
        # decides the  most popular genre by users 
        cursor.execute("""
            SELECT g.genre_name, COUNT(*) AS total
            FROM Users u
            JOIN Genres g ON u.genre_id = g.genre_id
            GROUP BY g.genre_id, g.genre_name
            ORDER BY total DESC
            LIMIT 1;
        """)
        popular_genre = cursor.fetchone()
        # most popular artist by users 
        cursor.execute("""
            SELECT a.artist_name, COUNT(*) AS total
            FROM Users u
            JOIN Artists a ON u.artist_id = a.artist_id
            GROUP BY a.artist_id, a.artist_name
            ORDER BY total DESC
            LIMIT 1;
        """)
        popular_artist = cursor.fetchone()
         # users by genre 
        cursor.execute("""
            SELECT g.genre_name, COUNT(*) AS total
            FROM Users u
            JOIN Genres g ON u.genre_id = g.genre_id
            GROUP BY g.genre_id, g.genre_name
            ORDER BY total DESC;
        """)
        users_by_genre = cursor.fetchall()
         # most recent added users 
        cursor.execute("""
            SELECT user_id, username, email
            FROM Users
            ORDER BY user_id DESC
            LIMIT 5;
        """)
        recent_users = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template(
            "stats.html",
            total_users=total_users,
            total_artists=total_artists,
            total_albums=total_albums,
            total_tracks=total_tracks,
            total_genres=total_genres,
            popular_genre=popular_genre,
            popular_artist=popular_artist,
            users_by_genre=users_by_genre,
            recent_users=recent_users,
        )

    # Login and logout 

    @app.route("/login", methods=["GET", "POST"])
    def login():
        error = None

        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "").strip()

            admin_user = os.getenv("ADMIN_USER", "admin")
            admin_password = os.getenv("ADMIN_PASSWORD", "admin123")

            if username == admin_user and password == admin_password:
                session["logged_in"] = True
                session["username"] = username
                return redirect(url_for("get_users"))
            else:
                error = "Wrong username or password."

        return render_template("login.html", error=error)

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
