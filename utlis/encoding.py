def encode_features(df, label_encoders):
    categorical_columns = ['Case Type', 'Court Name', 'Plaintiff', 'Defendant']
    for col in categorical_columns:
        if col in df.columns:
            df[col] = label_encoders[col].transform(df[col])
    return df
