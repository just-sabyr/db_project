from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from functools import wraps

# import blueprints
from code_files.genres import genres_bp
from code_files.artists import artists_bp
from code_files.albums import albums_bp
from code_files.tracks import tracks_bp
from code_files.audiofeatures import audiofeatures_bp
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
    @login_required
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
                session["role"] = "admin"
                session["username"] = "admin"
                return redirect(url_for("index"))
            else:
                error = "Invalid credentials. Please try again."

        return render_template("login.html", error=error)

    @app.route("/logout")
    def logout():
        session.clear()
        flash("You have been logged out successfully.", "info")
        return redirect(url_for("index"))
    

        #  Chosse table pags for navbar Add/Edit
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
