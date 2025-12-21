from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .shared import get_db_connection, login_required

favorites_bp = Blueprint('favorites', __name__)


# ─────────────────────────────────────────────────────────────────────────────
# FAVORITE TRACKS
# ─────────────────────────────────────────────────────────────────────────────

@favorites_bp.route('/tracks')
@login_required
def list_favorite_tracks():
    user_id = session.get('user_id')
    if not user_id:
        flash("Admin account doesn't have favorites.", "warning")
        return redirect(url_for('index'))

    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "error")
        return redirect(url_for('index'))

    cursor = conn.cursor(dictionary=True)

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page

    # Get total count
    cursor.execute(
        "SELECT COUNT(*) AS total FROM UserFavoriteTracks WHERE user_id = %s",
        (user_id,)
    )
    total_count = cursor.fetchone()['total']
    total_pages = (total_count + per_page - 1) // per_page

    # Get favorite tracks with details
    cursor.execute("""
        SELECT uft.track_id, uft.added_at, t.track_name, 
               a.album_name, ar.artist_name
        FROM UserFavoriteTracks uft
        JOIN Tracks t ON uft.track_id = t.track_id
        LEFT JOIN Albums a ON t.album_id = a.album_id
        LEFT JOIN Artists ar ON t.artist_id = ar.artist_id
        WHERE uft.user_id = %s
        ORDER BY uft.added_at DESC
        LIMIT %s OFFSET %s
    """, (user_id, per_page, offset))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'list.html',
        title='My Favorite Tracks',
        subtitle='Tracks you have added to your favorites',
        columns=['Track', 'Artist', 'Album', 'Added'],
        keys=['track_name', 'artist_name', 'album_name', 'added_at'],
        rows=rows,
        show_actions=True,
        add_url=url_for('favorites.add_favorite_track'),
        edit_url_builder=None,
        delete_url_builder=lambda row: url_for('favorites.remove_favorite_track', track_id=row['track_id']),
        current_page=page,
        total_pages=total_pages,
        total_count=total_count
    )

