from flask import Blueprint, request, redirect, url_for, render_template, jsonify
import mysql.connector
from .shared import get_db_connection, execute_safe_query, role_required, get_genres_and_artists, get_albums_list, is_admin, paginate_query

tracks_bp = Blueprint('tracks', __name__)

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

def track_edit_url(row):
    return url_for("tracks.edit_track", track_id=row["track_id"])

def track_delete_url(row):
    return url_for("tracks.delete_track", track_id=row["track_id"])

@tracks_bp.route("/")
def get_tracks():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Cannot connect to database"}), 500

    cursor = conn.cursor(dictionary=True)
    
    # Get page from query params, default to 1
    page = request.args.get("page", 1, type=int)
    per_page = 10  # Items per page
    
    base_query = "SELECT track_id, track_name, album_id, artist_id, genre_id, duration, explicit, popularity FROM Tracks"
    count_query = "SELECT COUNT(*) AS total FROM Tracks"
    
    rows, total_count, total_pages, current_page = paginate_query(
        cursor, base_query, count_query, page=page, per_page=per_page
    )

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
        add_url=(url_for("tracks.create_track") if is_admin() else None),
        edit_url_builder=(track_edit_url if is_admin() else None),
        delete_url_builder=(track_delete_url if is_admin() else None),
        description=None,
        # Pagination data
        current_page=current_page,
        total_pages=total_pages,
        total_count=total_count
    )

@tracks_bp.route("/new", methods=["GET", "POST"])
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
                cancel_url=url_for("tracks.get_tracks"),
                error_message=error
            )

        return redirect(url_for("tracks.get_tracks"))

    return render_template(
        "add.html",
        title="Track",
        subtitle="Create a new track record",
        fields=fields,
        cancel_url=url_for("tracks.get_tracks"),
        error_message=None
    )

@tracks_bp.route("/<int:track_id>/edit", methods=["GET", "POST"])
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
        return redirect(url_for("tracks.get_tracks"))

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
                cancel_url=url_for("tracks.get_tracks"),
                error_message=error
            )

        return redirect(url_for("tracks.get_tracks"))

    return render_template(
        "edit.html",
        title="Track",
        subtitle=f"Editing track_id = {track_id}",
        fields=fields,
        values=track,
        cancel_url=url_for("tracks.get_tracks"),
        error_message=None
    )

@tracks_bp.route("/<int:track_id>/delete", methods=["POST"])
@role_required("admin")
def delete_track(track_id):
    query = "DELETE FROM Tracks WHERE track_id = %s;"
    success, error = execute_safe_query(query, (track_id,))

    if not success:
        return jsonify({"error": error}), 500

    return redirect(url_for("tracks.get_tracks"))
