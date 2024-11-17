import pandas as pd
import numpy as np
import glob

# Path to your filtered data directory
data_path = "filtered_data/"  # Adjust this to your folder path
csv_files = glob.glob(data_path + "*.csv")

# Combine all trials into one DataFrame
combined_data = pd.DataFrame()

for file in csv_files:
    trial_data = pd.read_csv(file)
    if "left" in file:
        trial_data["Label"] = "left"
    elif "right" in file:
        trial_data["Label"] = "right"
    elif "rest" in file:
        trial_data["Label"] = "rest"
    combined_data = pd.concat([combined_data, trial_data], ignore_index=True)

# Save combined data for inspection
combined_data.to_csv("combined_eeg_data.csv", index=False)

# Feature extraction function using sliding windows
def extract_features_windowed(data, window_size, step_size, label):
    """
    Extract features using a sliding window approach.
    
    Args:
        data: DataFrame with raw EEG band data (Delta, Theta, etc.)
        window_size: Number of samples per window
        step_size: Step size for sliding window
        label: Label for the entire trial (left, right, rest)
    
    Returns:
        A DataFrame of extracted features for each window
    """
    features_list = []
    for start in range(0, len(data) - window_size + 1, step_size):
        window = data.iloc[start:start + window_size]
        features = {"Label": label}
        for band in ['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma']:
            features[f"{band}_mean"] = window[band].mean()
            features[f"{band}_std"] = window[band].std()
            features[f"{band}_relative"] = window[band].sum() / window[['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma']].sum().sum()
        features_list.append(features)
    return pd.DataFrame(features_list)

# Parameters for sliding windows
window_size = 256  # Example: 1 second window for 256 Hz sampling rate
step_size = 128    # Example: 50% overlap

# Extract features for each trial
feature_data = []

for label in combined_data["Label"].unique():
    # Filter data for the current label
    label_data = combined_data[combined_data["Label"] == label]
    # Extract features using sliding windows
    features = extract_features_windowed(label_data, window_size, step_size, label)
    feature_data.append(features)

# Combine all features into a single DataFrame
feature_df = pd.concat(feature_data, ignore_index=True)

# Save the extracted features
feature_df.to_csv("eeg_features_windowed.csv", index=False)

print(f"Feature extraction complete. Features saved to 'eeg_features_windowed.csv'.")
