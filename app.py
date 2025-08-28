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
from pymongo import MongoClient
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Debug: Print loaded environment variables (remove in production)
print(f"GOOGLE_API_KEY loaded: {'Yes' if os.getenv('GOOGLE_API_KEY') else 'No'}")
print(f"MONGODB_URL loaded: {'Yes' if os.getenv('MONGODB_URL') else 'No'}")

# MongoDB Setup
def setup_mongodb():
    try:
        mongodb_url = os.getenv('MONGODB_URL')
        if not mongodb_url:
            print("Error: MONGODB_URL not found in .env file")
            return None, None
        
        print("Connecting to MongoDB...")
        client = MongoClient(mongodb_url, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.server_info()
        
        db = client.court_db
        
        # Initialize collections
        collections = {
            'users': db.users,
            'cases': db.cases,
            'hearings': db.hearings,
            'documents': db.documents,
            'predictions': db.predictions,  # For AI predictions
            'case_filings': db.case_filings,  # For case filing service
            'hearing_schedules': db.hearing_schedules,  # For hearing schedules
            'legal_resources': db.legal_resources  # For legal resources
        }
        
        # Create indexes
        try:
            collections['users'].create_index("username", unique=True)
            collections['cases'].create_index("case_number", unique=True)
            collections['hearings'].create_index([("case_id", 1), ("date", 1)])
            print("Database indexes created successfully!")
        except Exception as e:
            print(f"Warning: Error creating indexes: {str(e)}")
        
        print("MongoDB connected successfully!")
        print(f"Connected to database: {db.name}")
        
        return client, db
        
    except Exception as e:
        print(f"MongoDB connection error: {str(e)}")
        print("\nDebug Information:")
        print("- Check if MongoDB Atlas is accessible")
        print("- Verify your IP is whitelisted in MongoDB Atlas")
        print("- Confirm username and password are correct")
        print("- Make sure your cluster is running")
        print(f"- Full error: {str(e)}")
        return None, None

# Initialize MongoDB connection
mongo_client, db = setup_mongodb()

if db is not None:
    # Set up collections if connection successful
    users_collection = db.users
    cases_collection = db.cases
    hearings_collection = db.hearings
    documents_collection = db.documents
    predictions_collection = db.predictions
    case_filings_collection = db.case_filings
    hearing_schedules_collection = db.hearing_schedules
    legal_resources_collection = db.legal_resources
    
    # Create indexes for new collections
    case_filings_collection.create_index([("case_number", 1)], unique=True)
    hearing_schedules_collection.create_index([("case_id", 1), ("hearing_date", 1)])
    legal_resources_collection.create_index([("title", "text"), ("content", "text")])
    print("Database collections initialized")
else:
    print("Warning: Application running without database connection")

# Set default secret keys
DEFAULT_SECRET_KEY = secrets.token_hex(32)
DEFAULT_JWT_SECRET = secrets.token_hex(32)

print("Using secrets:")
print(f"FLASK_SECRET_KEY: {DEFAULT_SECRET_KEY[:10]}...")
print(f"JWT_SECRET_KEY: {DEFAULT_JWT_SECRET[:10]}...")

# No default users - users must register through the registration page

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
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
    
    # Create uploads directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Configure Gemini API - Updated to Gemini 2.0 Flash
    api_key = os.getenv("GOOGLE_API_KEY")
    model = None
    if api_key:
        try:
            genai.configure(api_key=api_key)
            # Use Gemini 2.0 Flash for better performance
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            print("Gemini 2.0 Flash model loaded successfully!")
        except Exception as e:
            print(f"Error loading Gemini 2.0 Flash: {e}")
            try:
                # Fallback to Gemini 1.5 Pro if 2.0 fails
                model = genai.GenerativeModel("gemini-1.5-pro")
                print("Fallback to Gemini 1.5 Pro model loaded!")
            except Exception as e2:
                print(f"Error loading Gemini 1.5 Pro: {e2}")
                model = None
    else:
        print("Warning: GOOGLE_API_KEY not found. AI features will be disabled.")

    def token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'token' not in session:
                print("No token in session")
                return redirect(url_for('login'))
            
            try:
                jwt.decode(session['token'], app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
                print("Token verified successfully")
                return f(*args, **kwargs)
            except Exception as e:
                print(f"Token verification error: {str(e)}")
                session.clear()
                return redirect(url_for('login'))
        return decorated

    # Test connection route
    @app.route('/test-connection')
    def test_connection():
        results = {}
        
        # Test MongoDB
        if db is not None:
            try:
                # Test basic connection
                db.command('ping')
                results['mongodb'] = 'Connected successfully'
                
                # Test collections
                user_count = users_collection.count_documents({})
                results['users_count'] = user_count
                
            except Exception as e:
                results['mongodb_error'] = str(e)
        else:
            results['mongodb'] = 'Not connected'
        
        # Test Gemini API
        if model:
            try:
                test_response = model.generate_content("Hello, this is a test.")
                results['gemini'] = 'Connected successfully'
            except Exception as e:
                results['gemini_error'] = str(e)
        else:
            results['gemini'] = 'API key not configured'
        
        return jsonify(results)

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

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'GET':
            return render_template('register.html')

        if request.method == 'POST':
            try:
                username = request.form.get('username', '').strip().lower()
                password = request.form.get('password', '').strip()
                email = request.form.get('email', '').strip().lower()

                if not all([username, password, email]):
                    flash('All fields are required', 'error')
                    return render_template('register.html')

                if db is None:
                    flash('Database connection error. Please try again later.', 'error')
                    return render_template('register.html')

                # Check if username already exists
                if users_collection.find_one({'username': username}):
                    flash('Username already exists', 'error')
                    return render_template('register.html')

                # Create new user
                new_user = {
                    'username': username,
                    'password': generate_password_hash(password),
                    'email': email,
                    'role': 'user',
                    'created_at': datetime.datetime.utcnow()
                }

                users_collection.insert_one(new_user)
                logger.info(f"New user registered: {username}")
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))

            except Exception as e:
                logger.error(f"Registration error: {str(e)}")
                flash('Registration failed. Please try again.', 'error')
                return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        # Clear any existing session
        if request.method == 'GET':
            session.clear()
            return render_template('login.html')
            
        if request.method == 'POST':
            try:
                username = request.form.get('username', '').strip().lower()
                password = request.form.get('password', '').strip()
                
                if not all([username, password]):
                    flash('Username and password are required', 'error')
                    return render_template('login.html')

                if db is None:
                    logger.error("Database connection is not available")
                    flash('Database connection error. Please try again later.', 'error')
                    return render_template('login.html')
                
                # Find user in database
                user = users_collection.find_one({'username': username})
                
                if user and check_password_hash(user['password'], password):
                    # Create new session
                    session.clear()
                    
                    # Create JWT token
                    now = datetime.datetime.now(datetime.timezone.utc)
                    token_data = {
                        'user_id': str(user['_id']),
                        'username': username,
                        'role': user['role'],
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
                    session['user_id'] = str(user['_id'])
                    session['role'] = user['role']
                    
                    print(f"User {username} logged in successfully")
                    return redirect(url_for('welcome'))
                    
                else:
                    flash('Invalid username or password', 'error')
                    
            except Exception as e:
                print(f"Login error: {str(e)}")
                session.clear()
                flash('Login error. Please try again.', 'error')
        
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        username = session.get('username', 'Unknown')
        session.clear()
        flash('Logged out successfully!', 'success')
        print(f"User {username} logged out")
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
        try:
            # Fetch all cases from MongoDB
            logger.info("Fetching cases from MongoDB")
            cases = list(case_filings_collection.find({}).sort('filing_date', -1))
            logger.info(f"Found {len(cases)} cases")
            logger.debug(f"Cases data: {cases}")
            return render_template('cases.html', cases=cases)
        except Exception as e:
            logger.error(f"Error fetching cases: {str(e)}")
            flash("Error fetching case data", "error")
            return render_template('cases.html', cases=[])

    @app.route('/contact')
    @token_required
    def contact():
        return render_template('contact.html')

    @app.route('/ai_model')
    @token_required
    def ai_model():
        print(f"AI Model page accessed by user: {session.get('username')}")
        # Get recent predictions for this user
        recent_predictions = []
        if db is not None:
            try:
                predictions = predictions_collection.find(
                    {'user_id': session.get('user_id')},
                    {'_id': 1, 'case_id': 1, 'case_type': 1, 'status': 1, 'created_at': 1}
                ).sort('created_at', -1).limit(5)
                recent_predictions = list(predictions)
            except Exception as e:
                logger.error(f"Error fetching predictions: {str(e)}")
        return render_template('ai.html', recent_predictions=recent_predictions)

    @app.route('/prediction/<prediction_id>')
    @token_required
    def view_prediction(prediction_id):
        if db is None:
            flash('Database connection error', 'error')
            return redirect(url_for('ai_model'))
            
        try:
            prediction = predictions_collection.find_one({'_id': ObjectId(prediction_id)})
            if not prediction:
                flash('Prediction not found', 'error')
                return redirect(url_for('ai_model'))
                
            # Check if the prediction belongs to the current user
            if str(prediction['user_id']) != session.get('user_id'):
                flash('Unauthorized access', 'error')
                return redirect(url_for('ai_model'))
                
            return render_template('prediction_details.html', prediction=prediction)
            
        except Exception as e:
            logger.error(f"Error retrieving prediction: {str(e)}")
            flash('Error retrieving prediction details', 'error')
            return redirect(url_for('ai_model'))

    # Service page routes
    @app.route('/case-filing', methods=['GET'])
    @token_required
    def case_filing():
        # Get recent filings for the current user
        recent_filings = []
        if db is not None:
            try:
                user_id = session.get('user_id')
                logger.info(f"Fetching recent filings for user_id: {user_id}")
                
                # Debug: Print total number of documents in collection
                total_docs = case_filings_collection.count_documents({})
                logger.info(f"Total documents in case_filings collection: {total_docs}")
                
                # Get recent filings
                recent_filings = case_filings_collection.find(
                    {'user_id': user_id}
                ).sort('filing_date', -1).limit(5)
                
                recent_filings = list(recent_filings)
                logger.info(f"Found {len(recent_filings)} recent filings")
                
            except Exception as e:
                logger.error(f"Error fetching recent filings: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
        else:
            logger.error("Database is not connected")
            
        return render_template('case_filing.html', recent_filings=recent_filings)

    @app.route('/submit-case-filing', methods=['POST'])
    @token_required
    def submit_case_filing():
        if db is None:
            flash('Database connection error', 'error')
            return redirect(url_for('case_filing'))

        try:
            # Log form data for debugging
            logger.info(f"Received case filing form data: {request.form}")
            
            # Generate unique case number
            case_number = f"CASE-{datetime.datetime.now().strftime('%Y%m%d')}-{secrets.randbelow(10000):04d}"
            logger.info(f"Generated case number: {case_number}")
            
            # Create case filing document
            filing_data = {
                'case_number': case_number,
                'case_type': request.form.get('case_type'),
                'filing_date': datetime.datetime.strptime(request.form.get('filing_date'), '%Y-%m-%d'),
                'plaintiff_name': request.form.get('plaintiff_name'),
                'defendant_name': request.form.get('defendant_name'),
                'case_description': request.form.get('case_description'),
                'court_name': request.form.get('court_name'),
                'lawyer_name': request.form.get('lawyer_name'),
                'user_id': session.get('user_id'),
                'username': session.get('username'),
                'status': 'pending',
                'created_at': datetime.datetime.utcnow()
            }

            # Handle file uploads
            if 'documents' in request.files:
                files = request.files.getlist('documents')
                document_ids = []
                for file in files:
                    if file and file.filename:
                        # Save file details in documents collection
                        doc_data = {
                            'filename': file.filename,
                            'case_number': case_number,
                            'content_type': file.content_type,
                            'uploaded_at': datetime.datetime.utcnow(),
                            'user_id': session.get('user_id')
                        }
                        result = documents_collection.insert_one(doc_data)
                        document_ids.append(str(result.inserted_id))
                        
                        # Save file to filesystem
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], str(result.inserted_id)))
                
                filing_data['document_ids'] = document_ids

            # Insert filing data
            logger.info(f"Attempting to insert case filing: {filing_data}")
            result = case_filings_collection.insert_one(filing_data)
            
            # Verify the insertion
            inserted_id = result.inserted_id
            logger.info(f"Document inserted with ID: {inserted_id}")
            
            # Verify we can retrieve the inserted document
            inserted_doc = case_filings_collection.find_one({'_id': inserted_id})
            if inserted_doc:
                logger.info("Successfully verified document insertion")
            else:
                logger.error("Failed to verify document insertion")
            
            flash(f'Case filing submitted successfully. Case Number: {case_number}', 'success')
            return redirect(url_for('case_filing'))

        except Exception as e:
            logger.error(f"Error submitting case filing: {str(e)}")
            flash('Error submitting case filing. Please try again.', 'error')
            return redirect(url_for('case_filing'))
        
    @app.route('/hearing-schedule', methods=['GET'])
    @token_required
    def hearing_schedule():
        upcoming_hearings = []
        if db is not None:
            try:
                # Get hearings scheduled for today or future
                today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                upcoming_hearings = hearing_schedules_collection.find({
                    'hearing_date': {'$gte': today}
                }).sort('hearing_date', 1).limit(10)
                upcoming_hearings = list(upcoming_hearings)
            except Exception as e:
                logger.error(f"Error fetching upcoming hearings: {str(e)}")
        return render_template('hearing_schedule.html', upcoming_hearings=upcoming_hearings)

    @app.route('/submit-hearing', methods=['POST'])
    @token_required
    def submit_hearing():
        if db is None:
            flash('Database connection error', 'error')
            return redirect(url_for('hearing_schedule'))

        try:
            # Verify case exists
            case = case_filings_collection.find_one({'case_number': request.form.get('case_number')})
            if not case:
                flash('Invalid case number', 'error')
                return redirect(url_for('hearing_schedule'))

            # Create hearing schedule document
            hearing_data = {
                'case_number': request.form.get('case_number'),
                'hearing_type': request.form.get('hearing_type'),
                'hearing_date': datetime.datetime.strptime(request.form.get('hearing_date'), '%Y-%m-%d'),
                'hearing_time': datetime.datetime.strptime(request.form.get('hearing_time'), '%H:%M'),
                'judge_name': request.form.get('judge_name'),
                'courtroom': request.form.get('courtroom'),
                'user_id': session.get('user_id'),
                'username': session.get('username'),
                'created_at': datetime.datetime.utcnow(),
                'status': 'scheduled'
            }

            # Insert hearing data
            result = hearing_schedules_collection.insert_one(hearing_data)
            
            flash('Hearing scheduled successfully', 'success')
            return redirect(url_for('hearing_schedule'))

        except Exception as e:
            logger.error(f"Error scheduling hearing: {str(e)}")
            flash('Error scheduling hearing. Please try again.', 'error')
            return redirect(url_for('hearing_schedule'))
        
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
                
            # Create prediction document
            prediction_data = {
                'case_id': case_id,
                'case_type': case_type,
                'plaintiff_name': plaintiff_name,
                'plaintiff_args': plaintiff_args,
                'defendant_name': defendant_name,
                'defendant_args': defendant_args,
                'date_filed': date_filed,
                'legal_principles': legal_principles,
                'judge_name': judge_name,
                'court_name': court_name,
                'user_id': session.get('user_id'),
                'username': session.get('username'),
                'created_at': datetime.datetime.utcnow(),
                'status': 'pending'
            }

            # Use Gemini AI for prediction if available
            if model:
                try:
                    print(f"Using Gemini model for prediction")
                    
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
                    
                    print("Sending IPC prompt to Gemini...")
                    ipc_response = model.generate_content(ipc_prompt).text
                    print("IPC response received")
                    
                    print("Sending judgment prompt to Gemini...")
                    judgment_response = model.generate_content(judgment_prompt).text
                    print("Judgment response received")
                    
                    # Update prediction data with AI responses
                    prediction_data.update({
                        'ipc_analysis': ipc_response,
                        'judgment_prediction': judgment_response,
                        'status': 'completed',
                        'completed_at': datetime.datetime.utcnow()
                    })
                    
                except Exception as e:
                    print(f"AI API Error: {e}")
                    import traceback
                    traceback.print_exc()
                    ipc_response = f"AI prediction error: {str(e)}"
                    judgment_response = f"AI prediction error: {str(e)}"
                    
                    # Update prediction data with error
                    prediction_data.update({
                        'status': 'error',
                        'error_message': str(e),
                        'completed_at': datetime.datetime.utcnow()
                    })
            else:
                ipc_response = "AI features disabled - API key not configured"
                judgment_response = "AI features disabled - API key not configured"
                
                # Update prediction data with disabled status
                prediction_data.update({
                    'status': 'disabled',
                    'error_message': 'AI features disabled - API key not configured',
                    'completed_at': datetime.datetime.utcnow()
                })
            
            # Store prediction in database
            if db is not None:
                try:
                    result = predictions_collection.insert_one(prediction_data)
                    prediction_data['_id'] = str(result.inserted_id)
                    logger.info(f"Prediction stored with ID: {result.inserted_id}")
                except Exception as e:
                    logger.error(f"Error storing prediction: {str(e)}")

            return jsonify({
                'prediction_id': str(prediction_data.get('_id')),
                'ipc_response': ipc_response,
                'response': judgment_response,
                'status': prediction_data['status']
            })
            
        except Exception as e:
            print(f"General error in predict_case: {e}")
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

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404 if os.path.exists('templates/404.html') else ("Page not found", 404)

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500 if os.path.exists('templates/500.html') else ("Internal server error", 500)

    return app

# For direct running
if __name__ == '__main__':
    print("=" * 60)
    print("Starting Court Case Prediction System...")
    print("=" * 60)
    print("Configuration:")
    print(f"- MongoDB: {'Connected' if db is not None else 'Not Connected'}")
    print(f"- Gemini API: {'Configured' if os.getenv('GOOGLE_API_KEY') else 'Not Configured'}")
    print("- JWT Authentication: Enabled")
    print("- AI Model: Gemini 2.0 Flash (with fallback)")
    print("\nServer Details:")
    print("   - URL: http://localhost:5000")
    print("   - Login: http://localhost:5000/login")
    print("   - Test Connection: http://localhost:5000/test-connection")
    print("=" * 60)
    
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)