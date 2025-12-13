import pandas as pd
import os

# ------------------- CONFIG -------------------

DATASET_PATH = os.path.join("dataset_csv", "dataset.csv")
GENRES_PATH = os.path.join("dataset_csv", "genres.csv")
OUTPUT_PATH = os.path.join("dataset_csv", "artists.csv")

# Some known artists and their countries (manual, limited, safe)
ARTIST_COUNTRIES = {
    "Taylor Swift": "USA",
    "Drake": "Canada",
    "Ed Sheeran": "UK",
    "Ariana Grande": "USA",
    "The Weeknd": "Canada",
    "Bad Bunny": "Puerto Rico",
    "BTS": "South Korea",
    "BLACKPINK": "South Korea",
    "Kanye West": "USA",
    "Eminem": "USA",
}

# ------------------- MAIN LOGIC -------------------

def main():
    # Load dataset.csv
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"dataset.csv not found at {DATASET_PATH}")

    df = pd.read_csv(DATASET_PATH)

    # Load genres.csv (genre name -> genre_id)
    if not os.path.exists(GENRES_PATH):
        raise FileNotFoundError(f"genres.csv not found at {GENRES_PATH}")

    genres_df = pd.read_csv(GENRES_PATH)

    # Build genre name -> genre_id mapping
    genre_map = {
        str(row["genre"]).strip().lower(): int(row["genre_id"])
        for _, row in genres_df.iterrows()
    }

    # Extract artist name
    # Multiple artists separated by ';' -> keep only the first
    df["artist_name"] = (
        df["artists"]
        .astype(str)
        .str.split(";")
        .str[0]
        .str.strip()
    )

    # Extract genre name (take the first available genre column)
    if "track_genre" in df.columns:
        df["artist_genre"] = df["track_genre"]
    elif "playlist_genre" in df.columns:
        df["artist_genre"] = df["playlist_genre"]
    else:
        df["artist_genre"] = None

    # Keep relevant columns only
    artists_df = df[["artist_name", "popularity", "artist_genre"]].dropna(
        subset=["artist_name"]
    )

    # One row per artist
    artists_df = (
        artists_df
        .groupby("artist_name", as_index=False)
        .agg({
            "popularity": "max",        # max popularity per artist
            "artist_genre": "first"     # first genre per artist (as requested)
        })
    )

    # Map genre name -> genre_id
    def map_genre_id(genre_name):
        if not isinstance(genre_name, str):
            return None
        return genre_map.get(genre_name.strip().lower())

    artists_df["genre_id"] = artists_df["artist_genre"].apply(map_genre_id)

    # Assign country (only for some artists, rest Unknown)
    def get_country(artist_name):
        return ARTIST_COUNTRIES.get(artist_name, "Unknown")

    artists_df["country"] = artists_df["artist_name"].apply(get_country)

    # Create artist_id
    artists_df.insert(0, "artist_id", range(1, len(artists_df) + 1))

    # Final column order
    artists_df = artists_df[[
        "artist_id",
        "artist_name",
        "popularity",
        "country",
        "genre_id"
    ]].rename(columns={
        "popularity": "artist_popularity"
    })

    # Save artists.csv
    artists_df.to_csv(OUTPUT_PATH, index=False)

    print(f"[SUCCESS] artists.csv rebuilt with {len(artists_df)} artists.")
    print("[INFO] genre_id assigned using first genre per artist.")
    print("[INFO] country filled for known artists, others set to 'Unknown'.")


if __name__ == "__main__":
    main()
