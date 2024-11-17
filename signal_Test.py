import numpy as np
import pandas as pd
import joblib
from pylsl import StreamInlet, resolve_stream
from scipy.signal import butter, lfilter, iirnotch
from collections import deque, Counter
import time

# Bandpass filter
def bandpass_filter(data, lowcut, highcut, fs, order=4):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return lfilter(b, a, data)

# Notch filter (remove power-line noise)
def notch_filter(data, freq=50.0, fs=256.0, Q=30.0):
    b, a = iirnotch(freq / (fs / 2), Q)
    return lfilter(b, a, data)

# Define frequency bands
BANDS = {
    "Delta": (0.5, 4),
    "Theta": (4, 8),
    "Alpha": (8, 13),
    "Beta": (13, 30),
    "Gamma": (30, 100),
}

# Extract features from a window
def extract_features_window(data):
    features = {}
    for band, (low, high) in BANDS.items():
        filtered = bandpass_filter(data, low, high, fs=256)
        features[f"{band}_mean"] = np.mean(filtered)
        features[f"{band}_std"] = np.std(filtered)
        features[f"{band}_relative"] = np.sum(filtered) / (np.sum(data) + 1e-6)
    # Add ratios
    features["Theta_Alpha_ratio"] = features["Theta_mean"] / (features["Alpha_mean"] + 1e-6)
    features["Beta_Theta_ratio"] = features["Beta_mean"] / (features["Theta_mean"] + 1e-6)
    return features

# Detect blinks with a filter
def detect_blink_with_filter(data, multiplier=3.5):  # Adjusted multiplier
    filtered = bandpass_filter(data, 0.5, 4, fs=256)
    dynamic_threshold = multiplier * np.std(filtered)
    return np.max(np.abs(filtered)) > dynamic_threshold

# Weighted voting for final prediction
def weighted_vote(predictions, probabilities):
    weighted_counts = Counter()
    for pred, prob in zip(predictions, probabilities):
        weighted_counts[pred] += prob
    return max(weighted_counts, key=weighted_counts.get)

# Normalize features dynamically
def normalize_features(features, global_min, global_max):
    normalized = {}
    for key, value in features.items():
        if key in global_min:  # Ensure the feature exists in global_min/global_max
            normalized[key] = (value - global_min[key]) / (global_max[key] - global_min[key] + 1e-6)
    return normalized

# Load training dataset and compute global min/max
training_data = pd.read_csv("eeg_features_windowed.csv")
training_data["Theta_Alpha_ratio"] = training_data["Theta_mean"] / (training_data["Alpha_mean"] + 1e-6)
training_data["Beta_Theta_ratio"] = training_data["Beta_mean"] / (training_data["Theta_mean"] + 1e-6)

feature_columns = [col for col in training_data.columns if col != "Label"]
global_min = training_data[feature_columns].min().to_dict()
global_max = training_data[feature_columns].max().to_dict()

# Load the trained model and label encoder
model = joblib.load("eeg_model_xgboost.pkl")
label_encoder = joblib.load("label_encoder.pkl")

streams = resolve_stream('type', 'EEG')
inlet = StreamInlet(streams[0])

window_size = 256
step_size = 128
data_buffer = []
recent_predictions = deque(maxlen=5)

print("Starting real-time EEG classification...")
while True:
    chunk, timestamps = inlet.pull_chunk()
    if chunk:
        data_buffer.extend(chunk)
        if len(data_buffer) >= window_size:
            window = np.array(data_buffer[-window_size:])
            window = notch_filter(window, freq=50.0)

            # Extract features
            features = extract_features_window(window)
            features = normalize_features(features, global_min, global_max)

            if detect_blink_with_filter(window):
                print("Blink detected!")
            else:
                feature_names = [f"{band}_{stat}" for band in BANDS.keys() for stat in ["mean", "std", "relative"]] + \
                                ["Theta_Alpha_ratio", "Beta_Theta_ratio"]
                X = pd.DataFrame([list(features.values())], columns=feature_names)

                # Predict probabilities and final label
                proba = model.predict_proba(X)[0]
                prediction = model.predict(X)[0]

                # Decode prediction to original label
                decoded_prediction = label_encoder.inverse_transform([prediction])[0]

                recent_predictions.append((decoded_prediction, max(proba)))
                final_prediction = weighted_vote([p[0] for p in recent_predictions],
                                                 [p[1] for p in recent_predictions])
                print(f"Final Prediction: {final_prediction} (Confidence: {max(proba):.2f})")

            data_buffer = data_buffer[step_size:]
    time.sleep(1)

