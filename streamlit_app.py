import os
from flask import Flask, render_template, request
from dotenv import load_dotenv
import google.generativeai as gemini

# Load environment variables (API keys, etc.)
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Set Gemini API key
gemini.api_key = os.getenv("GOOGLE_API_KEY")

# Helper function to send the case details to the Gemini AI and predict outcome
def predict_case_outcome(case_details):
    # Compose a prompt combining all case details
    prompt = f"""
    Predict the likely outcome of the following court case:
    
    - Case Title: {case_details['case_title']}
    - Date Filed: {case_details['date_filed']}
    - Case Type: {case_details['case_type']}
    - Plaintiff: {case_details['plaintiff']}
    - Defendant: {case_details['defendant']}
    
    Based on these details, what is the expected judgment?
    """

    # Send the prompt to the Gemini AI API
    try:
        response = gemini.generate_text(prompt=prompt, model="models/text-bison-001", max_tokens=256)
        return response["candidates"][0]["output"]
    except Exception as e:
        return f"Error: {str(e)}"

# Route for the main form page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Collect form data
        case_title = request.form.get('case_title')
        date_filed = request.form.get('date_filed')
        case_type = request.form.get('case_type')
        plaintiff = request.form.get('plaintiff')
        defendant = request.form.get('defendant')

        # Combine data into case details dictionary
        case_details = {
            'case_title': case_title,
            'date_filed': date_filed,
            'case_type': case_type,
            'plaintiff': plaintiff,
            'defendant': defendant
        }

        # Get prediction from Gemini AI
        predicted_outcome = predict_case_outcome(case_details)

        # Return the result to the user
        return render_template('index.html', prediction=predicted_outcome, case_details=case_details)

    return render_template('index.html')

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
