from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure the LLM model client
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("API key not found! Please set the GOOGLE_API_KEY in your environment.")

genai.configure(api_key=api_key)

# Initialize the LLM model and chat session
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

def get_gemini_response(prompt):
    try:
        response = chat.send_message(prompt, stream=False)
        return response.text.strip() if response else "No response received."
    except Exception as e:
        return f"Error: {str(e)}"

def preprocess_data_for_ipc(data):
    return (
        f"Case Type: {data['Case Type'].values[0]}\n"
        f"Date Filed: {data['Date Filed'].values[0]}\n"
        f"Generate the applicable IPC sections for the given case based on the provided information."
    )

def preprocess_data_for_judgment(data):
    return (
        f"Case Type: {data['Case Type'].values[0]}\n"
        f"Plaintiff Name: {data['Plaintiff Name'].values[0]}\n"
        f"Plaintiff's Arguments: {data['Plaintiff Arguments'].values[0]}\n"
        f"Defendant Name: {data['Defendant Name'].values[0]}\n"
        f"Defendant's Arguments: {data['Defendant Arguments'].values[0]}\n"
        f"Date Filed: {data['Date Filed'].values[0]}\n"
        f"Legal Principles: {data['Legal Principles'].values[0]}\n"
        f"Judge Name: {data['Judge Name'].values[0]}\n"
        f"Court Name: {data['Court Name'].values[0]}\n"
        f"Provide a descriptive judgment and predict the outcome of this case based on the above details."
    )

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        try:
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

            # Validate input data
            if not all([case_id, case_type, plaintiff_name, plaintiff_args, 
                        defendant_name, defendant_args, date_filed, 
                        legal_principles, judge_name, court_name]):
                return jsonify({'error': 'All fields are required.'}), 400

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

            # Preprocess data and send it to the LLM model
            ipc_prompt = preprocess_data_for_ipc(data)
            ipc_response = get_gemini_response(ipc_prompt)

            judgment_prompt = preprocess_data_for_judgment(data)
            judgment_response = get_gemini_response(judgment_prompt)

            return jsonify({
                'ipc_response': ipc_response if ipc_response else 'No IPC sections predicted.',
                'response': judgment_response if judgment_response else 'No judgment predicted.'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return render_template('kunal.html')

if __name__ == '__main__':
    app.run(debug=True) 