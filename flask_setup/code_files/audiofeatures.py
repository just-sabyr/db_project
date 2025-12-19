from flask import Blueprint, request, redirect, url_for, render_template, jsonify
import mysql.connector
from .shared import get_db_connection, execute_safe_query, role_required, get_tracks_list, is_admin

audiofeatures_bp = Blueprint('audiofeatures', __name__)

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

def audiofeatures_edit_url(row):
    return url_for("audiofeatures.edit_audiofeatures", feature_id=row["feature_id"])

def audiofeatures_delete_url(row):
    return url_for("audiofeatures.delete_audiofeatures", feature_id=row["feature_id"])

@audiofeatures_bp.route("/")
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
        add_url=(url_for("audiofeatures.create_audiofeatures") if is_admin() else None),
        edit_url_builder=(audiofeatures_edit_url if is_admin() else None),
        delete_url_builder=(audiofeatures_delete_url if is_admin() else None),
        description=None
    )

@audiofeatures_bp.route("/new", methods=["GET", "POST"])
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
                cancel_url=url_for("audiofeatures.get_audio_features"),
                error_message=error
            )

        return redirect(url_for("audiofeatures.get_audio_features"))

    return render_template(
        "add.html",
        title="Audio Features",
        subtitle="Create a new audio feature record",
        fields=fields,
        cancel_url=url_for("audiofeatures.get_audio_features"),
        error_message=None
    )

@audiofeatures_bp.route("/<int:feature_id>/edit", methods=["GET", "POST"])
@role_required("admin")
def edit_audiofeatures(feature_id):
    conn = get_db_connection()
    if conn is None:
        return

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM AudioFeatures WHERE feature_id = %s;", (feature_id,))
    feature = cursor.fetchone()

    cursor.close()
    conn.close()

    if not feature:
        return redirect(url_for("audiofeatures.get_audio_features"))

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
                cancel_url=url_for("audiofeatures.get_audio_features"),
                error_message=error
            )

        return redirect(url_for("audiofeatures.get_audio_features"))

    return render_template(
        "edit.html",
        title="Audio Features",
        subtitle=f"Editing feature_id = {feature_id}",
        fields=fields,
        values=feature,
        cancel_url=url_for("audiofeatures.get_audio_features"),
        error_message=None
    )

@audiofeatures_bp.route("/<int:feature_id>/delete", methods=["POST"])
@role_required("admin")
def delete_audiofeatures(feature_id):
    query = "DELETE FROM AudioFeatures WHERE feature_id = %s;"
    success, error = execute_safe_query(query, (feature_id,))

    if not success:
        return

    return redirect(url_for("audiofeatures.get_audio_features"))
