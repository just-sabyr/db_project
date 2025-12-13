import pandas as pd
import os
from collections import Counter

# ------------------- CONFIG -------------------

DATASET_PATH = os.path.join("dataset_csv", "dataset.csv")
GENRES_PATH = os.path.join("dataset_csv", "genres.csv")
OUTPUT_PATH = os.path.join("dataset_csv", "artists.csv")

# ------------------- HELPERS -------------------

def first_artist(name):
    if not isinstance(name, str):
        return None
    name = name.strip()
    if not name:
        return None
    for sep in [";", ",", "&", " feat.", " ft.", " featuring "]:
        if sep in name:
            return name.split(sep)[0].strip()
    return name


def normalize_genre(g):
    if not isinstance(g, str):
        return None
    g = g.lower().replace("-", " ").replace("_", " ")
    return " ".join(g.split())


# ------------------- COUNTRY INFERENCE -------------------

def infer_country(artist_name, genre_name):
    name = artist_name.lower() if isinstance(artist_name, str) else ""
    genre = genre_name.lower() if isinstance(genre_name, str) else ""

    # ---- Genre based (strongest signal) ----
    if any(k in genre for k in ["k-pop", "korean"]):
        return "South Korea"
    if any(k in genre for k in ["j-pop", "anime", "japanese"]):
        return "Japan"
    if any(k in genre for k in ["mandopop", "cantopop", "c-pop"]):
        return "China"
    if any(k in genre for k in ["desi", "bollywood", "indian"]):
        return "India"
    if any(k in genre for k in ["latin", "reggaeton", "salsa", "bachata", "cumbia"]):
        return "Latin America"
    if any(k in genre for k in ["afrobeats", "afrobeat", "afro pop", "afro"]):
        return "Nigeria"
    if any(k in genre for k in ["britpop", "uk garage", "grime"]):
        return "UK"
    if any(k in genre for k in ["french pop", "chanson"]):
        return "France"
    if any(k in genre for k in ["german techno", "german pop"]):
        return "Germany"
    if any(k in genre for k in ["russian", "hardbass", "phonk"]):
        return "Russia"
    if any(k in genre for k in ["arab", "arabic", "middle eastern"]):
        return "Middle East"

    # ---- Name based heuristics ----
    if any(k in name for k in ["kim ", "park ", "lee ", "choi ", "jung ", "seo "]):
        return "South Korea"
    if any(k in name for k in ["yuki", "hiro", "sato", "tanaka", "akira", "takashi"]):
        return "Japan"
    if any(k in name for k in ["juan", "jose", "carlos", "miguel", "luis", "ángel", "alejandro"]):
        return "Latin America"
    if any(k in name for k in ["mohamed", "muhammad", "ali", "ahmed", "hassan", "abdul"]):
        return "Middle East"
    if any(k in name for k in ["ivan", "dmitri", "nikita", "sergey", "alexei"]):
        return "Eastern Europe"

    # ---- Language / accent clues ----
    if any(ch in name for ch in ["á", "é", "í", "ó", "ú", "ñ", "ã", "ç"]):
        return "Latin America"

    # ---- Genre fallback ----
    if any(k in genre for k in ["techno", "house", "edm", "trance"]):
        return "Europe"
    if any(k in genre for k in ["hip hop", "rap", "trap"]):
        return "USA"

    return "Unknown"


# ------------------- MAIN LOGIC -------------------

def main():
    # Load dataset
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError("dataset.csv not found")

    df = pd.read_csv(DATASET_PATH)

    # Load genres
    if not os.path.exists(GENRES_PATH):
        raise FileNotFoundError("genres.csv not found")

    genres_df = pd.read_csv(GENRES_PATH)
    genres_df["genre_norm"] = genres_df["genre"].apply(normalize_genre)

    genre_map = dict(zip(genres_df["genre_norm"], genres_df["genre_id"]))

    # Extract artist and genre
    df["artist_name"] = df["artists"].apply(first_artist)

    if "track_genre" in df.columns:
        df["genre_name"] = df["track_genre"]
    elif "playlist_genre" in df.columns:
        df["genre_name"] = df["playlist_genre"]
    else:
        df["genre_name"] = None

    df["genre_norm"] = df["genre_name"].apply(normalize_genre)

    df = df.dropna(subset=["artist_name"])

    # Group by artist
    grouped = []
    for artist, g in df.groupby("artist_name"):
        max_pop = g["popularity"].max()
        main_genre = Counter(g["genre_norm"]).most_common(1)[0][0]
        grouped.append((artist, int(max_pop), main_genre))

    artists_df = pd.DataFrame(
        grouped,
        columns=["artist_name", "artist_popularity", "main_genre"]
    )

    # Map genre_id
    artists_df["genre_id"] = artists_df["main_genre"].map(genre_map)

    # Infer country
    artists_df["country"] = artists_df.apply(
        lambda r: infer_country(r["artist_name"], r["main_genre"]),
        axis=1
    )

    # Create artist_id
    artists_df.insert(0, "artist_id", range(1, len(artists_df) + 1))

    # Final columns
    artists_df = artists_df[
        ["artist_id", "artist_name", "artist_popularity", "country", "genre_id"]
    ]

    # Save
    artists_df.to_csv(OUTPUT_PATH, index=False)

    print(f"[SUCCESS] artists.csv rebuilt with {len(artists_df)} artists.")
    print("[INFO] genre_id assigned using first genre per artist.")
    print("[INFO] country inferred using genre + name heuristics.")


if __name__ == "__main__":
    main()
