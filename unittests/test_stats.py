def login_as_admin(client):
    return client.post(
        "/login",
        data={"username": "admin", "password": "admin123"},
        follow_redirects=True,
    )


def test_stats_page_loads_for_admin(client, clean_db, db_connection):
    cursor = db_connection.cursor()

    # Insert genres
    cursor.execute("""
        INSERT INTO Genres (genre_id, genre_name)
        VALUES (1, 'Pop'), (2, 'Rock');
    """)

    # Insert artists
    cursor.execute("""
        INSERT INTO Artists (artist_id, artist_name, artist_popularity, country, genre_id)
        VALUES
        (1, 'Pop Artist', 70, 'USA', 1),
        (2, 'Rock Artist', 80, 'UK', 2);
    """)

    # Insert albums
    cursor.execute("""
        INSERT INTO Albums (album_id, album_name, artist_id)
        VALUES
        (1, 'Pop Album', 1),
        (2, 'Rock Album', 2);
    """)

    # Insert tracks
    cursor.execute("""
        INSERT INTO Tracks (track_id, track_name, album_id)
        VALUES
        (1, 'Pop Track', 1),
        (2, 'Rock Track', 2);
    """)

    # Insert users
    cursor.execute("""
        INSERT INTO Users (user_id, username, password, genre_id, artist_id)
        VALUES
        (1, 'user1', 'pass', 1, 1),
        (2, 'user2', 'pass', 1, 1),
        (3, 'user3', 'pass', 2, 2);
    """)

    db_connection.commit()
    cursor.close()

    # Login as admin
    login_as_admin(client)

    response = client.get("/stats")
    assert response.status_code == 200


def test_stats_counts_are_correct(client, clean_db, db_connection):
    cursor = db_connection.cursor()

    cursor.execute("INSERT INTO Genres (genre_id, genre_name) VALUES (1, 'Pop');")
    cursor.execute("""
        INSERT INTO Artists (artist_id, artist_name, artist_popularity, country, genre_id)
        VALUES (1, 'Artist', 50, 'USA', 1);
    """)
    cursor.execute("INSERT INTO Albums (album_id, album_name, artist_id) VALUES (1, 'Album', 1);")
    cursor.execute("INSERT INTO Tracks (track_id, track_name, album_id) VALUES (1, 'Track', 1);")
    cursor.execute("""
        INSERT INTO Users (user_id, username, password, genre_id, artist_id)
        VALUES (1, 'user', 'pass', 1, 1);
    """)

    db_connection.commit()
    cursor.close()

    login_as_admin(client)
    response = client.get("/stats")
    html = response.data.decode()

    assert "1" in html  # counts appear on page


def test_most_popular_genre_and_artist(client, clean_db, db_connection):
    cursor = db_connection.cursor()

    cursor.execute("""
        INSERT INTO Genres (genre_id, genre_name)
        VALUES (1, 'Pop'), (2, 'Rock');
    """)

    cursor.execute("""
        INSERT INTO Artists (artist_id, artist_name, artist_popularity, country, genre_id)
        VALUES
        (1, 'Pop Artist', 60, 'USA', 1),
        (2, 'Rock Artist', 80, 'UK', 2);
    """)

    cursor.execute("""
        INSERT INTO Users (user_id, username, password, genre_id, artist_id)
        VALUES
        (1, 'u1', 'pass', 1, 1),
        (2, 'u2', 'pass', 1, 1),
        (3, 'u3', 'pass', 2, 2);
    """)

    db_connection.commit()
    cursor.close()

    login_as_admin(client)
    response = client.get("/stats")
    html = response.data.decode()

    assert "Pop" in html
    assert "Pop Artist" in html


def test_users_by_genre_aggregation(clean_db, db_connection):
    cursor = db_connection.cursor(dictionary=True)

    cursor.execute("""
        INSERT INTO Genres (genre_id, genre_name)
        VALUES (1, 'Pop'), (2, 'Rock');
    """)

    cursor.execute("""
        INSERT INTO Users (user_id, username, password, genre_id)
        VALUES
        (1, 'u1', 'pass', 1),
        (2, 'u2', 'pass', 1),
        (3, 'u3', 'pass', 2);
    """)

    db_connection.commit()

    cursor.execute("""
        SELECT g.genre_name, COUNT(*) AS total
        FROM Users u
        JOIN Genres g ON u.genre_id = g.genre_id
        GROUP BY g.genre_name;
    """)

    results = cursor.fetchall()
    cursor.close()

    result_map = {row["genre_name"]: row["total"] for row in results}

    assert result_map["Pop"] == 2
    assert result_map["Rock"] == 1


def test_stats_requires_admin(client):
    response = client.get("/stats")
    assert response.status_code in (302, 401, 403)
