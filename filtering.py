import pandas as pd

# Step 1: Load the EEG data file into a Pandas DataFrame to inspect its structure.
eeg_data = pd.read_csv('data/right_trial5.csv')

# Display the first few rows of the dataset to understand its structure.
eeg_data.head()


from scipy.signal import butter, lfilter

# Define a bandpass filter function
def bandpass_filter(data, lowcut, highcut, fs, order=4):
    """
    Apply a bandpass filter to a 1D numpy array.
    :param data: The raw EEG data (1D array)
    :param lowcut: The lower frequency bound
    :param highcut: The upper frequency bound
    :param fs: Sampling frequency (Hz)
    :param order: Filter order
    :return: Bandpass-filtered data
    """
    nyquist = 0.5 * fs  # Nyquist frequency
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return lfilter(b, a, data)

# Function defined; now, we will apply it to the dataset. Next, we move on to filtering the EEG channels.

import numpy as np

# Sampling frequency (fs) assumed to be 256 Hz 
fs = 256  

# Define frequency bands
frequency_bands = {
    'Delta': (0.5, 4),
    'Theta': (4, 8),
    'Alpha': (8, 13),
    'Beta': (13, 30),
    'Gamma': (30, 100)
}

# Initialize a new DataFrame for filtered data
filtered_data = pd.DataFrame()
filtered_data['timestamps'] = eeg_data['timestamps']

# Apply bandpass filtering to each frequency band
for band_name, (low, high) in frequency_bands.items():
    band_columns = []
    for column in eeg_data.columns[1:]:  # Ignore the 'timestamps' column
        filtered_signal = bandpass_filter(eeg_data[column].values, low, high, fs)
        band_columns.append(filtered_signal)
    # Average across channels for each band
    filtered_data[band_name] = np.mean(band_columns, axis=0)

# Step 3 complete: frequency bands filtered. Next, we will save the filtered data.

# Save the filtered data to a new CSV file
filtered_file_path = 'filtered_data/right_filtered_trial5.csv'
filtered_data.to_csv(filtered_file_path, index=False)

# Provide the path to the user
filtered_file_path
