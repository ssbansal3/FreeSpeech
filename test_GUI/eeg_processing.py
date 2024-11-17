import threading
import numpy as np
import pandas as pd
import joblib
from pylsl import StreamInlet, resolve_stream
from scipy.signal import butter, lfilter, iirnotch
from collections import deque, Counter
import time

class EEGThread(threading.Thread):
    def __init__(self, event_queue):
        super().__init__()
        self.event_queue = event_queue
        self._stop_event = threading.Event()
        self.daemon = True  # Allow thread to be killed when main program exits
        self.initialize_eeg_processing()

    def initialize_eeg_processing(self):
        # Initialize your EEG processing variables here
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
        self.BANDS = {
            "Delta": (0.5, 4),
            "Theta": (4, 8),
            "Alpha": (8, 13),
            "Beta": (13, 30),
            "Gamma": (30, 100),
        }

        # Extract features from a window
        def extract_features_window(data):
            features = {}
            for band, (low, high) in self.BANDS.items():
                filtered = bandpass_filter(data, low, high, fs=256)
                features[f"{band}_mean"] = np.mean(filtered)
                features[f"{band}_std"] = np.std(filtered)
                features[f"{band}_relative"] = np.sum(filtered) / (np.sum(data) + 1e-6)
            # Add ratios
            features["Theta_Alpha_ratio"] = features["Theta_mean"] / (features["Alpha_mean"] + 1e-6)
            features["Beta_Theta_ratio"] = features["Beta_mean"] / (features["Theta_mean"] + 1e-6)
            return features

        # Detect blinks with a filter
        def detect_blink_with_filter(data, multiplier=3.88):  # Adjusted multiplier
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

        # Assign functions and variables to the class
        self.bandpass_filter = bandpass_filter
        self.notch_filter = notch_filter
        self.extract_features_window = extract_features_window
        self.detect_blink_with_filter = detect_blink_with_filter
        self.weighted_vote = weighted_vote
        self.normalize_features = normalize_features

        # Load training dataset and compute global min/max
        training_data = pd.read_csv("eeg_features_windowed.csv")
        training_data["Theta_Alpha_ratio"] = training_data["Theta_mean"] / (training_data["Alpha_mean"] + 1e-6)
        training_data["Beta_Theta_ratio"] = training_data["Beta_mean"] / (training_data["Theta_mean"] + 1e-6)

        feature_columns = [col for col in training_data.columns if col != "Label"]
        self.global_min = training_data[feature_columns].min().to_dict()
        self.global_max = training_data[feature_columns].max().to_dict()

        # Load the trained model and label encoder
        self.model = joblib.load("eeg_model_xgboost.pkl")
        self.label_encoder = joblib.load("label_encoder.pkl")

        streams = resolve_stream('type', 'EEG')
        self.inlet = StreamInlet(streams[0])

        self.window_size = 256
        self.step_size = 128
        self.data_buffer = []
        self.recent_predictions = deque(maxlen=5)

    def run(self):
        print("Starting EEG Thread...")
        while not self._stop_event.is_set():
            chunk, timestamps = self.inlet.pull_chunk(timeout=1.0)
            if chunk:
                self.data_buffer.extend(chunk)
                if len(self.data_buffer) >= self.window_size:
                    window = np.array(self.data_buffer[-self.window_size:])
                    window = self.notch_filter(window, freq=50.0)

                    # Extract features
                    features = self.extract_features_window(window)
                    features = self.normalize_features(features, self.global_min, self.global_max)

                    if self.detect_blink_with_filter(window):
                        print("Blink detected!")
                        self.event_queue.put("blink")
                    else:
                        feature_names = [f"{band}_{stat}" for band in self.BANDS.keys() for stat in ["mean", "std", "relative"]] + \
                                        ["Theta_Alpha_ratio", "Beta_Theta_ratio"]
                        X = pd.DataFrame([list(features.values())], columns=feature_names)

                        # Predict probabilities and final label
                        proba = self.model.predict_proba(X)[0]
                        prediction = self.model.predict(X)[0]

                        # Decode prediction to original label
                        decoded_prediction = self.label_encoder.inverse_transform([prediction])[0]

                        self.recent_predictions.append((decoded_prediction, max(proba)))
                        final_prediction = self.weighted_vote([p[0] for p in self.recent_predictions],
                                                             [p[1] for p in self.recent_predictions])
                        print(f"Final Prediction: {final_prediction} (Confidence: {max(proba):.2f})")
                        # Put the prediction into the queue
                        if final_prediction.lower() == "left":
                            self.event_queue.put("left")
                        elif final_prediction.lower() == "right":
                            self.event_queue.put("right")
                        # You can add more conditions if needed

                    self.data_buffer = self.data_buffer[self.step_size:]
            time.sleep(0.1)

    def stop(self):
        self._stop_event.set()
