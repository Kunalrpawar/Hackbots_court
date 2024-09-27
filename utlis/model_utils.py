import pandas as pd
import joblib

def load_model(model_path, encoder_path):
    """
    Load the machine learning model and label encoders from disk.
    """
    model = joblib.load(model_path)
    label_encoders = joblib.load(encoder_path)
    return model, label_encoders

def preprocess_data(df, label_encoders):
    """
    Preprocess the input data for prediction.
    Encodes categorical features using the provided label encoders.
    """
    for col, le in label_encoders.items():
        if col in df.columns:
            df[col] = le.transform(df[col].astype(str))
        else:
            df[col] = le.transform([None] * len(df))
    return df
