from flask import Flask, jsonify, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
from functools import wraps

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
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not session.get("logged_in"):
                return redirect(url_for("login"))
            return view_func(*args, **kwargs)

        return wrapped

    # Role-based access decorator 
    def role_required(*roles):
        def decorator(view_func):
            @wraps(view_func)
            def wrapped(*args, **kwargs):
                if not session.get("logged_in"):
                    return redirect(url_for("login"))

                user_role = session.get("role")
                if user_role not in roles:
                    return "Forbidden: you don't have permission for this page.", 403

                return view_func(*args, **kwargs)
            return wrapped
        return decorator

    # helpers for unified templates 
    def build_user_fields(genres, artists):
        return [
            {"name": "username", "label": "Username", "type": "text"},
            {"name": "email", "label": "Email", "type": "text"},
            {"name": "phone_number", "label": "Phone Number", "type": "text"},
            {"name": "dob", "label": "Date of Birth", "type": "date"},
            {
                "name": "genre_id", "label": "Favorite Genre", "type": "select",
                "options": [{"value": g["genre_id"], "text": g["genre_name"]} for g in genres]
            },
            {
                "name": "artist_id", "label": "Favorite Artist", "type": "select",
                "options": [{"value": a["artist_id"], "text": a["artist_name"]} for a in artists]
            },
        ]

    def user_edit_url(row):
        return url_for("edit_user", user_id=row["user_id"])

    def user_delete_url(row):
        return url_for("delete_user", user_id=row["user_id"])

    # ADDED: CRUD helpers for other tables 
    def is_admin():
        return session.get("logged_in") and session.get("role") == "admin"

    def get_albums_list():
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT album_id, album_name FROM Albums ORDER BY album_name;")
        albums = cursor.fetchall()
        cursor.close()
        conn.close()
        return albums

    def get_tracks_list():
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT track_id, track_name FROM Tracks ORDER BY track_name;")
        tracks = cursor.fetchall()
        cursor.close()
        conn.close()
        return tracks

    def build_genre_fields():
        return [
            {"name": "parent_genre", "label": "Parent Genre", "type": "text"},
            {"name": "genre_name", "label": "Genre Name", "type": "text"},
            {"name": "genre_description", "label": "Genre Description", "type": "text"},
        ]

    def build_artist_fields(genres):
        return [
            {"name": "artist_name", "label": "Artist Name", "type": "text"},
            {"name": "country", "label": "Country", "type": "text"},
            {
                "name": "genre_id", "label": "Genre", "type": "select",
                "options": [{"value": g["genre_id"], "text": g["genre_name"]} for g in genres]
            },
            {"name": "artist_popularity", "label": "Artist Popularity", "type": "text"},
        ]

    def build_album_fields(genres, artists):
        return [
            {"name": "album_name", "label": "Album Name", "type": "text"},
            {"name": "release_year", "label": "Release Year", "type": "text"},
            {
                "name": "artist_id", "label": "Artist", "type": "select",
                "options": [{"value": a["artist_id"], "text": a["artist_name"]} for a in artists]
            },
            {
                "name": "genre_id", "label": "Genre", "type": "select",
                "options": [{"value": g["genre_id"], "text": g["genre_name"]} for g in genres]
            },
            {"name": "cover_url", "label": "Cover URL", "type": "text"},
        ]

    def build_track_fields(genres, artists, albums):
        return [
            {"name": "track_name", "label": "Track Name", "type": "text"},
            {
                "name": "album_id", "label": "Album", "type": "select",
                "options": [{"value": al["album_id"], "text": al["album_name"]} for al in albums]
            },
            {
                "name": "artist_id", "label": "Artist", "type": "select",
                "options": [{"value": a["artist_id"], "text": a["artist_name"]} for a in artists]
            },
            {
                "name": "genre_id", "label": "Genre", "type": "select",
                "options": [{"value": g["genre_id"], "text": g["genre_name"]} for g in genres]
            },
            {"name": "duration", "label": "Duration", "type": "text"},
            {"name": "explicit", "label": "Explicit (0/1)", "type": "text"},
            {"name": "popularity", "label": "Popularity", "type": "text"},
        ]

    def build_audiofeatures_fields(tracks):
        return [
            {
                "name": "track_id", "label": "Track", "type": "select",
                "options": [{"value": t["track_id"], "text": t["track_name"]} for t in tracks]
            },
            {"name": "danceability", "label": "Danceability", "type": "text"},
            {"name": "energy", "label": "Energy", "type": "text"},
            {"name": "valence", "label": "Valence", "type": "text"},
            {"name": "tempo", "label": "Tempo", "type": "text"},
            {"name": "loudness", "label": "Loudness", "type": "text"},
            {"name": "acousticness", "label": "Acousticness", "type": "text"},
        ]

    def genre_edit_url(row):
        return url_for("edit_genre", genre_id=row["genre_id"])

    def genre_delete_url(row):
        return url_for("delete_genre", genre_id=row["genre_id"])

    def artist_edit_url(row):
        return url_for("edit_artist", artist_id=row["artist_id"])

    def artist_delete_url(row):
        return url_for("delete_artist", artist_id=row["artist_id"])

    def album_edit_url(row):
        return url_for("edit_album", album_id=row["album_id"])

    def album_delete_url(row):
        return url_for("delete_album", album_id=row["album_id"])

    def track_edit_url(row):
        return url_for("edit_track", track_id=row["track_id"])

    def track_delete_url(row):
        return url_for("delete_track", track_id=row["track_id"])

    def audiofeatures_edit_url(row):
        return url_for("edit_audiofeatures", feature_id=row["feature_id"])

    def audiofeatures_delete_url(row):
        return url_for("delete_audiofeatures", feature_id=row["feature_id"])

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

        return render_template(
            "list.html",
            title="Genres",
            subtitle="Browse genres from the database",
            columns=["genre_id", "parent_genre", "genre_name", "genre_description"],
            keys=["genre_id", "parent_genre", "genre_name", "genre_description"],
            rows=rows,
            show_actions=is_admin(),
            add_url=(url_for("create_genre") if is_admin() else None),
            edit_url_builder=(genre_edit_url if is_admin() else None),
            delete_url_builder=(genre_delete_url if is_admin() else None),
            description=None
        )

    # ADDED: Genres CRUD
    @app.route("/genres/new", methods=["GET", "POST"])
    @role_required("admin")
    def create_genre():
        fields = build_genre_fields()

        if request.method == "POST":
            parent_genre = request.form.get("parent_genre") or None
            genre_name = request.form.get("genre_name")
            genre_description = request.form.get("genre_description") or None

            query = """
                INSERT INTO Genres (parent_genre, genre_name, genre_description)
                VALUES (%s, %s, %s);
            """
            params = (parent_genre, genre_name, genre_description)

            success, error = execute_safe_query(query, params)
            if not success:
                return render_template(
                    "add.html",
                    title="Genre",
                    subtitle="Create a new genre record",
                    fields=fields,
                    cancel_url=url_for("get_genres"),
                    error_message=error
                )

            return redirect(url_for("get_genres"))

        return render_template(
            "add.html",
            title="Genre",
            subtitle="Create a new genre record",
            fields=fields,
            cancel_url=url_for("get_genres"),
            error_message=None
        )

    @app.route("/genres/<int:genre_id>/edit", methods=["GET", "POST"])
    @role_required("admin")
    def edit_genre(genre_id):
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Cannot connect to database"}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Genres WHERE genre_id = %s;", (genre_id,))
        genre = cursor.fetchone()

        cursor.close()
        conn.close()

        if not genre:
            return redirect(url_for("get_genres"))

        fields = build_genre_fields()

        if request.method == "POST":
            parent_genre = request.form.get("parent_genre") or None
            genre_name = request.form.get("genre_name")
            genre_description = request.form.get("genre_description") or None

            query = """
                UPDATE Genres
                SET parent_genre = %s,
                    genre_name = %s,
                    genre_description = %s
                WHERE genre_id = %s;
            """
            params = (parent_genre, genre_name, genre_description, genre_id)

            success, error = execute_safe_query(query, params)
            if not success:
                return render_template(
                    "edit.html",
                    title="Genre",
                    subtitle=f"Editing genre_id = {genre_id}",
                    fields=fields,
                    values={
                        **genre,
                        "parent_genre": parent_genre,
                        "genre_name": genre_name,
                        "genre_description": genre_description,
                    },
                    cancel_url=url_for("get_genres"),
                    error_message=error
                )

            return redirect(url_for("get_genres"))

        return render_template(
            "edit.html",
            title="Genre",
            subtitle=f"Editing genre_id = {genre_id}",
            fields=fields,
            values=genre,
            cancel_url=url_for("get_genres"),
            error_message=None
        )

    @app.route("/genres/<int:genre_id>/delete", methods=["POST"])
    @role_required("admin")
    def delete_genre(genre_id):
        query = "DELETE FROM Genres WHERE genre_id = %s;"
        success, error = execute_safe_query(query, (genre_id,))

        if not success:
            return jsonify({"error": error}), 500

        return redirect(url_for("get_genres"))

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

        return render_template(
            "list.html",
            title="Artists",
            subtitle="Browse artists from the database",
            columns=["artist_id", "artist_name", "country", "genre_id", "artist_popularity"],
            keys=["artist_id", "artist_name", "country", "genre_id", "artist_popularity"],
            rows=rows,
            show_actions=is_admin(),
            add_url=(url_for("create_artist") if is_admin() else None),
            edit_url_builder=(artist_edit_url if is_admin() else None),
            delete_url_builder=(artist_delete_url if is_admin() else None),
            description=None
        )

    # ADDED: Artists CRUD 
    @app.route("/artists/new", methods=["GET", "POST"])
    @role_required("admin")
    def create_artist():
        genres, _artists = get_genres_and_artists()
        fields = build_artist_fields(genres)

        if request.method == "POST":
            artist_name = request.form.get("artist_name")
            country = request.form.get("country") or None
            genre_id = request.form.get("genre_id") or None
            artist_popularity = request.form.get("artist_popularity") or None

            query = """
                INSERT INTO Artists (artist_name, country, genre_id, artist_popularity)
                VALUES (%s, %s, %s, %s);
            """
            params = (artist_name, country, genre_id, artist_popularity)

            success, error = execute_safe_query(query, params)
            if not success:
                return render_template(
                    "add.html",
                    title="Artist",
                    subtitle="Create a new artist record",
                    fields=fields,
                    cancel_url=url_for("get_artists"),
                    error_message=error
                )

            return redirect(url_for("get_artists"))

        return render_template(
            "add.html",
            title="Artist",
            subtitle="Create a new artist record",
            fields=fields,
            cancel_url=url_for("get_artists"),
            error_message=None
        )

    @app.route("/artists/<int:artist_id>/edit", methods=["GET", "POST"])
    @role_required("admin")
    def edit_artist(artist_id):
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Cannot connect to database"}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Artists WHERE artist_id = %s;", (artist_id,))
        artist = cursor.fetchone()

        cursor.close()
        conn.close()

        if not artist:
            return redirect(url_for("get_artists"))

        genres, _artists = get_genres_and_artists()
        fields = build_artist_fields(genres)

        if request.method == "POST":
            artist_name = request.form.get("artist_name")
            country = request.form.get("country") or None
            genre_id = request.form.get("genre_id") or None
            artist_popularity = request.form.get("artist_popularity") or None

            query = """
                UPDATE Artists
                SET artist_name = %s,
                    country = %s,
                    genre_id = %s,
                    artist_popularity = %s
                WHERE artist_id = %s;
            """
            params = (artist_name, country, genre_id, artist_popularity, artist_id)

            success, error = execute_safe_query(query, params)
            if not success:
                return render_template(
                    "edit.html",
                    title="Artist",
                    subtitle=f"Editing artist_id = {artist_id}",
                    fields=fields,
                    values={
                        **artist,
                        "artist_name": artist_name,
                        "country": country,
                        "genre_id": genre_id,
                        "artist_popularity": artist_popularity,
                    },
                    cancel_url=url_for("get_artists"),
                    error_message=error
                )

            return redirect(url_for("get_artists"))

        return render_template(
            "edit.html",
            title="Artist",
            subtitle=f"Editing artist_id = {artist_id}",
            fields=fields,
            values=artist,
            cancel_url=url_for("get_artists"),
            error_message=None
        )

    @app.route("/artists/<int:artist_id>/delete", methods=["POST"])
    @role_required("admin")
    def delete_artist(artist_id):
        query = "DELETE FROM Artists WHERE artist_id = %s;"
        success, error = execute_safe_query(query, (artist_id,))

        if not success:
            return jsonify({"error": error}), 500

        return redirect(url_for("get_artists"))

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

        return render_template(
            "list.html",
            title="Albums",
            subtitle="Browse albums from the database",
            columns=["album_id", "album_name", "release_year", "artist_id", "genre_id", "cover_url"],
            keys=["album_id", "album_name", "release_year", "artist_id", "genre_id", "cover_url"],
            rows=rows,
            show_actions=is_admin(),
            add_url=(url_for("create_album") if is_admin() else None),
            edit_url_builder=(album_edit_url if is_admin() else None),
            delete_url_builder=(album_delete_url if is_admin() else None),
            description=None
        )

    # ADDED: Albums CRUD 
    @app.route("/albums/new", methods=["GET", "POST"])
    @role_required("admin")
    def create_album():
        genres, artists = get_genres_and_artists()
        fields = build_album_fields(genres, artists)

        if request.method == "POST":
            album_name = request.form.get("album_name")
            release_year = request.form.get("release_year") or None
            artist_id = request.form.get("artist_id") or None
            genre_id = request.form.get("genre_id") or None
            cover_url = request.form.get("cover_url") or None

            query = """
                INSERT INTO Albums (album_name, release_year, artist_id, genre_id, cover_url)
                VALUES (%s, %s, %s, %s, %s);
            """
            params = (album_name, release_year, artist_id, genre_id, cover_url)

            success, error = execute_safe_query(query, params)
            if not success:
                return render_template(
                    "add.html",
                    title="Album",
                    subtitle="Create a new album record",
                    fields=fields,
                    cancel_url=url_for("get_albums"),
                    error_message=error
                )

            return redirect(url_for("get_albums"))

        return render_template(
            "add.html",
            title="Album",
            subtitle="Create a new album record",
            fields=fields,
            cancel_url=url_for("get_albums"),
            error_message=None
        )

    @app.route("/albums/<int:album_id>/edit", methods=["GET", "POST"])
    @role_required("admin")
    def edit_album(album_id):
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Cannot connect to database"}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Albums WHERE album_id = %s;", (album_id,))
        album = cursor.fetchone()

        cursor.close()
        conn.close()

        if not album:
            return redirect(url_for("get_albums"))

        genres, artists = get_genres_and_artists()
        fields = build_album_fields(genres, artists)

        if request.method == "POST":
            album_name = request.form.get("album_name")
            release_year = request.form.get("release_year") or None
            artist_id = request.form.get("artist_id") or None
            genre_id = request.form.get("genre_id") or None
            cover_url = request.form.get("cover_url") or None

            query = """
                UPDATE Albums
                SET album_name = %s,
                    release_year = %s,
                    artist_id = %s,
                    genre_id = %s,
                    cover_url = %s
                WHERE album_id = %s;
            """
            params = (album_name, release_year, artist_id, genre_id, cover_url, album_id)

            success, error = execute_safe_query(query, params)
            if not success:
                return render_template(
                    "edit.html",
                    title="Album",
                    subtitle=f"Editing album_id = {album_id}",
                    fields=fields,
                    values={
                        **album,
                        "album_name": album_name,
                        "release_year": release_year,
                        "artist_id": artist_id,
                        "genre_id": genre_id,
                        "cover_url": cover_url,
                    },
                    cancel_url=url_for("get_albums"),
                    error_message=error
                )

            return redirect(url_for("get_albums"))

        return render_template(
            "edit.html",
            title="Album",
            subtitle=f"Editing album_id = {album_id}",
            fields=fields,
            values=album,
            cancel_url=url_for("get_albums"),
            error_message=None
        )

    @app.route("/albums/<int:album_id>/delete", methods=["POST"])
    @role_required("admin")
    def delete_album(album_id):
        query = "DELETE FROM Albums WHERE album_id = %s;"
        success, error = execute_safe_query(query, (album_id,))

        if not success:
            return jsonify({"error": error}), 500

        return redirect(url_for("get_albums"))

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

        return render_template(
            "list.html",
            title="Tracks",
            subtitle="Browse tracks from the database",
            columns=["track_id", "track_name", "album_id", "artist_id", "genre_id", "duration", "explicit", "popularity"],
            keys=["track_id", "track_name", "album_id", "artist_id", "genre_id", "duration", "explicit", "popularity"],
            rows=rows,
            show_actions=is_admin(),
            add_url=(url_for("create_track") if is_admin() else None),
            edit_url_builder=(track_edit_url if is_admin() else None),
            delete_url_builder=(track_delete_url if is_admin() else None),
            description=None
        )

    # ADDED: Tracks CRUD 
    @app.route("/tracks/new", methods=["GET", "POST"])
    @role_required("admin")
    def create_track():
        genres, artists = get_genres_and_artists()
        albums = get_albums_list()
        fields = build_track_fields(genres, artists, albums)

        if request.method == "POST":
            track_name = request.form.get("track_name")
            album_id = request.form.get("album_id") or None
            artist_id = request.form.get("artist_id") or None
            genre_id = request.form.get("genre_id") or None
            duration = request.form.get("duration") or None
            explicit = request.form.get("explicit") or None
            popularity = request.form.get("popularity") or None

            query = """
                INSERT INTO Tracks (track_name, album_id, artist_id, genre_id, duration, explicit, popularity)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """
            params = (track_name, album_id, artist_id, genre_id, duration, explicit, popularity)

            success, error = execute_safe_query(query, params)
            if not success:
                return render_template(
                    "add.html",
                    title="Track",
                    subtitle="Create a new track record",
                    fields=fields,
                    cancel_url=url_for("get_tracks"),
                    error_message=error
                )

            return redirect(url_for("get_tracks"))

        return render_template(
            "add.html",
            title="Track",
            subtitle="Create a new track record",
            fields=fields,
            cancel_url=url_for("get_tracks"),
            error_message=None
        )

    @app.route("/tracks/<int:track_id>/edit", methods=["GET", "POST"])
    @role_required("admin")
    def edit_track(track_id):
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Cannot connect to database"}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Tracks WHERE track_id = %s;", (track_id,))
        track = cursor.fetchone()

        cursor.close()
        conn.close()

        if not track:
            return redirect(url_for("get_tracks"))

        genres, artists = get_genres_and_artists()
        albums = get_albums_list()
        fields = build_track_fields(genres, artists, albums)

        if request.method == "POST":
            track_name = request.form.get("track_name")
            album_id = request.form.get("album_id") or None
            artist_id = request.form.get("artist_id") or None
            genre_id = request.form.get("genre_id") or None
            duration = request.form.get("duration") or None
            explicit = request.form.get("explicit") or None
            popularity = request.form.get("popularity") or None

            query = """
                UPDATE Tracks
                SET track_name = %s,
                    album_id = %s,
                    artist_id = %s,
                    genre_id = %s,
                    duration = %s,
                    explicit = %s,
                    popularity = %s
                WHERE track_id = %s;
            """
            params = (track_name, album_id, artist_id, genre_id, duration, explicit, popularity, track_id)

            success, error = execute_safe_query(query, params)
            if not success:
                return render_template(
                    "edit.html",
                    title="Track",
                    subtitle=f"Editing track_id = {track_id}",
                    fields=fields,
                    values={
                        **track,
                        "track_name": track_name,
                        "album_id": album_id,
                        "artist_id": artist_id,
                        "genre_id": genre_id,
                        "duration": duration,
                        "explicit": explicit,
                        "popularity": popularity,
                    },
                    cancel_url=url_for("get_tracks"),
                    error_message=error
                )

            return redirect(url_for("get_tracks"))

        return render_template(
            "edit.html",
            title="Track",
            subtitle=f"Editing track_id = {track_id}",
            fields=fields,
            values=track,
            cancel_url=url_for("get_tracks"),
            error_message=None
        )

    @app.route("/tracks/<int:track_id>/delete", methods=["POST"])
    @role_required("admin")
    def delete_track(track_id):
        query = "DELETE FROM Tracks WHERE track_id = %s;"
        success, error = execute_safe_query(query, (track_id,))

        if not success:
            return jsonify({"error": error}), 500

        return redirect(url_for("get_tracks"))
    # -------------------------------------------------------------

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

        return render_template(
            "list.html",
            title="Audio Features",
            subtitle="Browse audio feature records",
            columns=["feature_id", "track_id", "danceability", "energy", "valence", "tempo", "loudness", "acousticness"],
            keys=["feature_id", "track_id", "danceability", "energy", "valence", "tempo", "loudness", "acousticness"],
            rows=rows,
            show_actions=is_admin(),
            add_url=(url_for("create_audiofeatures") if is_admin() else None),
            edit_url_builder=(audiofeatures_edit_url if is_admin() else None),
            delete_url_builder=(audiofeatures_delete_url if is_admin() else None),
            description=None
        )

    # ADDED: AudioFeatures CRUD 
    @app.route("/audiofeatures/new", methods=["GET", "POST"])
    @role_required("admin")
    def create_audiofeatures():
        tracks = get_tracks_list()
        fields = build_audiofeatures_fields(tracks)

        if request.method == "POST":
            track_id = request.form.get("track_id") or None
            danceability = request.form.get("danceability") or None
            energy = request.form.get("energy") or None
            valence = request.form.get("valence") or None
            tempo = request.form.get("tempo") or None
            loudness = request.form.get("loudness") or None
            acousticness = request.form.get("acousticness") or None

            query = """
                INSERT INTO AudioFeatures (track_id, danceability, energy, valence, tempo, loudness, acousticness)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """
            params = (track_id, danceability, energy, valence, tempo, loudness, acousticness)

            success, error = execute_safe_query(query, params)
            if not success:
                return render_template(
                    "add.html",
                    title="Audio Features",
                    subtitle="Create a new audio feature record",
                    fields=fields,
                    cancel_url=url_for("get_audio_features"),
                    error_message=error
                )

            return redirect(url_for("get_audio_features"))

        return render_template(
            "add.html",
            title="Audio Features",
            subtitle="Create a new audio feature record",
            fields=fields,
            cancel_url=url_for("get_audio_features"),
            error_message=None
        )

    @app.route("/audiofeatures/<int:feature_id>/edit", methods=["GET", "POST"])
    @role_required("admin")
    def edit_audiofeatures(feature_id):
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Cannot connect to database"}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM AudioFeatures WHERE feature_id = %s;", (feature_id,))
        feature = cursor.fetchone()

        cursor.close()
        conn.close()

        if not feature:
            return redirect(url_for("get_audio_features"))

        tracks = get_tracks_list()
        fields = build_audiofeatures_fields(tracks)

        if request.method == "POST":
            track_id = request.form.get("track_id") or None
            danceability = request.form.get("danceability") or None
            energy = request.form.get("energy") or None
            valence = request.form.get("valence") or None
            tempo = request.form.get("tempo") or None
            loudness = request.form.get("loudness") or None
            acousticness = request.form.get("acousticness") or None

            query = """
                UPDATE AudioFeatures
                SET track_id = %s,
                    danceability = %s,
                    energy = %s,
                    valence = %s,
                    tempo = %s,
                    loudness = %s,
                    acousticness = %s
                WHERE feature_id = %s;
            """
            params = (track_id, danceability, energy, valence, tempo, loudness, acousticness, feature_id)

            success, error = execute_safe_query(query, params)
            if not success:
                return render_template(
                    "edit.html",
                    title="Audio Features",
                    subtitle=f"Editing feature_id = {feature_id}",
                    fields=fields,
                    values={
                        **feature,
                        "track_id": track_id,
                        "danceability": danceability,
                        "energy": energy,
                        "valence": valence,
                        "tempo": tempo,
                        "loudness": loudness,
                        "acousticness": acousticness,
                    },
                    cancel_url=url_for("get_audio_features"),
                    error_message=error
                )

            return redirect(url_for("get_audio_features"))

        return render_template(
            "edit.html",
            title="Audio Features",
            subtitle=f"Editing feature_id = {feature_id}",
            fields=fields,
            values=feature,
            cancel_url=url_for("get_audio_features"),
            error_message=None
        )

    @app.route("/audiofeatures/<int:feature_id>/delete", methods=["POST"])
    @role_required("admin")
    def delete_audiofeatures(feature_id):
        query = "DELETE FROM AudioFeatures WHERE feature_id = %s;"
        success, error = execute_safe_query(query, (feature_id,))

        if not success:
            return jsonify({"error": error}), 500

        return redirect(url_for("get_audio_features"))

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

        return render_template(
            "list.html",
            title="Users",
            subtitle="View and manage users",
            columns=["user_id", "username", "email", "phone_number", "dob", "genre_id", "artist_id"],
            keys=["user_id", "username", "email", "phone_number", "dob", "genre_id", "artist_id"],
            rows=rows,
            show_actions=True,
            add_url=url_for("create_user"),
            edit_url_builder=user_edit_url,
            delete_url_builder=user_delete_url,
            description=None
        )

    @app.route("/users/new", methods=["GET", "POST"])
    @role_required("admin")
    def create_user():
        genres, artists = get_genres_and_artists()
        fields = build_user_fields(genres, artists)

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
                return render_template(
                    "add.html",
                    title="User",
                    subtitle="Create a new user record",
                    fields=fields,
                    cancel_url=url_for("get_users"),
                    error_message=error
                )

            return redirect(url_for("get_users"))

        return render_template(
            "add.html",
            title="User",
            subtitle="Create a new user record",
            fields=fields,
            cancel_url=url_for("get_users"),
            error_message=None
        )

    @app.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
    @role_required("admin")
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

        genres, artists = get_genres_and_artists()
        fields = build_user_fields(genres, artists)

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
                return render_template(
                    "edit.html",
                    title="User",
                    subtitle=f"Editing user_id = {user_id}",
                    fields=fields,
                    values={
                        **user,
                        "username": username,
                        "email": email,
                        "phone_number": phone_number,
                        "dob": dob,
                        "genre_id": genre_id,
                        "artist_id": artist_id,
                    },
                    cancel_url=url_for("get_users"),
                    error_message=error
                )

            return redirect(url_for("get_users"))

        return render_template(
            "edit.html",
            title="User",
            subtitle=f"Editing user_id = {user_id}",
            fields=fields,
            values=user,
            cancel_url=url_for("get_users"),
            error_message=None
        )

    @app.route("/users/<int:user_id>/delete", methods=["POST"])
    @role_required("admin")
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
                session["role"] = "admin"   #  ADDED: role 
                return redirect(url_for("get_users"))
            else:
                error = "Wrong username or password."

        return render_template("login.html", error=error)

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))
    

    #  Chosse table pags for navbar Add/Edit
    @app.route("/choose/add")
    @role_required("admin")
    def choose_add():
        tables = [
            {"label": "Genres", "url": url_for("create_genre")},
            {"label": "Artists", "url": url_for("create_artist")},
            {"label": "Albums", "url": url_for("create_album")},
            {"label": "Tracks", "url": url_for("create_track")},
            {"label": "Audio Features", "url": url_for("create_audiofeatures")},
            {"label": "Users", "url": url_for("create_user")},
        ]
        return render_template(
            "choose_table.html",
            title="Add record",
            subtitle="Choose which table you want to add a new record to:",
            tables=tables,
            hint=None
        )

    @app.route("/choose/edit")
    @role_required("admin")
    def choose_edit():
        tables = [
            {"label": "Genres", "url": url_for("get_genres")},
            {"label": "Artists", "url": url_for("get_artists")},
            {"label": "Albums", "url": url_for("get_albums")},
            {"label": "Tracks", "url": url_for("get_tracks")},
            {"label": "Audio Features", "url": url_for("get_audio_features")},
            {"label": "Users", "url": url_for("get_users")},
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
