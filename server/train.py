# train_model.py
import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from imblearn.over_sampling import SMOTE


# Load the dataset
data = pd.read_csv("diabetes.csv")

# Preprocess data: Replace zeros with NaN in certain columns and impute
columns_to_impute = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
data[columns_to_impute] = data[columns_to_impute].replace(0, np.nan)

# Ensure the data is numeric
data[columns_to_impute] = data[columns_to_impute].apply(pd.to_numeric)

# Impute the missing values
imputer = SimpleImputer(strategy='median')
data[columns_to_impute] = imputer.fit_transform(data[columns_to_impute])

# Split features and target
X = data.drop('Outcome', axis=1)
y = data['Outcome']

# Split the data for training/testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_test = scaler.transform(X_test)

# SMOTE for Balancing the Dataset
smote = SMOTE(random_state=42)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

# Train Random Forest on Balanced Data
rf_model_smote = RandomForestClassifier(random_state=42)
rf_model_smote.fit(X_train_resampled, y_train_resampled)

# Save the scaler and model to disk
with open("scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)

with open("model.pkl", "wb") as f:
    pickle.dump(rf_model_smote, f)

print("Training complete and objects saved to disk.")