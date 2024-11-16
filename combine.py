import pandas as pd
import glob

# Path to your filtered data directory
data_path = "filtered_data/"  # Adjust this to your folder path
csv_files = glob.glob(data_path + "*.csv")

# Initialize an empty DataFrame
combined_data = pd.DataFrame()

# Combine all files and add labels
for file in csv_files:
    # Read each file
    trial_data = pd.read_csv(file)
    
    # Extract the label (based on filename)
    if "left" in file:
        trial_data["Label"] = "left"
    elif "right" in file:
        trial_data["Label"] = "right"
    elif "rest" in file:
        trial_data["Label"] = "rest"
    
    # Append to the combined DataFrame
    combined_data = pd.concat([combined_data, trial_data], ignore_index=True)

# Save the combined dataset (optional)
combined_data.to_csv("combined_eeg_data.csv", index=False)
