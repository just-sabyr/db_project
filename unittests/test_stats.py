def test_stats_counts(client, clean_db, db_connection):
    cursor = db_connection.cursor()

    cursor.execute("""
        INSERT INTO Genres (genre_id, genre_name)
        VALUES (1, 'Pop');
    """)

    cursor.execute("""
        INSERT INTO Artists (artist_id, artist_name, artist_popularity, country, genre_id)
        VALUES
        (1, 'Artist A', 60, 'USA', 1),
        (2, 'Artist B', 40, 'UK', 1);
    """)

    cursor.execute("""
        INSERT INTO Albums (album_id, album_name, release_year, artist_id, genre_id)
        VALUES
        (1, 'Album A', 2020, 1, 1);
    """)

    cursor.execute("""
        INSERT INTO Tracks (track_id, track_name, album_id, artist_id, genre_id, duration, explicit, popularity)
        VALUES
        (1, 'Track A', 1, 1, 1, 180, 0, 55);
    """)

    db_connection.commit()
    cursor.close()

    response = client.get("/stats")

    assert response.status_code == 200
