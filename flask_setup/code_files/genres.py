from flask import Blueprint, request, redirect, url_for, render_template, jsonify, session
import mysql.connector
from .shared import get_db_connection, execute_safe_query, role_required, is_admin, paginate_query

genres_bp = Blueprint('genres', __name__)

def build_genre_fields():
    return [
        {"name": "parent_genre", "label": "Parent Genre", "type": "text"},
        {"name": "genre_name", "label": "Genre Name", "type": "text"},
        {"name": "genre_description", "label": "Genre Description", "type": "text"},
    ]

def genre_edit_url(row):
    return url_for("genres.edit_genre", genre_id=row["genre_id"])

def genre_delete_url(row):
    return url_for("genres.delete_genre", genre_id=row["genre_id"])

@genres_bp.route("/")
def get_genres():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Cannot connect to database"}), 500

    cursor = conn.cursor(dictionary=True)
    
    # Get page from query params, default to 1
    page = request.args.get("page", 1, type=int)
    per_page = 10  # Items per page
    
    base_query = "SELECT genre_id, parent_genre, genre_name, genre_description FROM Genres"
    count_query = "SELECT COUNT(*) AS total FROM Genres"
    
    rows, total_count, total_pages, current_page = paginate_query(
        cursor, base_query, count_query, page=page, per_page=per_page
    )

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
        add_url=(url_for("genres.create_genre") if is_admin() else None),
        edit_url_builder=(genre_edit_url if is_admin() else None),
        delete_url_builder=(genre_delete_url if is_admin() else None),
        description=None,
        # Pagination data
        current_page=current_page,
        total_pages=total_pages,
        total_count=total_count
    )

@genres_bp.route("/new", methods=["GET", "POST"])
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
                cancel_url=url_for("genres.get_genres"),
                error_message=error
            )

        return redirect(url_for("genres.get_genres"))

    return render_template(
        "add.html",
        title="Genre",
        subtitle="Create a new genre record",
        fields=fields,
        cancel_url=url_for("genres.get_genres"),
        error_message=None
    )

@genres_bp.route("/<int:genre_id>/edit", methods=["GET", "POST"])
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
        return redirect(url_for("genres.get_genres"))

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
                cancel_url=url_for("genres.get_genres"),
                error_message=error
            )

        return redirect(url_for("genres.get_genres"))

    return render_template(
        "edit.html",
        title="Genre",
        subtitle=f"Editing genre_id = {genre_id}",
        fields=fields,
        values=genre,
        cancel_url=url_for("genres.get_genres"),
        error_message=None
    )

@genres_bp.route("/<int:genre_id>/delete", methods=["POST"])
@role_required("admin")
def delete_genre(genre_id):
    query = "DELETE FROM Genres WHERE genre_id = %s;"
    success, error = execute_safe_query(query, (genre_id,))

    if not success:
        return jsonify({"error": error}), 500

    return redirect(url_for("genres.get_genres"))
