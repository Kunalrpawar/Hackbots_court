def encode_features(input_data, label_encoders):
    # List of categorical columns
    categorical_columns = ['case_type', 'court', 'plaintiff', 'defendant']
    
    # Encode each categorical feature
    for col in categorical_columns:
        if col in input_data.columns and col in label_encoders:
            input_data[col] = label_encoders[col].transform(input_data[col])

    return input_data