@favorites_bp.route('/tracks/<int:track_id>/remove', methods=['POST'])
@login_required
def remove_favorite_track(track_id):
    user_id = session.get('user_id')
    if not user_id:
        flash("Admin account doesn't have favorites.", "warning")
        return redirect(url_for('index'))

    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "error")
        return redirect(url_for('favorites.list_favorite_tracks'))

    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM UserFavoriteTracks WHERE user_id = %s AND track_id = %s",
        (user_id, track_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash("Track removed from favorites.", "info")
    return redirect(url_for('favorites.list_favorite_tracks'))


# ─────────────────────────────────────────────────────────────────────────────
# FAVORITE ARTISTS
# ─────────────────────────────────────────────────────────────────────────────
@favorites_bp.route('/tracks/add', methods=['GET', 'POST'])
@login_required
def add_favorite_track():
    user_id = session.get('user_id')
    if not user_id:
        flash("User session not found.", "error")
        return redirect(url_for('login'))

    if request.method == 'POST':
        track_id = request.form.get('track_id')
        
        if not track_id:
            return render_template(
                'add.html',
                title='Favorite Track',
                subtitle='Search and add a track to your favorites',
                fields=_get_track_fields(),
                cancel_url=url_for('favorites.list_favorite_tracks'),
                error_message="Please select a track."
            )

        conn = get_db_connection()
        if conn is None:
            flash("Database connection failed.", "error")
            return redirect(url_for('favorites.list_favorite_tracks'))

        cursor = conn.cursor()
        
        try:
            # Check if already exists
            cursor.execute(
                "SELECT 1 FROM UserFavoriteTracks WHERE user_id = %s AND track_id = %s",
                (user_id, track_id)
            )
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return render_template(
                    'add.html',
                    title='Favorite Track',
                    subtitle='Search and add a track to your favorites',
                    fields=_get_track_fields(),
                    cancel_url=url_for('favorites.list_favorite_tracks'),
                    error_message="This track is already in your favorites."
                )
            
            # Insert favorite
            cursor.execute(
                "INSERT INTO UserFavoriteTracks (user_id, track_id) VALUES (%s, %s)",
                (user_id, track_id)
            )
            conn.commit()
            cursor.close()
            conn.close()
            
            flash("Track added to favorites!", "success")
            return redirect(url_for('favorites.list_favorite_tracks'))
            
        except Exception as e:
            cursor.close()
            conn.close()
            return render_template(
                'add.html',
                title='Favorite Track',
                subtitle='Search and add a track to your favorites',
                fields=_get_track_fields(),
                cancel_url=url_for('favorites.list_favorite_tracks'),
                error_message=f"Error adding favorite: {str(e)}"
            )

    return render_template(
        'add.html',
        title='Favorite Track',
        subtitle='Search and add a track to your favorites',
        fields=_get_track_fields(),
        cancel_url=url_for('favorites.list_favorite_tracks')
    )


@favorites_bp.route('/artists/add', methods=['GET', 'POST'])
@login_required
def add_favorite_artist():
    user_id = session.get('user_id')
    if not user_id:
        flash("User session not found.", "error")
        return redirect(url_for('login'))

    if request.method == 'POST':
        artist_id = request.form.get('artist_id')
        
        if not artist_id:
            return render_template(
                'add.html',
                title='Favorite Artist',
                subtitle='Search and add an artist to your favorites',
                fields=_get_artist_fields(),
                cancel_url=url_for('favorites.list_favorite_artists'),
                error_message="Please select an artist."
            )

        conn = get_db_connection()
        if conn is None:
            flash("Database connection failed.", "error")
            return redirect(url_for('favorites.list_favorite_artists'))

        cursor = conn.cursor()
        
        try:
            # Check if already exists
            cursor.execute(
                "SELECT 1 FROM UserFavoriteArtists WHERE user_id = %s AND artist_id = %s",
                (user_id, artist_id)
            )
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return render_template(
                    'add.html',
                    title='Favorite Artist',
                    subtitle='Search and add an artist to your favorites',
                    fields=_get_artist_fields(),
                    cancel_url=url_for('favorites.list_favorite_artists'),
                    error_message="This artist is already in your favorites."
                )
            
            # Insert favorite
            cursor.execute(
                "INSERT INTO UserFavoriteArtists (user_id, artist_id) VALUES (%s, %s)",
                (user_id, artist_id)
            )
            conn.commit()
            cursor.close()
            conn.close()
            
            flash("Artist added to favorites!", "success")
            return redirect(url_for('favorites.list_favorite_artists'))
            
        except Exception as e:
            cursor.close()
            conn.close()
            return render_template(
                'add.html',
                title='Favorite Artist',
                subtitle='Search and add an artist to your favorites',
                fields=_get_artist_fields(),
                cancel_url=url_for('favorites.list_favorite_artists'),
                error_message=f"Error adding favorite: {str(e)}"
            )

    return render_template(
        'add.html',
        title='Favorite Artist',
        subtitle='Search and add an artist to your favorites',
        fields=_get_artist_fields(),
        cancel_url=url_for('favorites.list_favorite_artists')
    )


@favorites_bp.route('/artists/<int:artist_id>/remove', methods=['POST'])
@login_required
def remove_favorite_artist(artist_id):
    user_id = session.get('user_id')
    if not user_id:
        flash("User session not found.", "error")
        return redirect(url_for('login'))

    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "error")
        return redirect(url_for('favorites.list_favorite_artists'))

    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM UserFavoriteArtists WHERE user_id = %s AND artist_id = %s",
        (user_id, artist_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash("Artist removed from favorites.", "info")
    return redirect(url_for('favorites.list_favorite_artists'))


# Complete the list_favorite_artists query
@favorites_bp.route('/artists')
@login_required
def list_favorite_artists():
    user_id = session.get('user_id')
    if not user_id:
        flash("User session not found.", "error")
        return redirect(url_for('login'))

    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "error")
        return redirect(url_for('index'))

    cursor = conn.cursor(dictionary=True)

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page

    # Get total count
    cursor.execute(
        "SELECT COUNT(*) AS total FROM UserFavoriteArtists WHERE user_id = %s",
        (user_id,)
    )
    total_count = cursor.fetchone()['total']
    total_pages = (total_count + per_page - 1) // per_page

    # Get favorite artists with details
    cursor.execute("""
        SELECT ufa.artist_id, ufa.added_at, ar.artist_name, ar.country, ar.artist_popularity
        FROM UserFavoriteArtists ufa
        JOIN Artists ar ON ufa.artist_id = ar.artist_id
        WHERE ufa.user_id = %s
        ORDER BY ufa.added_at DESC
        LIMIT %s OFFSET %s
    """, (user_id, per_page, offset))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'list.html',
        title='My Favorite Artists',
        subtitle='Artists you have added to your favorites',
        columns=['Artist', 'Country', 'Popularity', 'Added'],
        keys=['artist_name', 'country', 'artist_popularity', 'added_at'],
        rows=rows,
        show_actions=True,
        add_url=url_for('favorites.add_favorite_artist'),
        edit_url_builder=None,
        delete_url_builder=lambda row: url_for('favorites.remove_favorite_artist', artist_id=row['artist_id']),
        current_page=page,
        total_pages=total_pages,
        total_count=total_count
    )

# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def _get_track_fields():
    return [
        {
            'name': 'track_id',
            'label': 'Track',
            'type': 'search',
            'required': True,
            'search_url': '/tracks/search',
            'data_key': 'tracks',
            'id_field': 'track_id',
            'name_field': 'track_name',
            'secondary_field': 'artist_name',
            'placeholder': 'Search for a track...'
        }
    ]


def _get_artist_fields():
    return [
        {
            'name': 'artist_id',
            'label': 'Artist',
            'type': 'search',
            'required': True,
            'search_url': '/artists/search',
            'data_key': 'artists',
            'id_field': 'artist_id',
            'name_field': 'artist_name',
            'secondary_field': 'country',
            'placeholder': 'Search for an artist...'
        }
    ]