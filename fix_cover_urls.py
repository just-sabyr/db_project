import csv
import requests
from urllib.parse import quote
import time

# -------- CONFIG --------
INPUT = "dataset_csv/albums.csv"
OUTPUT = "dataset_csv/albums_fixed.csv"

MAX_REAL_COVERS = 5000

PLACEHOLDER = "https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg"

print(">>> fix_cover_urls.py started")

# -------- FUNCTION --------
def get_wiki_cover(album_name):
    try:
        page_title = quote(album_name.replace(" ", "_"))
        url = f"https://en.wikipedia.org/wiki/{page_title}"

        response = requests.get(url, timeout=6)
        if response.status_code != 200:
            return PLACEHOLDER

        html = response.text

        for line in html.splitlines():
            if "upload.wikimedia.org" in line and ("jpg" in line or "png" in line):
                start = line.find("https://upload.wikimedia.org")
                end = line.find('"', start)
                if end > start:
                    return line[start:end]

    except Exception:
        return PLACEHOLDER

    return PLACEHOLDER


# -------- MAIN --------
with open(INPUT, newline="", encoding="utf-8") as fin, \
     open(OUTPUT, "w", newline="", encoding="utf-8") as fout:

    reader = csv.DictReader(fin)
    writer = csv.DictWriter(fout, fieldnames=reader.fieldnames)
    writer.writeheader()

    for i, row in enumerate(reader, start=1):

        if i <= MAX_REAL_COVERS:
            row["cover_url"] = get_wiki_cover(row["album_name"])
            time.sleep(0.05)  # polite delay
        else:
            row["cover_url"] = PLACEHOLDER

        writer.writerow(row)

        if i % 100 == 0:
            print(f"Processed {i} albums...")

print(f"✅ DONE: albums_fixed.csv created (real covers for first {MAX_REAL_COVERS})")
