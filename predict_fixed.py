import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import os

def preprocess_input(input_data):
    """Preprocess input data for prediction"""
    try:
        # Check if required model files exist
        required_files = [
            'models/label_encoder_case_type.pkl',
            'models/label_encoder_court.pkl',
            'models/label_encoder_plaintiff.pkl',
            'models/label_encoder_defendant.pkl'
        ]
        
        missing_files = [f for f in required_files if not os.path.exists(f)]
        if missing_files:
            raise FileNotFoundError(f"Missing required model files: {missing_files}")
        
        # Load encoders
        le_case_type = joblib.load('models/label_encoder_case_type.pkl')
        le_court = joblib.load('models/label_encoder_court.pkl')
        le_plaintiff = joblib.load('models/label_encoder_plaintiff.pkl')
        le_defendant = joblib.load('models/label_encoder_defendant.pkl')
        
        # Create a copy to avoid modifying original data
        processed_data = input_data.copy()
        
        # Transform input data - handle unknown categories gracefully
        try:
            processed_data['Case Type'] = le_case_type.transform(processed_data['Case Type'].astype(str))
        except ValueError:
            processed_data['Case Type'] = 0  # Default encoding
            
        try:
            processed_data['Court Name'] = le_court.transform(processed_data['Court Name'].astype(str))
        except ValueError:
            processed_data['Court Name'] = 0

        try:
            processed_data['Plaintiff'] = le_plaintiff.transform(processed_data['Plaintiff'].astype(str))
        except ValueError:
            processed_data['Plaintiff'] = 0
            
        try:
            processed_data['Defendant'] = le_defendant.transform(processed_data['Defendant'].astype(str))
        except ValueError:
            processed_data['Defendant'] = 0
        
        # Convert date to timestamp
        processed_data['Date Filed'] = pd.to_datetime(processed_data['Date Filed'], errors='coerce').map(
            lambda x: x.timestamp() if pd.notna(x) else 0
        )
        
        return processed_data
        
    except Exception as e:
        print(f"Error in preprocessing: {e}")
        raise

def predict_outcome(input_data):
    """Predict case outcome using trained model"""
    try:
        # Check if model exists
        model_path = 'models/case_outcome_model.pkl'
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}. Please train the model first.")
        
        # Load model
        model = joblib.load(model_path)
        
        # Preprocess the input data
        preprocessed_input = preprocess_input(input_data)
        
        # Make prediction
        prediction = model.predict(preprocessed_input)
        return prediction
        
    except Exception as e:
        print(f"Error in prediction: {e}")
        raise

def predict_outcome_with_confidence(input_data):
    """Predict case outcome with confidence scores"""
    try:
        # Check if model exists
        model_path = 'models/case_outcome_model.pkl'
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}. Please train the model first.")
        
        # Load model
        model = joblib.load(model_path)
        
        # Preprocess the input data
        preprocessed_input = preprocess_input(input_data)
        
        # Make prediction with probabilities
        prediction = model.predict(preprocessed_input)
        probabilities = model.predict_proba(preprocessed_input)
        
        # Convert numpy types to Python native types for JSON serialization
        return {
            'prediction': prediction[0],
            'confidence': float(np.max(probabilities[0])),
            'probabilities': probabilities[0]
        }
        
    except Exception as e:
        print(f"Error in prediction with confidence: {e}")
        raise

# Example usage
if __name__ == '__main__':
    try:
        # Input data
        input_data = pd.DataFrame({
            'Case Type': ['Corporate Dispute'],
            'Court Name': ['Madras High Court'],
            'Plaintiff': ['ABC Corporation'],
            'Defendant': ['XYZ Ltd'],
            'Date Filed': ['2024/09/25']
        })

        # Get prediction
        outcome = predict_outcome(input_data)
        print("Predicted Outcome:", outcome)
        
        # Get prediction with confidence
        result = predict_outcome_with_confidence(input_data)
        print("Predicted Outcome:", result['prediction'])
        print("Confidence:", f"{result['confidence']:.2%}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have trained the model first using train_model.py")
