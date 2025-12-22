from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash

# import blueprints
from code_files.genres import genres_bp
from code_files.artists import artists_bp
from code_files.albums import albums_bp
from code_files.tracks import tracks_bp
from code_files.audiofeatures import audiofeatures_bp
from code_files.favorites import favorites_bp
from code_files.users import users_bp
from code_files.shared import get_db_connection, login_required, role_required


# load the variables from the .env file 
load_dotenv()


def create_app():
    app = Flask(__name__)

    # secret key for login and logout
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-me")

    # basic database settings (taken from .env or the default values)
    app.config["DB_HOST"] = os.getenv("DB_HOST", "localhost")
    app.config["DB_USER"] = os.getenv("DB_USER", "superuser")
    app.config["DB_PASSWORD"] = os.getenv("DB_PASSWORD", "123")
    app.config["DB_NAME"] = os.getenv("DB_NAME", "db_project")

    # Register blueprints
    app.register_blueprint(genres_bp, url_prefix='/genres')
    app.register_blueprint(artists_bp, url_prefix='/artists')
    app.register_blueprint(albums_bp, url_prefix='/albums')
    app.register_blueprint(tracks_bp, url_prefix='/tracks')
    app.register_blueprint(audiofeatures_bp, url_prefix='/audiofeatures')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(favorites_bp, url_prefix='/favorites')  


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

    @app.route("/stats")
    @role_required("admin")
    def stats_page():
        conn = get_db_connection()
        if conn is None:
            return

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


    @app.route("/album-audio-stats")
    def album_audio_stats():
        conn = get_db_connection()
        if conn is None:
            flash("Database connection failed.", "error")
            return redirect(url_for("index"))

        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                a.album_name,
                COUNT(t.track_id) AS track_count,
                AVG(af.energy) AS avg_energy,
                AVG(af.danceability) AS avg_danceability,
                AVG(af.valence) AS avg_valence
            FROM Albums a
            JOIN Tracks t ON a.album_id = t.album_id
            LEFT JOIN AudioFeatures af ON t.track_id = af.track_id
            GROUP BY a.album_id, a.album_name
            ORDER BY avg_energy DESC;
        """)

        results = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template("album_audio_stats.html", results=results)
   
        @app.route("/artists-stats")
        @role_required("admin")
        def artists_stats():
            conn = get_db_connection()
        if conn is None:
            flash("Database connection failed.", "error")
            return redirect(url_for("index"))

        cursor = conn.cursor(dictionary=True)

        # total artists
        cursor.execute("SELECT COUNT(*) AS total FROM Artists;")
        total_artists = cursor.fetchone()["total"]

        # average popularity
        cursor.execute("SELECT AVG(artist_popularity) AS avg_popularity FROM Artists;")
        avg_popularity = cursor.fetchone()["avg_popularity"]

        # most popular artist
        cursor.execute("""
            SELECT artist_name, artist_popularity
            FROM Artists
            ORDER BY artist_popularity DESC
            LIMIT 1;
        """)
        top_artist = cursor.fetchone()

        # artists by country (COMPLEX QUERY)
        cursor.execute("""
            SELECT country, COUNT(*) AS total
            FROM Artists
            GROUP BY country
            ORDER BY total DESC;
        """)
        artists_by_country = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template(
            "artists_stats.html",
            total_artists=total_artists,
            avg_popularity=avg_popularity,
            top_artist=top_artist,
            artists_by_country=artists_by_country
        )

    @app.route("/most-energetic-albums")
    def most_energetic_albums():
        conn = get_db_connection()
        if conn is None:
            flash("Database connection failed.", "error")
            return redirect(url_for("index"))
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT
            a.album_name,
            AVG(af.energy) AS avg_energy
            FROM Albums a
            JOIN Tracks t ON a.album_id = t.album_id
            JOIN AudioFeatures af ON t.track_id = af.track_id
            GROUP BY a.album_id, a.album_name
            HAVING AVG(af.energy) > 0.7
            ORDER BY avg_energy DESC;
        """)

        results = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template("most_energetic_albums.html", results=results)

    
    
    @app.route("/login", methods=["GET", "POST"])
    def login():
        error = None

        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "").strip()

            # Check for admin first
            admin_user = os.getenv("ADMIN_USER", "admin")
            admin_password = os.getenv("ADMIN_PASSWORD", "admin123")

            if username == admin_user and password == admin_password:
                session["logged_in"] = True
                session["role"] = "admin"
                session["username"] = "admin"
                session["user_id"] = None
                flash("Welcome, Admin!", "success")
                return redirect(url_for("index"))

            # Check database for regular users
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(
                    "SELECT user_id, username, password_hash FROM Users WHERE username = %s",
                    (username,)
                )
                user = cursor.fetchone()
                cursor.close()
                conn.close()

                if user and check_password_hash(user["password_hash"], password):
                    session["logged_in"] = True
                    session["role"] = "user"
                    session["username"] = user["username"]
                    session["user_id"] = user["user_id"]
                    flash(f"Welcome back, {user['username']}!", "success")
                    return redirect(url_for("index"))

            error = "Invalid credentials. Please try again."

        return render_template("login.html", error=error)
    
    @app.route("/logout")
    def logout():
        session.clear()
        flash("You have been logged out successfully.", "info")
        return redirect(url_for("index"))


    @app.route("/profile", methods=["GET", "POST"])
    @login_required
    def profile():
        # Admin doesn't have a database profile
        if session.get("role") == "admin":
            flash("Admin account cannot be edited here.", "warning")
            return redirect(url_for("index"))

        user_id = session.get("user_id")
        conn = get_db_connection()
        if conn is None:
            flash("Database connection failed.", "error")
            return redirect(url_for("index"))

        cursor = conn.cursor(dictionary=True)

        # Get genres for dropdown (small table, ok to fetch all)
        cursor.execute("SELECT genre_id, genre_name FROM Genres ORDER BY genre_name;")
        genres = cursor.fetchall()
        # Removed: artists query - now using search autocomplete instead

        if request.method == "POST":
            new_username = request.form.get("username", "").strip()
            new_email = request.form.get("email", "").strip() or None
            new_phone = request.form.get("phone_number", "").strip() or None
            new_dob = request.form.get("dob", "").strip() or None
            new_password = request.form.get("password", "").strip()
            new_genre_id = request.form.get("genre_id") or None
            new_artist_id = request.form.get("artist_id") or None

            # Validation
            errors = []
            if not new_username:
                errors.append("Username cannot be empty.")
            if len(new_username) > 50:
                errors.append("Username must be 50 characters or less.")
            if new_phone and len(new_phone) > 13:
                errors.append("Phone number must be 13 characters or less.")
            if new_password and len(new_password) < 3:
                errors.append("Password must be at least 3 characters.")

            if errors:
                for error in errors:
                    flash(error, "error")
            else:
                try:
                    # Build dynamic update query
                    update_fields = []
                    params = []

                    update_fields.append("username = %s")
                    params.append(new_username)

                    update_fields.append("email = %s")
                    params.append(new_email)

                    update_fields.append("phone_number = %s")
                    params.append(new_phone)

                    update_fields.append("dob = %s")
                    params.append(new_dob)

                    update_fields.append("genre_id = %s")
                    params.append(new_genre_id)

                    update_fields.append("artist_id = %s")
                    params.append(new_artist_id)

                    # Only update password if provided
                    if new_password:
                        hashed_password = generate_password_hash(new_password)
                        update_fields.append("password_hash = %s")
                        params.append(hashed_password)

                    params.append(user_id)

                    query = f"UPDATE Users SET {', '.join(update_fields)} WHERE user_id = %s"
                    cursor.execute(query, tuple(params))
                    conn.commit()

                    session["username"] = new_username  # Update session
                    flash("Profile updated successfully!", "success")

                except mysql.connector.IntegrityError as e:
                    if "username" in str(e).lower():
                        flash("That username is already taken.", "error")
                    elif "email" in str(e).lower() or "chk_users_email" in str(e).lower():
                        flash("Invalid email format.", "error")
                    else:
                        flash(f"Update failed: {e}", "error")

        # Fetch current user data
        cursor.execute(
            """SELECT user_id, username, email, phone_number, dob, genre_id, artist_id 
               FROM Users WHERE user_id = %s""",
            (user_id,)
        )
        user = cursor.fetchone()

        # Get current artist name for display in search input
        current_artist_name = None
        if user and user.get("artist_id"):
            cursor.execute(
                "SELECT artist_name FROM Artists WHERE artist_id = %s",
                (user["artist_id"],)
            )
            artist = cursor.fetchone()
            if artist:
                current_artist_name = artist["artist_name"]

        cursor.close()
        conn.close()

        return render_template("profile.html", user=user, genres=genres, current_artist_name=current_artist_name)
    
    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            if not username or not password:
                return render_template("signup.html", error="Username and password are required")

            conn = get_db_connection()
            if conn is None:
                return render_template("signup.html", error="Database connection failed")
            cursor = conn.cursor()

        # check if user exists
            cursor.execute(
                "SELECT user_id FROM Users WHERE username = %s",
                (username,)
            )
            existing_user = cursor.fetchone()

            if existing_user:
                cursor.close()
                conn.close()
                return render_template("signup.html", error="Username already exists")

      
            cursor.execute(
                "INSERT INTO Users (username, password_hash) VALUES (%s, %s)",
                (username, generate_password_hash(password))
            )

            conn.commit()

            cursor.close()
            conn.close()
            return redirect(url_for("login"))

        return render_template("signup.html")


    #  Choose table pages for navbar Add/Edit
    @app.route("/choose/add")
    @role_required("admin")
    def choose_add():
        tables = [
            {"label": "Genres", "url": url_for("genres.create_genre")},
            {"label": "Artists", "url": url_for("artists.create_artist")},
            {"label": "Albums", "url": url_for("albums.create_album")},
            {"label": "Tracks", "url": url_for("tracks.create_track")},
            {"label": "Audio Features", "url": url_for("audiofeatures.create_audiofeatures")},
            {"label": "Users", "url": url_for("users.create_user")},
        ]
        return render_template(
            "choose_table.html",
            title="Add record",
            subtitle="Choose which table you want to add a new record to:",
            tables=tables,
            hint="After you open the table list, click the Add button on the row you want."
        )

    @app.route("/choose/edit")
    @role_required("admin")
    def choose_edit():
        tables = [
            {"label": "Genres", "url": url_for("genres.get_genres")},
            {"label": "Artists", "url": url_for("artists.get_artists")},
            {"label": "Albums", "url": url_for("albums.get_albums")},
            {"label": "Tracks", "url": url_for("tracks.get_tracks")},
            {"label": "Audio Features", "url": url_for("audiofeatures.get_audio_features")},
            {"label": "Users", "url": url_for("users.get_users")},
        ]
        return render_template(
            "choose_table.html",
            title="Edit record",
            subtitle="Choose a table, then click Edit on the row you want to update:",
            tables=tables,
            hint="After you open the table list, click the Edit button on the row you want."
        )    

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
