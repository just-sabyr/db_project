from flask import Flask, jsonify, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# load the variables from the .env file 
load_dotenv()

def create_app():
    app = Flask(__name__)

    # basic database settings (taken from .env or the default values)
    app.config["DB_HOST"] = os.getenv("DB_HOST", "localhost")
    app.config["DB_USER"] = os.getenv("DB_USER", "KATCHAW")
    app.config["DB_PASSWORD"] = os.getenv("DB_PASSWORD", "KATCHAW")
    app.config["DB_NAME"] = os.getenv("DB_NAME", "db_project")

    # helper function to open a connection to MySQL
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
            # just print the error so I can see what went wrong
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

    def get_genres_and_artists():           # helper: load genres and artists for dropdowns in the forms
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
    
    @app.route("/debug/templates")
    def debug_templates():
        folder = os.path.join(os.path.dirname(__file__), "templates")
        try:
            files = os.listdir(folder)
        except FileNotFoundError:
            return f"Templates folder not found at: {folder}"
        return "<br>".join(files)

    # default route; something to show that the API works
    @app.route("/")
    def index():
        return render_template("index.html")
      

    # simple test route
    @app.route("/ping")
    def ping():
        return {"message": "Flask is running!"}

    # route to show some of the genres from the database
    @app.route("/genres")
    def get_genres():
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Cannot connect to database"}), 500

        # using dictionary=True so we get JSON-friendly column names
        cursor = conn.cursor(dictionary=True)

        # just selecting a few rows to test the query
        cursor.execute("SELECT genre_id, parent_genre, genre_name, genre_description FROM Genres;")
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template("genres.html", genres=rows)
    
    # Artists API Route 
    @app.route("/artists")
    def get_artists():
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Cannot connect to database"}), 500

        cursor = conn.cursor(dictionary=True)
        # selecting a few columns just to keep output readable, its just for testing
        cursor.execute("SELECT artist_id, artist_name, country, genre_id, artist_popularity FROM Artists LIMIT 20;")
        rows = cursor.fetchall()

        cursor.close()
        conn.close()
        return render_template("artists.html", artists=rows)


    # Albums API Route 
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
        return render_template ("albums.html", albums = rows)


    # Tracks API Route 
    @app.route("/tracks")
    def get_tracks():
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Cannot connect to database"}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT track_id, track_name, album_id, artist_id, genre_id, duration, explicit,popularity FROM Tracks LIMIT 20;")
        rows = cursor.fetchall()

        cursor.close()
        conn.close()
        return render_template("tracks.html", tracks=rows)


    # Audio Features API Route 
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
    def get_users():
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Cannot connect to database"}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT user_id, username, email, phone_number, dob, genre_id, artist_id
            FROM Users LIMIT 20;
        """)
        rows = cursor.fetchall()

        cursor.close()
        conn.close()
        return render_template("users.html", users=rows)
    
    # Create User
    @app.route("/users/new", methods=["GET", "POST"])
    def create_user():
        if request.method == "POST":
            username = request.form.get("username")
            email = request.form.get("email") or None
            phone_number = request.form.get("phone_number") or None
            dob = request.form.get("dob") or None   # "" -> None
            genre_id = request.form.get("genre_id") or None
            artist_id = request.form.get("artist_id") or None

            conn = get_db_connection()
            if conn is None:
                return jsonify({"error": "Cannot connect to database"}), 500

            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Users (username, email, phone_number, dob, genre_id, artist_id)
                VALUES (%s, %s, %s, %s, %s, %s);
            """, (username, email, phone_number, dob, genre_id, artist_id))
            conn.commit()
            cursor.close()
            conn.close()

            return redirect(url_for("get_users"))

        genres, artists = get_genres_and_artists()
        return render_template("add_user.html", genres=genres, artists=artists)

    # Edit User 
    @app.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
    def edit_user(user_id):
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Cannot connect to database"}), 500

        cursor = conn.cursor(dictionary=True)

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

        cursor.execute("SELECT * FROM Users WHERE user_id = %s;", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user:
            # if user_id doesn't exist, just go back to list
            return redirect(url_for("get_users"))

        if user.get("dob"):
            try:
                user["dob"] = user["dob"].strftime("%Y-%m-%d")
            except AttributeError:
                # if it's already a string, ignore
                pass

        genres, artists = get_genres_and_artists()
        return render_template("edit_user.html", user=user, genres=genres, artists=artists)

    # Delete User 
    @app.route("/users/<int:user_id>/delete", methods=["POST"])
    def delete_user(user_id):
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Cannot connect to database"}), 500

        cursor = conn.cursor()
        cursor.execute("DELETE FROM Users WHERE user_id = %s;", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for("get_users"))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
