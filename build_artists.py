import pandas as pd
import os
import math
from collections import Counter

# ------------------- CONFIG -------------------

DATASET_PATH = os.path.join("dataset_csv", "dataset.csv")
GENRES_PATH = os.path.join("dataset_csv", "genres.csv")

# Default country for all artists (you can change this to "Unknown" or anything)
DEFAULT_COUNTRY = None  # or "Unknown"

# ------------------- HELPERS -------------------


def detect_column(possible_names, df, what):
    """
    Try to find the first existing column in df from a list of possible names.
    Raise a clear error if none is found.
    """
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
    """
    Take the first artist from a field that might contain multiple artists
    separated by comma, semicolon, ampersand, 'feat', etc.
    """
    if not isinstance(name, str):
        return None
    s = name.strip()
    if not s:
        return None

    # Common separators
    separators = [";", ",", "&", " feat.", " ft.", " featuring "]
    for sep in separators:
        if sep in s:
            return s.split(sep)[0].strip()

    return s


def normalize_genre(g):
    """
    Normalize genre strings to improve matching between dataset genres
    and Genres.genre_name.
    """
    if not isinstance(g, str):
        return None
    g = g.strip().lower()
    g = g.replace("-", " ")
    g = g.replace("_", " ")
    g = " ".join(g.split())  # collapse multiple spaces
    return g or None


# ------------------- MAIN LOGIC -------------------


def main():
    # 1) Load dataset
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"dataset.csv not found at {DATASET_PATH}")

    print(f"[INFO] Loading tracks dataset from {DATASET_PATH} ...")
    df = pd.read_csv(DATASET_PATH)

    # 2) Automatically detect relevant columns
    artist_col = detect_column(
        ["artists", "artist_name", "track_artist"],
        df,
        "artist name",
    )

    popularity_col = detect_column(
        ["popularity", "track_popularity"],
        df,
        "popularity",
    )

    genre_col = detect_column(
        ["track_genre", "playlist_genre", "playlist_subgenre"],
        df,
        "genre",
    )

    # 3) Clean basic columns
    df["artist_name"] = df[artist_col].apply(first_artist)
    df["artist_popularity_raw"] = df[popularity_col]
    df["genre_raw"] = df[genre_col].astype(str)

    # Drop rows without an artist name
    df = df.dropna(subset=["artist_name"])

    # 4) Group by artist: max popularity + most frequent genre
    grouped = []
    for artist, g in df.groupby("artist_name"):
        # Popularity: max of all tracks for that artist
        try:
            max_pop = g["artist_popularity_raw"].max()
            max_pop = int(max_pop) if not (isinstance(max_pop, float) and math.isnan(max_pop)) else None
        except Exception:
            max_pop = None

        # Genre: most frequent genre_raw
        genre_counts = Counter(g["genre_raw"])
        main_genre = genre_counts.most_common(1)[0][0] if genre_counts else None

        grouped.append((artist, max_pop, main_genre))

    artists_df = pd.DataFrame(
        grouped,
        columns=["artist_name", "artist_popularity", "main_genre_original"],
    )

    print(f"[INFO] Found {len(artists_df)} unique artists.")

    # 5) Load Genres table from CSV
    if not os.path.exists(GENRES_PATH):
        raise FileNotFoundError(f"genres.csv not found at {GENRES_PATH}")

    print(f"[INFO] Loading genres from {GENRES_PATH} ...")
    genres = pd.read_csv(GENRES_PATH)
    
   # Your genres.csv uses:
    # parent_genre, genre, short_description, genre_id
    genre_id_col = "genre_id"
    genre_name_col = "genre"   # THIS is the genre name

    # Normalize genre names in both tables
    artists_df["main_genre_norm"] = artists_df["main_genre_original"].apply(normalize_genre)
    genres["genre_name_norm"] = genres[genre_name_col].apply(normalize_genre)

    # 6) Join on normalized genre name
    merged = artists_df.merge(
        genres[[genre_id_col, "genre_name_norm"]],
        how="left",
        left_on="main_genre_norm",
        right_on="genre_name_norm",
    )

    # Split matched vs unmatched
    matched = merged[merged[genre_id_col].notna()].copy()
    unmatched = merged[merged[genre_id_col].isna()].copy()

    print(f"[INFO] Matched genres for {len(matched)} artists.")
    print(f"[INFO] Unmatched genres for {len(unmatched)} artists.")

    # 7) Build final artists.csv (only matched rows)
    matched = matched.sort_values("artist_name").reset_index(drop=True)
    matched.insert(0, "artist_id", range(1, len(matched) + 1))
    matched["country"] = DEFAULT_COUNTRY

    artists_final = matched[["artist_id",
                             "artist_name",
                             "artist_popularity",
                             "country",
                             genre_id_col]].rename(columns={genre_id_col: "genre_id"})

    # Save artists.csv
    out_dir = os.path.dirname(DATASET_PATH)
    artists_csv_path = os.path.join(out_dir, "artists.csv")
    artists_final.to_csv(artists_csv_path, index=False)
    print(f"[SUCCESS] Saved {len(artists_final)} artists to {artists_csv_path}")

    # 8) Save unmatched genres for manual fixing
    if len(unmatched) > 0:
        unmatched_path = os.path.join(out_dir, "artists_unmapped_genres.csv")
        unmatched[["artist_name",
                   "artist_popularity",
                   "main_genre_original"]].to_csv(unmatched_path, index=False)
        print(f"[WARN] Saved {len(unmatched)} artists with UNMATCHED genres to {unmatched_path}")
        print("       You or your teammate should review this file and either:")
        print("       - adjust genres.csv names, or")
        print("       - manually edit artists.csv for those artists.")
    else:
        print("[INFO] All artist genres were successfully matched to genre_id.")


if __name__ == "__main__":
    main()