import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib

# Step 1: Load the Features
features = pd.read_csv("eeg_features_windowed.csv")

# Step 2: Add New Features (Ratios)
features["Theta_Alpha_ratio"] = features["Theta_mean"] / (features["Alpha_mean"] + 1e-6)
features["Beta_Theta_ratio"] = features["Beta_mean"] / (features["Theta_mean"] + 1e-6)

# Step 3: Prepare the Input (X) and Target (y)
X = features.drop("Label", axis=1)  # Drop the label column to use as input
y = features["Label"]  # Target labels (left, right, rest)

# Step 4: Split the Dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Step 5: Train the Random Forest Model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Step 6: Evaluate the Model
y_pred = model.predict(X_test)
print("Classification Report:")
print(classification_report(y_test, y_pred))
print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")

# Step 7: Save the Trained Model
joblib.dump(model, "eeg_model_windowed.pkl")
print("Model saved as 'eeg_model_windowed.pkl'")


####Training XGboosting#####

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import xgboost as xgb
import joblib

# Step 1: Load the Features
features = pd.read_csv("eeg_features_windowed.csv")

# Step 2: Add New Features (Ratios)
features["Theta_Alpha_ratio"] = features["Theta_mean"] / (features["Alpha_mean"] + 1e-6)
features["Beta_Theta_ratio"] = features["Beta_mean"] / (features["Theta_mean"] + 1e-6)

# Step 3: Prepare the Input (X) and Target (y)
X = features.drop("Label", axis=1)  # Drop the label column to use as input
y = features["Label"]  # Target labels (left, right, rest)

# Encode string labels into numeric values
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Step 4: Split the Dataset
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)

# Step 5: Train the Gradient Boosting Model (XGBoost)
xgb_model = xgb.XGBClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    use_label_encoder=False,
    objective="multi:softprob"  # Set objective for multi-class classification
)

# Pass eval_set directly without eval_metric
xgb_model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    verbose=True
)

# Step 6: Save the Trained Model
joblib.dump(xgb_model, "eeg_model_xgboost.pkl")
joblib.dump(label_encoder, "label_encoder.pkl")  # Save the label encoder
print("Model saved as 'eeg_model_xgboost.pkl'")
print("Label encoder saved as 'label_encoder.pkl'")

# Step 7: Evaluate the Model
y_pred = xgb_model.predict(X_test)
y_pred_decoded = label_encoder.inverse_transform(y_pred)  # Decode predictions
y_test_decoded = label_encoder.inverse_transform(y_test)

print("Classification Report:")
print(classification_report(y_test_decoded, y_pred_decoded))
print(f"Accuracy: {accuracy_score(y_test_decoded, y_pred_decoded):.2f}")



