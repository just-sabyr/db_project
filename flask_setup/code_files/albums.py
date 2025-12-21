from flask import Blueprint, request, redirect, url_for, render_template, jsonify
import mysql.connector
from .shared import get_db_connection, execute_safe_query, role_required, get_genres_and_artists, is_admin, paginate_query

albums_bp = Blueprint('albums', __name__)

def build_album_fields(genres):
    """Build fields for album form - artist uses search"""
    return [
        {"name": "album_name", "label": "Album Name", "type": "text", "required": True},
        {"name": "release_year", "label": "Release Year", "type": "text"},
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
            "name": "genre_id", "label": "Genre", "type": "select",
            "options": [{"value": g["genre_id"], "text": g["genre_name"]} for g in genres]
        },
        {"name": "cover_url", "label": "Cover URL", "type": "text"},
    ]

def album_edit_url(row):
    return url_for("albums.edit_album", album_id=row["album_id"])

def album_delete_url(row):
    return url_for("albums.delete_album", album_id=row["album_id"])

@albums_bp.route("/")
def get_albums():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Cannot connect to database"}), 500

    cursor = conn.cursor(dictionary=True)

    # Get page from query params, default to 1
    page = request.args.get("page", 1, type=int)
    per_page = 10  # Items per page
    
    base_query = "SELECT album_id, album_name, release_year, artist_id, genre_id, cover_url FROM Albums"
    count_query = "SELECT COUNT(*) AS total FROM Albums"
    
    rows, total_count, total_pages, current_page = paginate_query(
        cursor, base_query, count_query, page=page, per_page=per_page
    )
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
        add_url=(url_for("albums.create_album") if is_admin() else None),
        edit_url_builder=(album_edit_url if is_admin() else None),
        delete_url_builder=(album_delete_url if is_admin() else None),
        description=None,
        # Pagination data
        current_page=current_page,
        total_pages=total_pages,
        total_count=total_count
    )

@albums_bp.route("/by-artist/<int:artist_id>")
def get_albums_by_artist(artist_id):
    """Get all albums for a specific artist"""
    conn = get_db_connection()
    if conn is None:
        return jsonify({"albums": []})
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT album_id, album_name
        FROM Albums
        WHERE artist_id = %s
        ORDER BY album_name
    """, (artist_id,))
    
    albums = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify({"albums": albums})


@albums_bp.route("/new", methods=["GET", "POST"])
@role_required("admin")
def create_album():
    genres, _ = get_genres_and_artists()  # Don't need artists list anymore
    fields = build_album_fields(genres)

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
                cancel_url=url_for("albums.get_albums"),
                error_message=error
            )

        return redirect(url_for("albums.get_albums"))

    return render_template(
        "add.html",
        title="Album",
        subtitle="Create a new album record",
        fields=fields,
        cancel_url=url_for("albums.get_albums"),
        error_message=None
    )


@albums_bp.route("/<int:album_id>/edit", methods=["GET", "POST"])
@role_required("admin")
def edit_album(album_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Cannot connect to database"}), 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Albums WHERE album_id = %s;", (album_id,))
    album = cursor.fetchone()

    if not album:
        cursor.close()
        conn.close()
        return redirect(url_for("albums.get_albums"))

    # Get current artist name for search input
    current_artist_name = None
    if album.get("artist_id"):
        cursor.execute(
            "SELECT artist_name FROM Artists WHERE artist_id = %s",
            (album["artist_id"],)
        )
        artist = cursor.fetchone()
        if artist:
            current_artist_name = artist["artist_name"]

    cursor.close()
    conn.close()

    genres, _ = get_genres_and_artists()  # Don't need artists list anymore
    fields = build_album_fields(genres)

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
                current_artist_name=current_artist_name,
                cancel_url=url_for("albums.get_albums"),
                error_message=error
            )

        return redirect(url_for("albums.get_albums"))

    return render_template(
        "edit.html",
        title="Album",
        subtitle=f"Editing album_id = {album_id}",
        fields=fields,
        values=album,
        current_artist_name=current_artist_name,
        cancel_url=url_for("albums.get_albums"),
        error_message=None
    )

@albums_bp.route("/<int:album_id>/delete", methods=["POST"])
@role_required("admin")
def delete_album(album_id):
    query = "DELETE FROM Albums WHERE album_id = %s;"
    success, error = execute_safe_query(query, (album_id,))

    if not success:
        return jsonify({"error": error}), 500

    return redirect(url_for("albums.get_albums"))

@albums_bp.route("/search")
def search_albums():
    """Search albums by name for autocomplete"""
    query = request.args.get("q", "").strip()
    
    if len(query) < 1:
        return jsonify({"albums": []})
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"albums": []})
    
    cursor = conn.cursor(dictionary=True)
    
    # Search albums and include artist name for display
    cursor.execute("""
        SELECT a.album_id, a.album_name, ar.artist_name
        FROM Albums a
        LEFT JOIN Artists ar ON a.artist_id = ar.artist_id
        WHERE a.album_name LIKE %s
        ORDER BY a.album_name
        LIMIT 20
    """, (f"%{query}%",))
    
    albums = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify({"albums": albums})
