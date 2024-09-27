import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load your dataset
data = pd.read_csv('path_to_your_dataset.csv')  # Update with your dataset path

# Preprocess your data
X = data[['Case Type', 'Court Name', 'Plaintiff', 'Defendant', 'Date Filed']]
y = data['Outcome']  # Update with your target column

# Encode categorical variables
le_case_type = LabelEncoder()
le_plaintiff = LabelEncoder()
le_defendant = LabelEncoder()

X['Case Type'] = le_case_type.fit_transform(X['Case Type'])
X['Plaintiff'] = le_plaintiff.fit_transform(X['Plaintiff'])
X['Defendant'] = le_defendant.fit_transform(X['Defendant'])
X['Date Filed'] = pd.to_datetime(X['Date Filed']).map(pd.Timestamp.timestamp)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Save the model and encoders
joblib.dump(model, 'models/case_outcome_model.pkl')
joblib.dump(le_case_type, 'models/label_encoder_case_type.pkl')
joblib.dump(le_plaintiff, 'models/label_encoder_plaintiff.pkl')
joblib.dump(le_defendant, 'models/label_encoder_defendant.pkl')
