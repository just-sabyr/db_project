"""
buildalbum.py

Generates Albums table entries from dataset.csv using MySQL.
Albums are derived from track-level data to ensure referential integrity.

Pipeline:
dataset.csv
 → resolve artist_id, genre_id
 → deduplicate (artist_id, album_name)
 → insert into Albums
 → export Albums to CSV (inspection only)

Author: Ildi
"""

import csv
import mysql.connector
from pathlib import Path
from dotenv import load_dotenv
import os

# -------------------- ENV --------------------
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "auth_plugin": "mysql_native_password"
}

# -------------------- PATHS --------------------
BASE_DIR = Path(__file__).parent
DATASET_PATH = BASE_DIR / "dataset_csv" / "dataset.csv"
ARTISTS_PATH = BASE_DIR / "dataset_csv" / "artists.csv"
GENRES_PATH = BASE_DIR / "dataset_csv" / "genres.csv"
OUTPUT_PATH = BASE_DIR / "albums_output.csv"

# -------------------- HELPERS --------------------
def normalize(s):
    if not s:
        return None
    s = s.strip().lower()
    s = s.replace("-", " ").replace("_", " ")
    return " ".join(s.split())

def parse_year(y):
    try:
        return int(float(y))
    except:
        return None

# -------------------- LOADERS --------------------
def load_dataset():
    with open(DATASET_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def load_lookup(path, id_col, name_col):
    lookup = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            name = normalize(r[name_col])
            if name:
                lookup[name] = int(r[id_col])
    return lookup

# -------------------- DB --------------------
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# -------------------- INSERT LOGIC --------------------
def insert_albums(rows):
    conn = get_connection()
    cur = conn.cursor()

    artists = load_lookup(ARTISTS_PATH, "artist_id", "artist_name")
    genres = load_lookup(GENRES_PATH, "genre_id", "genre")

    insert_sql = """
        INSERT IGNORE INTO Albums
        (artist_id, genre_id, album_name, release_year, cover_url)
        VALUES (%s, %s, %s, %s, %s);
    """

    seen = set()
    inserted = 0
    skipped = 0

    for r in rows:
        artist_name = normalize(r.get("artists") or r.get("artist_name"))
        album_name = r.get("album_name")
        genre_name = normalize(r.get("track_genre"))
        release_year = parse_year(r.get("release_year"))

        if not artist_name or not album_name or not genre_name:
            skipped += 1
            continue

        artist_id = artists.get(artist_name)
        genre_id = genres.get(genre_name)

        if artist_id is None or genre_id is None:
            skipped += 1
            continue

        key = (artist_id, album_name)
        if key in seen:
            continue
        seen.add(key)

        cur.execute(
            insert_sql,
            (artist_id, genre_id, album_name, release_year, None)
        )

        if cur.rowcount > 0:
            inserted += 1

    conn.commit()
    conn.close()

    print(f"[ALBUMS] Inserted: {inserted}")
    print(f"[ALBUMS] Skipped: {skipped}")

# -------------------- EXPORT --------------------
def export_albums():
    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT
            a.album_id,
            a.album_name,
            ar.artist_name,
            g.genre,
            a.release_year,
            a.cover_url
        FROM Albums a
        JOIN Artists ar ON a.artist_id = ar.artist_id
        JOIN Genres g ON a.genre_id = g.genre_id
        ORDER BY ar.artist_name, a.album_name;
    """

    cur.execute(query)
    rows = cur.fetchall()
    headers = [desc[0] for desc in cur.description]

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    conn.close()
    print(f"[EXPORT] Albums written to {OUTPUT_PATH}")

# -------------------- MAIN --------------------
def main():
    if not DATASET_PATH.exists():
        raise FileNotFoundError("dataset.csv not found")

    rows = load_dataset()
    insert_albums(rows)
    export_albums()
    print("[DONE] Albums generated successfully")

if __name__ == "__main__":
    main()
