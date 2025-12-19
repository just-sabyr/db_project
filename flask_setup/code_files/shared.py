from flask import current_app, session, redirect, url_for
import mysql.connector
from mysql.connector import Error
from functools import wraps

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=current_app.config["DB_HOST"],
            user=current_app.config["DB_USER"],
            password=current_app.config["DB_PASSWORD"],
            database=current_app.config["DB_NAME"]
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

def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not session.get("logged_in"):
                return redirect(url_for("login"))

            user_role = session.get("role")
            if user_role not in roles:
                return "<h1>Permission Denied</h1><p>You do not have the required role to access this page.</p>", 403

            return view_func(*args, **kwargs)
        return wrapped
    return decorator

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
