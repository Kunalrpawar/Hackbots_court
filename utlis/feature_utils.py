from sklearn.preprocessing import LabelEncoder
import joblib

def load_label_encoders(file_path):
    """
    Load label encoders from a file.
    """
    try:
        return joblib.load(file_path)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Label encoders file not found: {str(e)}")

def encode_features(df, label_encoders):
    """
    Encode categorical features using label encoders.
    """
    for col, le in label_encoders.items():
        if col in df.columns:
            df[col] = le.transform(df[col].astype(str))
    return df
