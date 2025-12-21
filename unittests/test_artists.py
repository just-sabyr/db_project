def test_artists_page_loads(client, clean_db, db_connection):
    cursor = db_connection.cursor()

    cursor.execute("""
        INSERT INTO Genres (genre_id, genre_name)
        VALUES (1, 'Pop');
    """)

    cursor.execute("""
        INSERT INTO Artists (artist_id, artist_name, artist_popularity, country, genre_id)
        VALUES
        (1, 'Test Artist 1', 50, 'USA', 1),
        (2, 'Test Artist 2', 70, 'UK', 1);
    """)

    db_connection.commit()
    cursor.close()

    response = client.get("/artists")

    assert response.status_code == 200
    assert b"Test Artist 1" in response.data
    assert b"Test Artist 2" in response.data


def test_artist_genre_relationship(clean_db, db_connection):
    cursor = db_connection.cursor(dictionary=True)

    cursor.execute("""
        INSERT INTO Genres (genre_id, genre_name)
        VALUES
        (1, 'Pop'),
        (2, 'Rock');
    """)

    cursor.execute("""
        INSERT INTO Artists (artist_id, artist_name, artist_popularity, country, genre_id)
        VALUES
        (1, 'Pop Artist', 60, 'USA', 1),
        (2, 'Rock Artist', 80, 'UK', 2),
        (3, 'Another Pop Artist', 70, 'USA', 1);
    """)

    db_connection.commit()

    cursor.execute("""
        SELECT g.genre_name, COUNT(a.artist_id) AS total_artists
        FROM Artists a
        JOIN Genres g ON a.genre_id = g.genre_id
        GROUP BY g.genre_name;
    """)

    results = cursor.fetchall()
    cursor.close()

    result_map = {row["genre_name"]: row["total_artists"] for row in results}

    assert result_map["Pop"] == 2
    assert result_map["Rock"] == 1


def test_artist_without_genre(clean_db, db_connection):
    cursor = db_connection.cursor(dictionary=True)

    cursor.execute("""
        INSERT INTO Artists (artist_id, artist_name, artist_popularity, country, genre_id)
        VALUES (1, 'Genreless Artist', 40, 'USA', NULL);
    """)

    db_connection.commit()

    cursor.execute("""
        SELECT * FROM Artists WHERE genre_id IS NULL;
    """)

    artist = cursor.fetchone()
    cursor.close()

    assert artist["artist_name"] == "Genreless Artist"


def test_duplicate_artist_name_rejected(clean_db, db_connection):
    cursor = db_connection.cursor()

    cursor.execute("""
        INSERT INTO Artists (artist_id, artist_name, artist_popularity, country)
        VALUES (1, 'Unique Artist', 50, 'USA');
    """)

    db_connection.commit()

    import pytest
    with pytest.raises(Exception):
        cursor.execute("""
            INSERT INTO Artists (artist_id, artist_name, artist_popularity, country)
            VALUES (2, 'Unique Artist', 60, 'UK');
        """)
        db_connection.commit()

    cursor.close()


def test_average_popularity_per_genre(clean_db, db_connection):
    cursor = db_connection.cursor(dictionary=True)

    cursor.execute("""
        INSERT INTO Genres (genre_id, genre_name)
        VALUES (1, 'Pop');
    """)

    cursor.execute("""
        INSERT INTO Artists (artist_id, artist_name, artist_popularity, country, genre_id)
        VALUES
        (1, 'Pop A', 40, 'USA', 1),
        (2, 'Pop B', 60, 'UK', 1);
    """)

    db_connection.commit()

    cursor.execute("""
        SELECT g.genre_name, AVG(a.artist_popularity) AS avg_popularity
        FROM Artists a
        JOIN Genres g ON a.genre_id = g.genre_id
        GROUP BY g.genre_name;
    """)

    result = cursor.fetchone()
    cursor.close()

    assert result["genre_name"] == "Pop"
    assert int(result["avg_popularity"]) == 50
