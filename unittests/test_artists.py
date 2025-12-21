import pytest


def seed_basic_data(db_connection):
    """
    Helper function to insert common test data.
    """
    cursor = db_connection.cursor()

    # Genres
    cursor.execute("""
        INSERT INTO Genres (genre_id, genre_name)
        VALUES
        (1, 'Pop'),
        (2, 'Rock'),
        (3, 'Jazz');
    """)

    # Artists
    cursor.execute("""
        INSERT INTO Artists (artist_id, artist_name, artist_popularity, country, genre_id)
        VALUES
        (1, 'Pop Artist A', 60, 'USA', 1),
        (2, 'Pop Artist B', 75, 'UK', 1),
        (3, 'Rock Artist', 80, 'USA', 2),
        (4, 'Jazz Artist', 55, 'France', 3),
        (5, 'Unknown Genre Artist', 40, 'Germany', NULL);
    """)

    db_connection.commit()
    cursor.close()


# ---------------------------------------------------
# BASIC PAGE LOAD TEST
# ---------------------------------------------------

def test_artists_page_loads(client, clean_db, db_connection):
    seed_basic_data(db_connection)

    response = client.get("/artists")

    assert response.status_code == 200
    assert b"Pop Artist A" in response.data
    assert b"Rock Artist" in response.data


# ---------------------------------------------------
# ARTIST–GENRE RELATIONSHIP TEST
# ---------------------------------------------------

def test_artist_genre_relationship(clean_db, db_connection):
    seed_basic_data(db_connection)

    cursor = db_connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT a.artist_name, g.genre_name
        FROM Artists a
        LEFT JOIN Genres g ON a.genre_id = g.genre_id
        WHERE a.artist_name = 'Pop Artist A';
    """)

    result = cursor.fetchone()
    cursor.close()

    assert result["genre_name"] == "Pop"


# ---------------------------------------------------
# COMPLEX QUERY: COUNT ARTISTS PER GENRE
# ---------------------------------------------------

def test_artist_count_per_genre(clean_db, db_connection):
    seed_basic_data(db_connection)

    cursor = db_connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT g.genre_name, COUNT(a.artist_id) AS artist_count
        FROM Genres g
        LEFT JOIN Artists a ON g.genre_id = a.genre_id
        GROUP BY g.genre_name;
    """)

    results = cursor.fetchall()
    cursor.close()

    result_map = {row["genre_name"]: row["artist_count"] for row in results}

    assert result_map["Pop"] == 2
    assert result_map["Rock"] == 1
    assert result_map["Jazz"] == 1


# ---------------------------------------------------
# EDGE CASE: ARTIST WITHOUT GENRE
# ---------------------------------------------------

def test_artist_with_null_genre(clean_db, db_connection):
    seed_basic_data(db_connection)

    cursor = db_connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT artist_name
        FROM Artists
        WHERE genre_id IS NULL;
    """)

    result = cursor.fetchone()
    cursor.close()

    assert result["artist_name"] == "Unknown Genre Artist"


# ---------------------------------------------------
# BUSINESS LOGIC: POPULARITY ORDERING
# ---------------------------------------------------

def test_artist_popularity_order(clean_db, db_connection):
    seed_basic_data(db_connection)

    cursor = db_connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT artist_name, artist_popularity
        FROM Artists
        ORDER BY artist_popularity DESC;
    """)

    results = cursor.fetchall()
    cursor.close()

    assert results[0]["artist_name"] == "Rock Artist"
    assert results[0]["artist_popularity"] == 80


# ---------------------------------------------------
# FILTERING: ARTISTS BY COUNTRY
# ---------------------------------------------------

def test_artists_by_country(clean_db, db_connection):
    seed_basic_data(db_connection)

    cursor = db_connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM Artists
        WHERE country = 'USA';
    """)

    result = cursor.fetchone()
    cursor.close()

    assert result["total"] == 2
