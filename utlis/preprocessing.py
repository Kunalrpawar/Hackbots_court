import pandas as pd

def preprocess_data(df):
    # Example preprocessing steps
    # Convert 'Date Filed' to datetime format and extract features
    df['Date Filed'] = pd.to_datetime(df['Date Filed'])
    df['year_filed'] = df['Date Filed'].dt.year
    df['month_filed'] = df['Date Filed'].dt.month
    df['day_filed'] = df['Date Filed'].dt.day
    
    # Drop the original 'Date Filed' column
    df = df.drop(columns=['Date Filed'])
    
    return df
