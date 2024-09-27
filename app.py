from flask import Flask, request, render_template
import pickle
import pandas as pd
import os

# Initialize Flask app
app = Flask(__name__)

# Load model and encoders
model_path = os.path.join("static", "models", "case_outcome_model.pkl")
le_case_type_path = os.path.join("static", "models", "label_encoder_case_type.pkl")
le_plaintiff_path = os.path.join("static", "models", "label_encoder_plaintiff.pkl")
le_defendant_path = os.path.join("static", "models", "label_encoder_defendant.pkl")

try:
    with open(model_path, 'rb') as file:
        model = pickle.load(file)
    with open(le_case_type_path, 'rb') as file:
        le_case_type = pickle.load(file)
    with open(le_plaintiff_path, 'rb') as file:
        le_plaintiff = pickle.load(file)
    with open(le_defendant_path, 'rb') as file:
        le_defendant = pickle.load(file)
    print("Models loaded successfully with pickle!")
except Exception as e:
    print(f"Error loading models with pickle: {e}")

def preprocess_input(input_data):
    input_data['Case Type'] = le_case_type.transform(input_data['Case Type'])
    input_data['Plaintiff'] = le_plaintiff.transform(input_data['Plaintiff'])
    input_data['Defendant'] = le_defendant.transform(input_data['Defendant'])
    input_data['Date Filed'] = pd.to_datetime(input_data['Date Filed']).map(pd.Timestamp.timestamp)
    return input_data

def predict_outcome(input_data):
    preprocessed_input = preprocess_input(input_data)
    prediction = model.predict(preprocessed_input)
    return prediction[0]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        case_type = request.form['case_type']
        court_name = request.form['court_name']
        plaintiff = request.form['plaintiff']
        defendant = request.form['defendant']
        date_filed = request.form['date_filed']

        input_data = pd.DataFrame({
            'Case Type': [case_type],
            'Court Name': [court_name],
            'Plaintiff': [plaintiff],
            'Defendant': [defendant],
            'Date Filed': [date_filed]
        })

        try:
            outcome = predict_outcome(input_data)
            return render_template('index.html', outcome=outcome)
        except Exception as e:
            return render_template('index.html', error=str(e))

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
