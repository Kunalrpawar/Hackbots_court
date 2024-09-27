from flask import Flask, render_template, request
import pandas as pd
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure the Gemini API client
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    raise ValueError("API key not found! Please set the GOOGLE_API_KEY in your environment.")

# Initialize the Gemini Pro model and chat session
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

# Function to send input to Gemini AI and receive a response
def get_gemini_response(input_text):
    try:
        response = chat.send_message(input_text, stream=True)
        full_response = ''.join([chunk.text for chunk in response])
        return full_response
    except Exception as e:
        return f"Error: {str(e)}"

# Preprocess the data (convert to text format for Gemini AI)
def preprocess_data_for_gemini(data):
    # Convert 'Date Filed' to datetime and extract year, month, and day
    data['Date Filed'] = pd.to_datetime(data['Date Filed'], errors='coerce')
    data['Date Filed Year'] = data['Date Filed'].dt.year
    data['Date Filed Month'] = data['Date Filed'].dt.month
    data['Date Filed Day'] = data['Date Filed'].dt.day

    # Combine relevant columns into a prompt for Gemini AI
    prompt = (
        f"Case Type: {data['Case Type'].values[0]}\n"
        f"Plaintiff Name: {data['Plaintiff Name'].values[0]}\n"
        f"Plaintiff's Arguments: {data['Plaintiff Arguments'].values[0]}\n"
        f"Defendant Name: {data['Defendant Name'].values[0]}\n"
        f"Defendant's Arguments: {data['Defendant Arguments'].values[0]}\n"
        f"Date Filed: {data['Date Filed Year'].values[0]}-{data['Date Filed Month'].values[0]}-{data['Date Filed Day'].values[0]}\n"
        f"Legal Principles: {data['Legal Principles'].values[0]}\n"
        f"Judge Name: {data['Judge Name'].values[0]}\n"
        f"Court Name: {data['Court Name'].values[0]}\n"
        f"Provide a descriptive judgment and predict the outcome of this case based on the above details.\n"
    )
    return prompt

@app.route('/', methods=['GET', 'POST'])
def home():
    # Initialize empty prompt and response
    prompt = None
    response = None
    
    if request.method == 'POST':
        # Capture form inputs
        case_id = request.form.get('case_id')
        case_type = request.form.get('case_type')
        plaintiff_name = request.form.get('plaintiff_name')
        plaintiff_args = request.form.get('plaintiff_args')
        defendant_name = request.form.get('defendant_name')
        defendant_args = request.form.get('defendant_args')
        date_filed = request.form.get('date_filed')
        legal_principles = request.form.get('legal_principles')
        judge_name = request.form.get('judge_name')
        court_name = request.form.get('court_name')

        # Combine inputs into a DataFrame to simulate a case entry
        data = pd.DataFrame([{
            'Case ID': case_id,
            'Case Type': case_type,
            'Plaintiff Name': plaintiff_name,
            'Plaintiff Arguments': plaintiff_args,
            'Defendant Name': defendant_name,
            'Defendant Arguments': defendant_args,
            'Date Filed': date_filed,
            'Legal Principles': legal_principles,
            'Judge Name': judge_name,
            'Court Name': court_name
        }])

        # Preprocess data and send it to Gemini AI
        prompt = preprocess_data_for_gemini(data)
        response = get_gemini_response(prompt)

    return render_template('kunal.html', prompt=prompt, response=response)

if __name__ == '__main__':
    app.run(debug=True)
