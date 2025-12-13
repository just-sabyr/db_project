import pandas as pd
import os
import math
from collections import Counter

# ------------------- CONFIG -------------------

DATASET_PATH = os.path.join("dataset_csv", "dataset.csv")
GENRES_PATH = os.path.join("dataset_csv", "genres.csv")

# ------------------- HELPERS -------------------

def detect_column(possible_names, df, what):
    for name in possible_names:
        if name in df.columns:
            print(f"[INFO] Using column '{name}' for {what}.")
            return name
    raise ValueError(
        f"Could not find any column for {what}. "
        f"Tried: {possible_names}\n"
        f"Available columns: {list(df.columns)}"
    )


def first_artist(name):
    if not isinstance(name, str):
        return None
    s = name.strip()
    if not s:
        return None

    separators = [";", ",", "&", " feat.", " ft.", " featuring "]
    for sep in separators:
        if sep in s:
            return s.split(sep)[0].strip()

    return s


def normalize_genre(g):
    if not isinstance(g, str):
        return None
    g = g.strip().lower()
    g = g.replace("-", " ").replace("_", " ")
    g = " ".join(g.split())
    return g or None


def normalize_artist_name(name):
    if not isinstance(name, str):
        return None
    return name.strip().lower()


# -------- COUNTRY INFERENCE (NEW PART) --------

def infer_country(artist_name, genre_name):
    name = artist_name.lower() if isinstance(artist_name, str) else ""
    genre = genre_name.lower() if isinstance(genre_name, str) else ""

    # Genre-based rules
    if "k-pop" in genre or "korean" in genre:
        return "South Korea"
    if "j-pop" in genre or "anime" in genre:
        return "Japan"
    if "latin" in genre or "reggaeton" in genre:
        return "Puerto Rico"
    if "afrobeats" in genre:
        return "Nigeria"

    # Name-based heuristics
    korean = ["kim", "park", "lee", "jung", "choi"]
    japanese = ["yuki", "hiro", "sato", "tanaka"]
    spanish = ["juan", "jose", "carlos", "luis", "ángel"]

    if any(k in name for k in korean):
        return "South Korea"
    if any(j in name for j in japanese):
        return "Japan"
    if any(s in name for s in spanish):
        return "Latin America"

    return "Unknown"


# ------------------- MAIN LOGIC -------------------

def main():
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"dataset.csv not found at {DATASET_PATH}")

    print(f"[INFO] Loading dataset from {DATASET_PATH}")
    df = pd.read_csv(DATASET_PATH)

    artist_col = detect_column(["artists"], df, "artist name")
    popularity_col = detect_column(["popularity"], df, "popularity")
    genre_col = detect_column(
        ["track_genre", "playlist_genre", "playlist_subgenre"],
        df,
        "genre"
    )

    df["artist_name_raw"] = df[artist_col].apply(first_artist)
    df["artist_name_norm"] = df["artist_name_raw"].apply(normalize_artist_name)
    df["artist_popularity_raw"] = df[popularity_col]
    df["genre_raw"] = df[genre_col].astype(str)

    df = df.dropna(subset=["artist_name_norm"])

    grouped = []
    for artist_norm, g in df.groupby("artist_name_norm"):
        original_name = g["artist_name_raw"].mode()[0]

        max_pop = g["artist_popularity_raw"].max()
        max_pop = int(max_pop) if not pd.isna(max_pop) else None

        main_genre = Counter(g["genre_raw"]).most_common(1)[0][0]
        grouped.append((original_name, max_pop, main_genre))

    artists_df = pd.DataFrame(
        grouped,
        columns=["artist_name", "artist_popularity", "main_genre_original"]
    )

    print(f"[INFO] Found {len(artists_df)} unique artists")

    genres = pd.read_csv(GENRES_PATH)
    genres["genre_name_norm"] = genres["genre"].apply(normalize_genre)
    artists_df["main_genre_norm"] = artists_df["main_genre_original"].apply(normalize_genre)

    merged = artists_df.merge(
        genres[["genre_id", "genre_name_norm"]],
        how="left",
        left_on="main_genre_norm",
        right_on="genre_name_norm"
    )

    matched = merged[merged["genre_id"].notna()].copy()

    matched = matched.sort_values("artist_name").reset_index(drop=True)
    matched.insert(0, "artist_id", range(1, len(matched) + 1))

    # -------- APPLY COUNTRY INFERENCE --------
    matched["country"] = matched.apply(
        lambda row: infer_country(row["artist_name"], row["main_genre_original"]),
        axis=1
    )

    artists_final = matched[
        ["artist_id", "artist_name", "artist_popularity", "country", "genre_id"]
    ]

    out_path = os.path.join("dataset_csv", "artists.csv")
    artists_final.to_csv(out_path, index=False)

    print(f"[SUCCESS] artists.csv rebuilt correctly with {len(artists_final)} artists.")
    print("[INFO] genre_id assigned using first genre per artist.")
    print("[INFO] country filled for known artists, others set to 'Unknown'.")


if __name__ == "__main__":
    main()
