"""
buildalbum.py

This script processes dataset_csv/dataset.csv and inserts album data into a local SQLite database.
It performs:
- dataset loading
- normalization of artist/genre names
- lookup artist/genre IDs
- validation of album rows
- insertion into Albums table
- export back to CSV

Author: Ildi
"""
import csv
import sqlite3
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATASET_PATH = BASE_DIR / "dataset_csv" / "dataset.csv"
ARTISTS_PATH = BASE_DIR / "dataset_csv" / "artists.csv"
GENRES_PATH = BASE_DIR / "dataset_csv" / "genres.csv"
DB_PATH = BASE_DIR / "albums.db"
OUTPUT_PATH = BASE_DIR / "albums_output.csv"


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS Albums (
    album_id INTEGER PRIMARY KEY,
    artist_id INTEGER,
    genre_id INTEGER,
    album_name TEXT NOT NULL,
    release_year INTEGER,
    cover_url TEXT
);
"""

CREATE_INDEX_SQL = """
CREATE UNIQUE INDEX IF NOT EXISTS idx_album_unique
ON Albums (artist_id, album_name, release_year);
"""

def load_dataset():               """Load the main dataset.csv and return all rows as dictionaries."""
    print(f"Loading dataset from: {DATASET_PATH}")
    rows = []
    with open(DATASET_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def load_lookup(path, id_col, name_col):
    """
    Loads artists.csv or genres.csv into a dictionary.
    Returns: { normalized_name: id }
    """
    table = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            name = r[name_col].strip().lower()
            table[name] = int(r[id_col])
    return table

def normalize(s):          """Normalize strings by lowering case, removing hyphens, and condensing spaces."""
    if not s:
        return None
    s = s.strip().lower()
    s = s.replace("-", " ").replace("_", " ")
    return " ".join(s.split())



def create_database():                 """Create the Albums table + unique index inside albums.db."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    cur.execute(CREATE_TABLE_SQL)
    cur.execute(CREATE_INDEX_SQL)
    conn.commit()
    conn.close()


def insert_data(rows):
    inserted = 0
    skipped = 0
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    artists = load_lookup(ARTISTS_PATH, "artist_id", "artist_name")
    genres = load_lookup(GENRES_PATH, "genre_id", "genre")

    insert_sql = """
    INSERT OR IGNORE INTO Albums
    (artist_id, genre_id, album_name, release_year, cover_url)
    VALUES (?, ?, ?, ?, ?);
    """

    for r in rows:
        artist = normalize(r.get("artists") or r.get("artist_name"))
        genre = normalize(r.get("track_genre"))
        album = r.get("album_name")
        year = r.get("release_year")
        cover = r.get("cover_url")

        artist_id = artists.get(artist)
        genre_id = genres.get(genre)

# Skip albums without valid artist_id
if artist_id is None:
    print(f"[WARN] Skipped album '{album}' — artist '{artist}' not found.")
    skipped += 1
    continue

# Skip empty album names
if not album or album.strip() == "":
    print(f"[WARN] Skipped album with missing album_name.")
    skipped += 1
    continue

    # Normalize empty year
    try:
    year = int(year) if year and year.isdigit() else None
    except:
    year = None
cur.execute(insert_sql, (artist_id, genre_id, album, year, cover))
inserted += 1


    conn.commit()
print(f"[SUMMARY] Inserted: {inserted} | Skipped: {skipped}")
    conn.close()


def export_to_csv():                        """Export the Albums table into albums_output.csv."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

query = """
    SELECT
        a.album_id,
        a.album_name,
        ar.artist_name,
        g.genre AS genre,
        a.release_year,
        a.cover_url
    FROM Albums a
    JOIN Artists ar ON a.artist_id = ar.artist_id
    JOIN Genres g ON a.genre_id = g.genre_id;
    """

       rows = cur.execute(query).fetchall()
        headers = [d[0] for d in cur.description]

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    conn.close()
    print(f"[SUCCESS] Exported albums to {OUTPUT_PATH}")



def main():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Cannot find dataset.csv at {DATASET_PATH}")

    rows = load_dataset()
    create_database()
    insert_data(rows)
    export_to_csv()
    print("[DONE] Albums processing complete.")

if __name__ == "__main__":
    main()
