
"""
buildalbum.py

Builds albums.csv from dataset.csv by resolving artist_id and genre_id
using artists.csv and genres.csv.

Handles multi-artist rows by selecting the FIRST artist.
"""

import csv
from pathlib import Path

# ------------------ Paths ------------------
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "dataset_csv"

DATASET_CSV = DATA_DIR / "dataset.csv"
ARTISTS_CSV = DATA_DIR / "artists.csv"
GENRES_CSV = DATA_DIR / "genres.csv"
OUTPUT_CSV = DATA_DIR / "albums.csv"

# ------------------ Helpers ------------------
def normalize(text):
    return text.strip().lower()

def extract_primary_artist(artists_field):
    """
    Spotify datasets store artists as 'Artist1;Artist2;Artist3'
    We take the first one.
    """
    if not artists_field:
        return ""
    return artists_field.split(";")[0]

# ------------------ Load artists ------------------
artist_lookup = {}
with open(ARTISTS_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        artist_name = normalize(row["artist_name"])
        artist_lookup[artist_name] = {
            "artist_id": row["artist_id"],
            "genre_id": row["genre_id"]
        }

# ------------------ Load genres ------------------
genre_lookup = {}
with open(GENRES_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        genre_lookup[normalize(row["genre"])] = row["genre_id"]

# ------------------ Build albums ------------------
albums_seen = set()
album_id = 1
written = 0
skipped = 0

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as out_f:
    fieldnames = [
    "album_id",
    "album_name",
    "artist_id",
    "genre_id",
    "release_year",
    "cover_url"
]

    writer = csv.DictWriter(out_f, fieldnames=fieldnames)
    writer.writeheader()

    with open(DATASET_CSV, newline="", encoding="utf-8") as data_f:
        reader = csv.DictReader(data_f)

        for row in reader:
            album_name = row.get("album_name", "").strip()
            primary_artist = extract_primary_artist(row.get("artists", ""))
            artist_name = normalize(primary_artist)
            genre_name = normalize(row.get("genre", ""))

            if not album_name or not artist_name:
                skipped += 1
                continue

            if artist_name not in artist_lookup:
                skipped += 1
                continue

            artist_id = artist_lookup[artist_name]["artist_id"]

            # Prefer artist.genre_id, fallback to dataset genre
            genre_id = artist_lookup[artist_name]["genre_id"]
            if not genre_id:
                genre_id = genre_lookup.get(genre_name)

            if not genre_id:
                skipped += 1
                continue

            dedup_key = (album_name.lower(), artist_id)
            if dedup_key in albums_seen:
                continue

            albums_seen.add(dedup_key)

            writer.writerow({
            "album_id": album_id,
            "album_name": album_name,
            "artist_id": artist_id,
            "genre_id": genre_id,
            "release_year": "",
            "cover_url": ""
    })


            album_id += 1
            written += 1

print("\nDONE")
print(f"Albums written: {written}")
print(f"Rows skipped: {skipped}")
print(f"Output -> {OUTPUT_CSV}")
