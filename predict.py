import pandas as pd
import joblib

def preprocess_input(input_data):
    # Load encoders
    le_case_type = joblib.load('models/label_encoder_case_type.pkl')
    le_plaintiff = joblib.load('models/label_encoder_plaintiff.pkl')
    le_defendant = joblib.load('models/label_encoder_defendant.pkl')

    # Transform input data
    input_data['Case Type'] = le_case_type.transform(input_data['Case Type'])
    input_data['Plaintiff'] = le_plaintiff.transform(input_data['Plaintiff'])
    input_data['Defendant'] = le_defendant.transform(input_data['Defendant'])
    input_data['Date Filed'] = pd.to_datetime(input_data['Date Filed']).map(pd.Timestamp.timestamp)

    return input_data

def predict_outcome(input_data):
    # Load model
    model = joblib.load('models/case_outcome_model.pkl')

    # Preprocess the input data
    preprocessed_input = preprocess_input(input_data)

    # Make prediction
    prediction = model.predict(preprocessed_input)
    return prediction

# Example usage
if __name__ == '__main__':
    # Input data
    input_data = pd.DataFrame({
        'Case Type': ['Corporate Dispute'],
        'Court Name': ['Madras High Court'],
        'Plaintiff': ['what is water irrigation'],
        'Defendant': ['High Court'],
        'Date Filed': ['2024/09/25']
    })

    # Get prediction
    outcome = predict_outcome(input_data)
    print("Predicted Outcome:", outcome)
