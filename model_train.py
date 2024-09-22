import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from utlis.preprocessing import preprocess_data
from utlis.encoding import encode_features
from sklearn.preprocessing import LabelEncoder

# Load and preprocess data
df = pd.read_csv('case.csv')
df = preprocess_data(df)

# Initialize LabelEncoders for categorical features
categorical_columns = ['Case Type', 'Court Name', 'Plaintiff', 'Defendant']
label_encoders = {}

for col in categorical_columns:
    if col in df.columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))  # Ensure all data is treated as strings
        label_encoders[col] = le

# Save the label encoders
joblib.dump(label_encoders, 'label_encoders.pkl')

# Prepare features and target variable
X = df.drop('Case Outcome', axis=1)
y = df['Case Outcome']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Save model
joblib.dump(model, 'case_outcome_model.pkl')
