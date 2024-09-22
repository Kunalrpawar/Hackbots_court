from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
from utlis.preprocessing import preprocess_data
from utlis.encoding import encode_features

app = Flask(__name__)

# Load the pre-trained model and the label encoders
model = joblib.load('case_outcome_model.pkl')
label_encoders = joblib.load('label_encoders.pkl')

@app.route('/')
def home():
    # Render the index.html page
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get JSON data from the request
        data = request.get_json()

        # Convert incoming data into a DataFrame
        input_data = pd.DataFrame([data])

        # Preprocess the data
        input_data = preprocess_data(input_data)
        
        # Encode categorical features
        input_data = encode_features(input_data, label_encoders)

        # Ensure all columns required by the model are present
        model_columns = [col for col in input_data.columns if col in label_encoders.keys()]
        for col in model_columns:
            if col not in input_data.columns:
                input_data[col] = 0  # Assign a default value if column is missing
         
        input_data = input_data[model_columns]  # Reorder columns to match model's training data

        # Make predictions
        prediction = model.predict(input_data)

        # Return the result
        return jsonify({'outcome_prediction': int(prediction[0])})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
