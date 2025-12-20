import pandas as pd

# Load the datasets
dataset = pd.read_csv('dataset_csv/dataset.csv')
albums = pd.read_csv('dataset_csv/albums.csv')
artists = pd.read_csv('dataset_csv/artists.csv')
genres = pd.read_csv('dataset_csv/genres.csv')

# Extract necessary columns for tracks
tracks = dataset[['track_id', 'track_name', 'album_name', 'artists', 'duration_ms', 'explicit', 'popularity']]

# Map album_name to album_id using albums.csv
album_map = albums.set_index('album_name')['album_id'].to_dict()
tracks['album_id'] = tracks['album_name'].map(album_map)

# Map artists to artist_id using artists.csv
artist_map = artists.set_index('artist_name')['artist_id'].to_dict()
tracks['artist_id'] = tracks['artists'].map(artist_map)

# Map track_genre to genre_id using genres.csv
genre_map = genres.set_index('genre')['genre_id'].to_dict()
tracks['genre_id'] = dataset['track_genre'].map(genre_map)

# Rename and transform columns to match the Tracks table schema
tracks.rename(columns={'duration_ms': 'duration'}, inplace=True)
tracks['duration'] = (tracks['duration'] / 1000).astype(int)  # Convert duration from ms to seconds

# Preprocess the explicit column: Convert True/False to 1/0
tracks['explicit'] = tracks['explicit'].map({True: 1, False: 0}).fillna(0).astype(int)

# Handle empty artist_id values by replacing NaN with None - Skip TODO
tracks['artist_id'] = tracks['artist_id']

# Assign sequential integers to track_id starting from 1
tracks['track_id'] = range(1, len(tracks) + 1)

# Select only the required columns
tracks = tracks[['track_id', 'track_name', 'album_id', 'artist_id', 'genre_id', 'duration', 'explicit', 'popularity']]

# Save the tracks data to a CSV file
tracks.to_csv('dataset_csv/tracks.csv', index=False)

print("Tracks CSV file has been created successfully.")