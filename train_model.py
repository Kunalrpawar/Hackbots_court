import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import os

def train_case_outcome_model():
    """Train the case outcome prediction model"""
    try:
        # Load your dataset - check if cases.csv exists
        dataset_path = 'cases.csv'
        if not os.path.exists(dataset_path):
            print(f"Dataset not found at {dataset_path}")
            return False
            
        data = pd.read_csv(dataset_path)
        print(f"Loaded dataset with {len(data)} cases")
        
        # Check if required columns exist
        required_columns = ['Case Type', 'Court Name', 'Plaintiff', 'Defendant', 'Date Filed', 'Outcome']
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            print(f"Missing required columns: {missing_columns}")
            # Add missing columns with default values
            for col in missing_columns:
                if col == 'Outcome':
                    data[col] = 'Unknown'  # Default outcome
                else:
                    data[col] = 'Unknown'  # Default value for other columns
        
        # Select features and target
        X = data[['Case Type', 'Court Name', 'Plaintiff', 'Defendant', 'Date Filed']]
        y = data['Outcome']
        
        # Handle missing values
        X = X.fillna('Unknown')
        y = y.fillna('Unknown')
        
        # Encode categorical variables
        le_case_type = LabelEncoder()
        le_court = LabelEncoder()
        le_plaintiff = LabelEncoder()
        le_defendant = LabelEncoder()
        
        # Fit and transform each column
        X['Case Type'] = le_case_type.fit_transform(X['Case Type'].astype(str))
        X['Court Name'] = le_court.fit_transform(X['Court Name'].astype(str))
        X['Plaintiff'] = le_plaintiff.fit_transform(X['Plaintiff'].astype(str))
        X['Defendant'] = le_defendant.fit_transform(X['Defendant'].astype(str))
        
        # Convert date to timestamp
        X['Date Filed'] = pd.to_datetime(X['Date Filed'], errors='coerce').map(
            lambda x: x.timestamp() if pd.notna(x) else 0
        )
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train the model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate the model
        train_score = model.score(X_train, y_train)
        test_score = model.score(X_test, y_test)
        
        print(f"Training accuracy: {train_score:.4f}")
        print(f"Testing accuracy: {test_score:.4f}")
        
        # Create models directory if it doesn't exist
        os.makedirs('models', exist_ok=True)
        
        # Save the model and encoders
        joblib.dump(model, 'models/case_outcome_model.pkl')
        joblib.dump(le_case_type, 'models/label_encoder_case_type.pkl')
        joblib.dump(le_court, 'models/label_encoder_court.pkl')
        joblib.dump(le_plaintiff, 'models/label_encoder_plaintiff.pkl')
        joblib.dump(le_defendant, 'models/label_encoder_defendant.pkl')
        
        print("Model and encoders saved successfully!")
        return True
        
    except Exception as e:
        print(f"Error training model: {e}")
        return False

if __name__ == '__main__':
    success = train_case_outcome_model()
    if success:
        print("Model training completed successfully!")
    else:
        print("Model training failed!")
