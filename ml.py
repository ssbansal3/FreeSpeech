import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib

# Step 1: Load the Features
features = pd.read_csv("eeg_features_windowed.csv")

# Step 2: Prepare the Input (X) and Target (y)
X = features.drop("Label", axis=1)  # Drop the label column to use as input
y = features["Label"]  # Target labels (left, right, rest)

# Step 3: Split the Dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Step 4: Train the Random Forest Model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Step 5: Evaluate the Model
y_pred = model.predict(X_test)
print("Classification Report:")
print(classification_report(y_test, y_pred))
print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")

# Step 6: Save the Trained Model
joblib.dump(model, "eeg_model_windowed.pkl")
print("Model saved as 'eeg_model_windowed.pkl'")


