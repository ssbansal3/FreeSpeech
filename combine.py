import pandas as pd
import numpy as np
import glob

# Combine all CSV files
data_path = "filtered_data/"
csv_files = glob.glob(data_path + "*.csv")
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

combined_data.to_csv("combined_eeg_data.csv", index=False)
print("Combined data saved.")

# Feature extraction
def extract_features(data):
    features = {}
    for band in ['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma']:
        if band in data:
            features[f"{band}_mean"] = np.mean(data[band])
            features[f"{band}_std"] = np.std(data[band])
            features[f"{band}_relative"] = np.sum(data[band]) / np.sum(data[['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma']].sum(axis=1))
    return features

feature_data = []

# Iterate over labels
for label, group in combined_data.groupby("Label"):
    print(f"Processing label: {label}")
    trial_features = extract_features(group)
    trial_features["Label"] = label
    feature_data.append(trial_features)

# Save extracted features
feature_df = pd.DataFrame(feature_data)
feature_df.to_csv("eeg_features.csv", index=False)
print("Feature extraction complete.")

