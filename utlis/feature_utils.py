from sklearn.preprocessing import LabelEncoder
import joblib
import os

def load_label_encoders():
    """
    Load all label encoders from the models directory.
    """
    encoders = {}
    encoder_files = {
        'case_type': 'models/label_encoder_case_type.pkl',
        'court': 'models/label_encoder_court.pkl',
        'plaintiff': 'models/label_encoder_plaintiff.pkl',
        'defendant': 'models/label_encoder_defendant.pkl'
    }
    
    for name, file_path in encoder_files.items():
        try:
            if os.path.exists(file_path):
                encoders[name] = joblib.load(file_path)
            else:
                print(f"Warning: {file_path} not found")
                encoders[name] = None
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            encoders[name] = None
    
    return encoders

def encode_features(df, label_encoders):
    """
    Encode categorical features using label encoders.
    """
    encoded_df = df.copy()
    
    for col, le in label_encoders.items():
        if col in encoded_df.columns and le is not None:
            try:
                # Handle unseen categories by using a default value
                encoded_df[col] = le.transform(encoded_df[col].astype(str))
            except ValueError:
                # If unseen categories exist, use a default encoding
                print(f"Warning: Unseen categories in {col}, using default encoding")
                encoded_df[col] = 0
    
    return encoded_df

def get_feature_names():
    """
    Get the list of feature names used by the model.
    """
    return ['Case Type', 'Court Name', 'Plaintiff', 'Defendant', 'Date Filed']
