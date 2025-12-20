import pandas as pd

# Load the dataset.csv file
dataset_path = "dataset_csv/dataset.csv"
dataset = pd.read_csv(dataset_path)

# Select the relevant columns for the AudioFeatures table
audio_features = dataset[[
    "track_id", "danceability", "energy", "valence", "tempo", "loudness", "acousticness"
]].copy()

# Save the processed data with original string track_id
output_path = "dataset_csv/original_audio_features.csv"
audio_features.to_csv(output_path, index=False)

# Load the original tracks file (with string track_id)
original_tracks = pd.read_csv('dataset_csv/original_tracks.csv')

# Load the new tracks file (with integer track_id)
tracks = pd.read_csv('dataset_csv/tracks.csv')

# Create a mapping from the original string track_id to the new integer track_id
track_id_map = pd.Series(tracks.track_id.values, index=original_tracks.track_id).to_dict()

# Map the string track_id to the new integer track_id
audio_features['track_id'] = audio_features['track_id'].map(track_id_map)

# Drop rows where track_id could not be mapped (is NaN) and convert to integer
audio_features.dropna(subset=['track_id'], inplace=True)
audio_features['track_id'] = audio_features['track_id'].astype(int)

# Save the audio_features.csv file with updated integer track_id values
final_output_path = 'dataset_csv/audio_features.csv'
audio_features.to_csv(final_output_path, index=False)

print(f"Audio features dataset saved to {final_output_path}")