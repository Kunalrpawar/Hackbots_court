from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def welcome():
    return render_template('homepage.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/cases')
def cases():
    return render_template('cases.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/ai_model', methods=['GET'])
def ai_model():
    return render_template('kunal.html')  # AI model page

@app.route('/', methods=['POST'])
def predict_case():
    # Extract form data
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

    # Example API call
    api_url = "https://api.gemini.example/predict"  # Replace with your actual API URL
    payload = {
        "case_id": case_id,
        "case_type": case_type,
        "plaintiff_name": plaintiff_name,
        "plaintiff_args": plaintiff_args,
        "defendant_name": defendant_name,
        "defendant_args": defendant_args,
        "date_filed": date_filed,
        "legal_principles": legal_principles,
        "judge_name": judge_name,
        "court_name": court_name
    }

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()  # Raise an error for bad responses
        api_data = response.json()
        
        ipc_response = api_data.get('ipc_sections', 'No IPC sections predicted.')
        overall_response = api_data.get('judgment', 'No judgment predicted.')
    except requests.exceptions.RequestException as e:
        print("API Request Error:", e)
        ipc_response = "Error calling API"
        overall_response = "Error calling API"
    except Exception as e:
        print("An unexpected error occurred:", e)
        ipc_response = "An unexpected error occurred."
        overall_response = "An unexpected error occurred."

    return jsonify({
        'ipc_response': ipc_response,
        'response': overall_response
    })

if __name__ == '__main__':
    app.run(debug=True)
