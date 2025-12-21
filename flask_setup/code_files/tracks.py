from flask import Blueprint, request, redirect, url_for, render_template, jsonify
import mysql.connector
from .shared import get_db_connection, execute_safe_query, role_required, get_genres_and_artists, is_admin, paginate_query

tracks_bp = Blueprint('tracks', __name__)

def build_track_fields(genres):
    """Build fields for track form - artist uses search, album depends on artist"""
    return [
        {"name": "track_name", "label": "Track Name", "type": "text", "required": True},
        {
            "name": "artist_id", 
            "label": "Artist", 
            "type": "search",
            "search_url": "/artists/search",
            "data_key": "artists",
            "id_field": "artist_id",
            "name_field": "artist_name",
            "secondary_field": "country",
            "placeholder": "Search for an artist..."
        },
        {
            "name": "album_id", 
            "label": "Album", 
            "type": "dependent_select",
            "depends_on": "artist_id",
            "fetch_url": "/albums/by-artist/",
            "data_key": "albums",
            "id_field": "album_id",
            "name_field": "album_name",
            "placeholder": "Select an artist first..."
        },
        {
            "name": "genre_id", "label": "Genre", "type": "select",
            "options": [{"value": g["genre_id"], "text": g["genre_name"]} for g in genres]
        },
        {"name": "duration", "label": "Duration (seconds)", "type": "text"},
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
    genres, _ = get_genres_and_artists()
    fields = build_track_fields(genres)

    if request.method == "POST":
        track_name = request.form.get("track_name")
        album_id = request.form.get("album_id") or None
        artist_id = request.form.get("artist_id") or None
        genre_id = request.form.get("genre_id") or None
        duration = request.form.get("duration") or None
        explicit = request.form.get("explicit") or None
        popularity = request.form.get("popularity") or None

        # Validate album belongs to artist if both are provided
        if album_id and artist_id:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(
                    "SELECT artist_id FROM Albums WHERE album_id = %s",
                    (album_id,)
                )
                album = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if album and album["artist_id"] and str(album["artist_id"]) != str(artist_id):
                    return render_template(
                        "add.html",
                        title="Track",
                        subtitle="Create a new track record",
                        fields=fields,
                        cancel_url=url_for("tracks.get_tracks"),
                        error_message="The selected album does not belong to the selected artist."
                    )

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

    if not track:
        cursor.close()
        conn.close()
        return redirect(url_for("tracks.get_tracks"))

    # Get display names for search fields
    search_display_values = {}
    
    if track.get("artist_id"):
        cursor.execute("SELECT artist_name FROM Artists WHERE artist_id = %s", (track["artist_id"],))
        artist = cursor.fetchone()
        if artist:
            search_display_values["artist_id"] = artist["artist_name"]

    if track.get("album_id"):
        cursor.execute("SELECT album_name FROM Albums WHERE album_id = %s", (track["album_id"],))
        album = cursor.fetchone()
        if album:
            search_display_values["album_id"] = album["album_name"]

    cursor.close()
    conn.close()

    genres, _ = get_genres_and_artists()
    fields = build_track_fields(genres)

    if request.method == "POST":
        track_name = request.form.get("track_name")
        album_id = request.form.get("album_id") or None
        artist_id = request.form.get("artist_id") or None
        genre_id = request.form.get("genre_id") or None
        duration = request.form.get("duration") or None
        explicit = request.form.get("explicit") or None
        popularity = request.form.get("popularity") or None

        # Validate album belongs to artist if both are provided
        if album_id and artist_id:
            conn2 = get_db_connection()
            if conn2:
                cursor2 = conn2.cursor(dictionary=True)
                cursor2.execute(
                    "SELECT artist_id FROM Albums WHERE album_id = %s",
                    (album_id,)
                )
                album_check = cursor2.fetchone()
                cursor2.close()
                conn2.close()
                
                if album_check and album_check["artist_id"] and str(album_check["artist_id"]) != str(artist_id):
                    return render_template(
                        "edit.html",
                        title="Track",
                        subtitle=f"Editing track_id = {track_id}",
                        fields=fields,
                        values=track,
                        search_display_values=search_display_values,
                        cancel_url=url_for("tracks.get_tracks"),
                        error_message="The selected album does not belong to the selected artist."
                    )

        query = """
            UPDATE Tracks
            SET track_name = %s, album_id = %s, artist_id = %s, genre_id = %s,
                duration = %s, explicit = %s, popularity = %s
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
                values=track,
                search_display_values=search_display_values,
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
        search_display_values=search_display_values,
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
    