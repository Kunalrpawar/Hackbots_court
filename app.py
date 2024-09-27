from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
import os
import joblib
import pandas as pd

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API client
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    raise ValueError("API key not found! Please set the GOOGLE_API_KEY in your environment.")

# Initialize the Gemini Pro model
model = genai.GenerativeModel("gemini-pro")

# Load your ML models and encoders
# le_case_type = joblib.load('models/label_encoder_case_type.pkl')
# le_plaintiff = joblib.load('models/label_encoder_plaintiff.pkl')
# le_defendant = joblib.load('models/label_encoder_defendant.pkl')
# case_outcome_model = joblib.load('models/case_outcome_model.pkl')

# Function to preprocess input data for prediction
def preprocess_input(input_data):
    input_data['Case Type'] = le_case_type.transform([input_data['Case Type']])
    input_data['Plaintiff'] = le_plaintiff.transform([input_data['Plaintiff']])
    input_data['Defendant'] = le_defendant.transform([input_data['Defendant']])
    input_data['Date Filed'] = pd.to_datetime(input_data['Date Filed']).timestamp()
    return pd.DataFrame(input_data)

# Route for homepage
@app.route("/")
def home():
    return render_template("index.html")

# API route for case prediction
@app.route("/predict", methods=["POST"])
def predict():
    try:
        input_data = {
            'Case Title': request.form['case_title'],
            'Date Filed': request.form['date_filed'],
            'Case Type': request.form['case_type'],
            'Court Name': request.form['court_name'],
            'Plaintiff': request.form['plaintiff'],
            'Defendant': request.form['defendant']
        }
        
        preprocessed_input = preprocess_input(input_data)
        prediction = case_outcome_model.predict(preprocessed_input)
        
        return jsonify({"outcome": prediction[0]})
    
    except Exception as e:
        return jsonify({"error": str(e)})

# API route for chatbot
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    try:
        response = model.generate_content(user_input)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
