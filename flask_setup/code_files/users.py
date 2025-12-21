from flask import Blueprint, request, redirect, url_for, render_template, session
import mysql.connector
from .shared import get_db_connection, execute_safe_query, role_required, get_genres_and_artists, login_required, paginate_query

users_bp = Blueprint('users', __name__)

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
    return url_for("users.edit_user", user_id=row["user_id"])

def user_delete_url(row):
    return url_for("users.delete_user", user_id=row["user_id"])

@users_bp.route("/")
@login_required
def get_users():
    conn = get_db_connection()
    if conn is None:
        return

    cursor = conn.cursor(dictionary=True)
    
    # Get page from query params, default to 1
    page = request.args.get("page", 1, type=int)
    per_page = 10  # Items per page
    
    base_query = "SELECT user_id, username, email, phone_number, dob, genre_id, artist_id FROM Users"
    count_query = "SELECT COUNT(*) AS total FROM Users"
    
    rows, total_count, total_pages, current_page = paginate_query(
        cursor, base_query, count_query, page=page, per_page=per_page
    )

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
        add_url=url_for("users.create_user"),
        edit_url_builder=user_edit_url,
        delete_url_builder=user_delete_url,
        description=None,
        # Pagination data
        current_page=current_page,
        total_pages=total_pages,
        total_count=total_count
    )

@users_bp.route("/new", methods=["GET", "POST"])
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
                cancel_url=url_for("users.get_users"),
                error_message=error
            )

        return redirect(url_for("users.get_users"))

    return render_template(
        "add.html",
        title="User",
        subtitle="Create a new user record",
        fields=fields,
        cancel_url=url_for("users.get_users"),
        error_message=None
    )

@users_bp.route("/<int:user_id>/edit", methods=["GET", "POST"])
@role_required("admin")
def edit_user(user_id):
    conn = get_db_connection()
    if conn is None:
        return

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Users WHERE user_id = %s;", (user_id,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if not user:
        return redirect(url_for("users.get_users"))

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
                cancel_url=url_for("users.get_users"),
                error_message=error
            )

        return redirect(url_for("users.get_users"))

    return render_template(
        "edit.html",
        title="User",
        subtitle=f"Editing user_id = {user_id}",
        fields=fields,
        values=user,
        cancel_url=url_for("users.get_users"),
        error_message=None
    )

@users_bp.route("/<int:user_id>/delete", methods=["POST"])
@role_required("admin")
def delete_user(user_id):
    query = "DELETE FROM Users WHERE user_id = %s;"
    success, error = execute_safe_query(query, (user_id,))

    if not success:
        return

    return redirect(url_for("users.get_users"))
