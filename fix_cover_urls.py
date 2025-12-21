import csv
import requests
import time

# -------- CONFIG --------
LASTFM_API_KEY = "42ed9d70c3843a8f6b2ea6242b9c1e1e"

INPUT = "dataset_csv/albums.csv"
OUTPUT = "dataset_csv/albums.csv"   # overwrite
MAX_ALBUMS = 100                    # FREE + safe

PLACEHOLDER = "https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg"

LASTFM_ENDPOINT = "https://ws.audioscrobbler.com/2.0/"

# -------- FUNCTION --------
def get_album_cover(album_name, artist_name=None):
    params = {
        "method": "album.search",
        "album": album_name,
        "api_key": LASTFM_API_KEY,
        "format": "json",
        "limit": 1
    }

    try:
        r = requests.get(LASTFM_ENDPOINT, params=params, timeout=5)
        data = r.json()

        albums = data.get("results", {}).get("albummatches", {}).get("album", [])

        if albums:
            images = albums[0].get("image", [])
            for img in reversed(images):  # get largest available
                if img.get("#text"):
                    return img["#text"]

    except Exception:
        pass

    return PLACEHOLDER


# -------- MAIN --------
print(">>> Last.fm cover fetch started")

rows = []

with open(INPUT, newline="", encoding="utf-8") as fin:
    reader = csv.DictReader(fin)
    fieldnames = reader.fieldnames

    for i, row in enumerate(reader, start=1):
        if i <= MAX_ALBUMS:
            row["cover_url"] = get_album_cover(row["album_name"])
            time.sleep(0.2)  # polite delay
        else:
            row["cover_url"] = PLACEHOLDER

        rows.append(row)

        print(f"Processed {i} albums")

with open(OUTPUT, "w", newline="", encoding="utf-8") as fout:
    writer = csv.DictWriter(fout, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"✅ DONE — covers fetched for first {MAX_ALBUMS} albums")
