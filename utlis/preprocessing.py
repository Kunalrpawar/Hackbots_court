import pandas as pd

def preprocess_data(input_data):
    # Convert case_date to datetime and extract year, month, day
    input_data['case_date'] = pd.to_datetime(input_data['case_date'])
    input_data['year'] = input_data['case_date'].dt.year
    input_data['month'] = input_data['case_date'].dt.month
    input_data['day'] = input_data['case_date'].dt.day

    # Drop the case_date column
    input_data = input_data.drop(columns=['case_date'])
    
    return input_data
