from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import requests
import os
from dotenv import load_dotenv
import google.generativeai as genai
import pandas as pd
import joblib
from functools import wraps
import jwt
import datetime
import secrets
import sys

# Load environment variables
load_dotenv()

# Set default secret keys
DEFAULT_SECRET_KEY = secrets.token_hex(32)
DEFAULT_JWT_SECRET = secrets.token_hex(32)

print(" Using secrets:")
print(f"FLASK_SECRET_KEY: {DEFAULT_SECRET_KEY[:10]}...")
print(f"JWT_SECRET_KEY: {DEFAULT_JWT_SECRET[:10]}...")

# Mock user database (replace with real database in production)
USERS = {
    'admin': {
        'password': 'admin123',
        'role': 'admin'
    },
        'user': {
        'password': 'user123',
        'role': 'user'
    }
}

def create_app():
    app = Flask(__name__)
    
    # Set secret keys
    app.secret_key = os.getenv("FLASK_SECRET_KEY", DEFAULT_SECRET_KEY)
    app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY", DEFAULT_JWT_SECRET)
    
    # JWT Configuration
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=24)
    app.config['JWT_ALGORITHM'] = 'HS256'
    
    # Session configuration
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=24)
    
    # File upload configuration
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')    # Configure Gemini API - Updated to Gemini 2.0 Flash
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        try:
            genai.configure(api_key=api_key)
            # Use Gemini 2.0 Flash for better performance
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            print(" Gemini 2.0 Flash model loaded successfully!")
        except Exception as e:
            print(f"  Error loading Gemini 2.0 Flash: {e}")
            try:
                # Fallback to Gemini 1.5 Pro if 2.0 fails
                model = genai.GenerativeModel("gemini-1.5-pro")
                print(" Fallback to Gemini 1.5 Pro model loaded!")
            except Exception as e2:
                print(f" Error loading Gemini 1.5 Pro: {e2}")
                model = None
    else:
        model = None
        print("⚠️  Warning: GOOGLE_API_KEY not found. AI features will be disabled.")

    def token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'token' not in session:
                print(" No token in session")
                return redirect(url_for('login'))
            
            try:
                jwt.decode(session['token'], app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
                print(" Token verified successfully")
                return f(*args, **kwargs)
            except Exception as e:
                print(f"Token verification error: {str(e)}")
                session.clear()
                return redirect(url_for('login'))
        return decorated

    @app.route('/')
    def index():
        if 'token' in session and 'username' in session:
            try:
                # Verify token
                jwt.decode(session['token'], app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
                return redirect(url_for('welcome'))
            except:
                session.clear()
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        # Clear any existing session
        if request.method == 'GET':
            session.clear()
            
        if request.method == 'POST':
            username = request.form.get('username', '').strip().lower()
            password = request.form.get('password', '').strip()
            
            if username in USERS and USERS[username]['password'] == password:
                try:
                    # Create new session
                    session.clear()
                    
                    # Create JWT token
                    now = datetime.datetime.now(datetime.timezone.utc)
                    token_data = {
                        'user': username,
                        'role': USERS[username]['role'],
                        'exp': now + datetime.timedelta(hours=24),
                        'iat': now
                    }
                    
                    token = jwt.encode(
                        token_data,
                        app.config['JWT_SECRET_KEY'],
                        algorithm="HS256"
                    )
                    
                    # Set session data
                    session['token'] = token
                    session['username'] = username
                    session['role'] = USERS[username]['role']
                    
                    return redirect(url_for('welcome'))
                    
                except Exception as e:
                    print(f"Login error: {str(e)}")
                    session.clear()
                    flash('Login error. Please try again.', 'error')
            else:
                flash('Invalid username or password', 'error')
        
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('Logged out successfully!', 'success')
        return redirect(url_for('login'))

    @app.route('/welcome')
    @token_required
    def welcome():
        if 'username' not in session:
            return redirect(url_for('login'))
        return render_template('homepage.html', username=session['username'])
        
    @app.route('/about')
    @token_required
    def about():
        return render_template('about.html')

    @app.route('/services')
    @token_required
    def services():
        return render_template('services.html')
        
    @app.route('/cases')
    @token_required
    def cases():
        return render_template('cases.html')

    @app.route('/contact')
    @token_required
    def contact():
        return render_template('contact.html')

    @app.route('/ai_model')
    @token_required
    def ai_model():
        print(f"🤖 AI Model page accessed by user: {session.get('username')}")
        return render_template('ai.html')

    # Service page routes
    @app.route('/case-filing')
    @token_required
    def case_filing():
        return render_template('case_filing.html')
        
    @app.route('/hearing-schedule')
    @token_required
    def hearing_schedule():
        return render_template('hearing_schedule.html')
        
    @app.route('/case-lookup')
    @token_required
    def case_lookup():
        return render_template('case_lookup.html')
        
    @app.route('/legal-resources')
    @token_required
    def legal_resources():
        return render_template('legal_resources.html')

    @app.route('/predict', methods=['POST'])
    @token_required
    def predict_case():
        try:
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

            # Validate input data
            if not all([case_id, case_type, plaintiff_name, plaintiff_args, 
                        defendant_name, defendant_args, date_filed, 
                        legal_principles, judge_name, court_name]):
                return jsonify({'error': 'All fields are required.'}), 400

            # Use Gemini AI for prediction if available
            if model:
                try:
                    print(f"🤖 Using Gemini model: {model.model_name}")
                    
                    # Create prompt for IPC sections
                    ipc_prompt = f"""
                    You are a legal expert. Based on the following case details, identify the applicable IPC (Indian Penal Code) sections:

                    Case Type: {case_type}
                    Date Filed: {date_filed}
                    Plaintiff Arguments: {plaintiff_args}
                    Defendant Arguments: {defendant_args}
                    Legal Principles: {legal_principles}

                    Please provide:
                    1. Relevant IPC sections with their numbers and descriptions
                    2. Brief explanation of why each section applies
                    3. Any additional legal considerations

                    Format your response in a clear, professional manner suitable for legal documentation.
                    """
                    
                    # Create prompt for judgment
                    judgment_prompt = f"""
                    You are a senior judge with extensive experience in {case_type} cases. Analyze the following case and provide a comprehensive judgment prediction:

                    Case Details:
                    - Case Type: {case_type}
                    - Plaintiff: {plaintiff_name}
                    - Plaintiff's Arguments: {plaintiff_args}
                    - Defendant: {defendant_name}
                    - Defendant's Arguments: {defendant_args}
                    - Date Filed: {date_filed}
                    - Legal Principles: {legal_principles}
                    - Judge: {judge_name}
                    - Court: {court_name}

                    Please provide:
                    1. Case Analysis: Brief overview of the legal issues
                    2. Applicable Laws: Relevant legal principles and precedents
                    3. Judgment Prediction: Likely outcome with reasoning
                    4. Confidence Level: Your confidence in this prediction (High/Medium/Low)
                    5. Key Factors: Main considerations that will influence the decision

                    Format your response as a professional legal judgment summary.
                    """
                    
                    print(" Sending IPC prompt to Gemini...")
                    ipc_response = model.generate_content(ipc_prompt).text
                    print(" IPC response received")
                    
                    print("Sending judgment prompt to Gemini...")
                    judgment_response = model.generate_content(judgment_prompt).text
                    print(" Judgment response received")
                    
                except Exception as e:
                    print(f" AI API Error: {e}")
                    import traceback
                    traceback.print_exc()
                    ipc_response = f"AI prediction error: {str(e)}"
                    judgment_response = f"AI prediction error: {str(e)}"
            else:
                ipc_response = "AI features disabled - API key not configured"
                judgment_response = "AI features disabled - API key not configured"

            return jsonify({
                'ipc_response': ipc_response,
                'response': judgment_response
            })
            
        except Exception as e:
            print(f" General error in predict_case: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500

    @app.route('/ml_predict', methods=['POST'])
    @token_required
    def ml_predict():
        """Traditional ML model prediction endpoint"""
        try:
            # Extract form data
            case_type = request.form.get('case_type')
            court_name = request.form.get('court_name')
            plaintiff = request.form.get('plaintiff_name')
            defendant = request.form.get('defendant_name')
            date_filed = request.form.get('date_filed')

            # Validate input
            if not all([case_type, court_name, plaintiff, defendant, date_filed]):
                return jsonify({'error': 'All fields are required.'}), 400

            # Create input DataFrame
            input_data = pd.DataFrame({
                'Case Type': [case_type],
                'Court Name': [court_name],
                'Plaintiff': [plaintiff],
                'Defendant': [defendant],
                'Date Filed': [date_filed]
            })

            # Try to use ML model if available
            try:
                from predict import predict_outcome
                outcome = predict_outcome(input_data)
                return jsonify({'prediction': str(outcome[0])})
            except Exception as e:
                return jsonify({'error': f'ML model error: {str(e)}'}), 500

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return app

# For direct running
if __name__ == '__main__':
    print(" Starting Court Case Prediction System...")
    print(" JWT Authentication enabled")
    print(" AI Model: Gemini 2.0 Flash (with fallback)")
    print(" Demo users:")
    print("   - Admin: admin / admin123")
    print("   - User: user / user123")
    print(" Server starting at http://localhost:5000")
    print(" Login at: http://localhost:5000/login")
    
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
