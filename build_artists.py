import pandas as pd
import os

# ------------------- CONFIG -------------------

DATASET_PATH = os.path.join("dataset_csv", "dataset.csv")
OUTPUT_PATH = os.path.join("dataset_csv", "artists.csv")

# ------------------- MAIN LOGIC -------------------

def main():
    # Load dataset
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"dataset.csv not found at {DATASET_PATH}")

    df = pd.read_csv(DATASET_PATH)

    # Extract artist names
    # dataset.csv already contains an 'artists' column
    # Multiple artists are separated by ';' -> take only the first
    df["artist_name"] = (
        df["artists"]
        .astype(str)
        .str.split(";")
        .str[0]
        .str.strip()
    )

    # Keep only needed columns
    artists_df = df[["artist_name", "popularity"]].dropna()

    # One row per artist, take max popularity
    artists_df = artists_df.groupby(
        "artist_name", as_index=False
    )["popularity"].max()

    # Create final artists table structure
    artists_df.insert(0, "artist_id", range(1, len(artists_df) + 1))
    artists_df["country"] = None
    artists_df["genre_id"] = None

    # Reorder columns to match DB schema
    artists_df = artists_df[
        ["artist_id", "artist_name", "popularity", "country", "genre_id"]
    ].rename(columns={"popularity": "artist_popularity"})

    # Save to CSV
    artists_df.to_csv(OUTPUT_PATH, index=False)

    print(f"[SUCCESS] artists.csv rebuilt correctly with {len(artists_df)} artists.")


if __name__ == "__main__":
    main()
