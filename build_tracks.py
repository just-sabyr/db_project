import pandas as pd

# Load the datasets
dataset = pd.read_csv('dataset_csv/dataset.csv')
albums = pd.read_csv('dataset_csv/albums.csv')
artists = pd.read_csv('dataset_csv/artists.csv')
genres = pd.read_csv('dataset_csv/genres.csv')


# Remove duplicate tracks based on track_id
dataset.drop_duplicates(subset='track_id', keep='first', inplace=True)

# Extract necessary columns for tracks
tracks = dataset[['track_id', 'track_name', 'album_name', 'artists', 'duration_ms', 'explicit', 'popularity']].copy()


# Map album_name to album_id using albums.csv
album_map = albums.set_index('album_name')['album_id'].to_dict()
tracks.loc[:, 'album_id'] = tracks['album_name'].map(album_map)

# Map artists to artist_id using artists.csv
artist_map = artists.set_index('artist_name')['artist_id'].to_dict()
tracks.loc[:, 'artist_id'] = tracks['artists'].map(artist_map)

# Map track_genre to genre_id using genres.csv
genre_map = genres.set_index('genre')['genre_id'].to_dict()
tracks.loc[:, 'genre_id'] = dataset['track_genre'].map(genre_map)

# Rename and transform columns to match the Tracks table schema
tracks.rename(columns={'duration_ms': 'duration'}, inplace=True)
tracks.loc[:, 'duration'] = (tracks['duration'] / 1000).astype(int)  # Convert duration from ms to seconds

# Preprocess the explicit column: Convert True/False to 1/0
tracks.loc[:, 'explicit'] = tracks['explicit'].map({True: 1, False: 0}).fillna(0).astype(int)

# Handle empty artist_id values by replacing NaN with None
tracks.loc[:, 'artist_id'] = tracks['artist_id']

# Select only the required columns and create a copy to avoid SettingWithCopyWarning
tracks = tracks[['track_id', 'track_name', 'album_id', 'artist_id', 'genre_id', 'duration', 'explicit', 'popularity']].copy()

# Save the original tracks data to a CSV file before modifying track_id
tracks.to_csv('dataset_csv/original_tracks.csv', index=False)

# Assign sequential integers to track_id starting from 1
tracks.loc[:, 'track_id'] = range(1, len(tracks) + 1)

# Save the modified tracks data to a CSV file
tracks.to_csv('dataset_csv/tracks.csv', index=False)

print("Original Tracks CSV file has been created successfully.")
print("Tracks CSV file with updated track_id has been created successfully.")