from flask import Blueprint, request, redirect, url_for, render_template, jsonify
import mysql.connector
from .shared import get_db_connection, execute_safe_query, role_required, get_genres_and_artists, is_admin, paginate_query

artists_bp = Blueprint('artists', __name__)

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

def artist_edit_url(row):
    return url_for("artists.edit_artist", artist_id=row["artist_id"])

def artist_delete_url(row):
    return url_for("artists.delete_artist", artist_id=row["artist_id"])


@artists_bp.route("/")
def get_artists():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Cannot connect to database"}), 500

    cursor = conn.cursor(dictionary=True)
    
    # Get page from query params, default to 1
    page = request.args.get("page", 1, type=int)
    per_page = 10  # Items per page
    
    base_query = "SELECT artist_id, artist_name, country, genre_id, artist_popularity FROM Artists"
    count_query = "SELECT COUNT(*) AS total FROM Artists"
    
    rows, total_count, total_pages, current_page = paginate_query(
        cursor, base_query, count_query, page=page, per_page=per_page
    )

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
        add_url=(url_for("artists.create_artist") if is_admin() else None),
        edit_url_builder=(artist_edit_url if is_admin() else None),
        delete_url_builder=(artist_delete_url if is_admin() else None),
        description=None,
        # Pagination data
        current_page=current_page,
        total_pages=total_pages,
        total_count=total_count
    )


@artists_bp.route("/new", methods=["GET", "POST"])
@role_required("admin")
def create_artist():
    genres, _ = get_genres_and_artists()
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
                cancel_url=url_for("artists.get_artists"),
                error_message=error
            )

        return redirect(url_for("artists.get_artists"))

    return render_template(
        "add.html",
        title="Artist",
        subtitle="Create a new artist record",
        fields=fields,
        cancel_url=url_for("artists.get_artists"),
        error_message=None
    )

@artists_bp.route("/<int:artist_id>/edit", methods=["GET", "POST"])
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
        return redirect(url_for("artists.get_artists"))

    genres, _ = get_genres_and_artists()
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
                cancel_url=url_for("artists.get_artists"),
                error_message=error
            )

        return redirect(url_for("artists.get_artists"))

    return render_template(
        "edit.html",
        title="Artist",
        subtitle=f"Editing artist_id = {artist_id}",
        fields=fields,
        values=artist,
        cancel_url=url_for("artists.get_artists"),
        error_message=None
    )

@artists_bp.route("/<int:artist_id>/delete", methods=["POST"])
@role_required("admin")
def delete_artist(artist_id):
    query = "DELETE FROM Artists WHERE artist_id = %s;"
    success, error = execute_safe_query(query, (artist_id,))

    if not success:
        return jsonify({"error": error}), 500

    return redirect(url_for("artists.get_artists"))

@artists_bp.route("/search")
def search_artists():
    """Search artists by name - returns JSON for autocomplete"""
    query = request.args.get("q", "").strip()
    limit = request.args.get("limit", 10, type=int)
    
    if len(query) < 2:
        return jsonify({"artists": []})
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT artist_id, artist_name, country 
           FROM Artists 
           WHERE artist_name LIKE %s 
           ORDER BY artist_popularity DESC, artist_name ASC
           LIMIT %s""",
        (f"%{query}%", limit)
    )
    artists = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify({"artists": artists})
