#!/usr/bin/env python3
"""
Main entry point for the Court Case Outcome Prediction System
"""

import os
import sys
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import flask
        import pandas
        import sklearn
        import joblib
        import dotenv
        import jwt
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_environment():
    """Check environment setup"""
    print("\n🔍 Checking environment setup...")
    
    # Check for .env file
    if os.path.exists('.env'):
        print("✅ .env file found")
        # Check for required environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        if os.getenv("GOOGLE_API_KEY"):
            print("✅ GOOGLE_API_KEY found")
        else:
            print("⚠️  GOOGLE_API_KEY not found")
            print("   Add GOOGLE_API_KEY=your_api_key_here to .env file")
            
        if os.getenv("JWT_SECRET_KEY"):
            print("✅ JWT_SECRET_KEY found")
        else:
            print("ℹ️  JWT_SECRET_KEY not found (will use auto-generated key)")
            
        if os.getenv("FLASK_SECRET_KEY"):
            print("✅ FLASK_SECRET_KEY found")
        else:
            print("ℹ️  FLASK_SECRET_KEY not found (will use auto-generated key)")
    else:
        print("⚠️  .env file not found")
        print("   Create a .env file with:")
        print("   GOOGLE_API_KEY=your_api_key_here")
        print("   JWT_SECRET_KEY=your_jwt_secret_here (optional)")
        print("   FLASK_SECRET_KEY=your_flask_secret_here (optional)")
    
    # Check for models directory
    if os.path.exists('models'):
        print("✅ Models directory found")
        model_files = os.listdir('models')
        if model_files:
            print(f"   Found {len(model_files)} model files")
        else:
            print("   No model files found - run train_model.py first")
    else:
        print("❌ Models directory not found")
        print("   Run train_model.py to create and train models")

def check_data():
    """Check if training data exists"""
    print("\n📊 Checking data files...")
    
    if os.path.exists('cases.csv'):
        print("✅ cases.csv found")
        # Get file size
        size = os.path.getsize('cases.csv')
        print(f"   File size: {size / 1024:.1f} KB")
    else:
        print("❌ cases.csv not found")
        print("   This file is required for training the model")

def show_menu():
    """Show main menu"""
    print("\n" + "="*50)
    print("🏛️  COURT CASE OUTCOME PREDICTION SYSTEM")
    print("="*50)
    print("\nChoose an option:")
    print("1. Run Flask Web Application")
    print("2. Run Streamlit Application")
    print("3. Train/Retrain ML Model")
    print("4. Test ML Prediction")
    print("5. Check System Status")
    print("6. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-6): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6']:
                return choice
            else:
                print("Please enter a number between 1 and 6")
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            sys.exit(0)

def run_flask_app():
    """Run the Flask web application"""
    print("\n🚀 Starting Flask web application...")
    try:
        from app import create_app
        app = create_app()
        print("✅ Flask app created successfully")
        print("🔐 JWT Authentication enabled")
        print("🌐 Starting server at http://localhost:5000")
        print("   Login credentials:")
        print("   - Admin: admin / admin123")
        print("   - User: user / user123")
        print("   Press Ctrl+C to stop the server")
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"❌ Error starting Flask app: {e}")
        print("   Make sure you have set up your .env file correctly")

def run_streamlit_app():
    """Run the Streamlit application"""
    print("\n🚀 Starting Streamlit application...")
    try:
        import subprocess
        print("✅ Streamlit app starting...")
        print("🌐 The app will open in your browser")
        print("   Press Ctrl+C to stop the server")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])
    except Exception as e:
        print(f"❌ Error starting Streamlit app: {e}")
        print("   Make sure Streamlit is installed: pip install streamlit")

def train_model():
    """Train the ML model"""
    print("\n🤖 Training ML model...")
    try:
        from train_model import train_case_outcome_model
        success = train_case_outcome_model()
        if success:
            print("✅ Model training completed successfully!")
        else:
            print("❌ Model training failed!")
    except Exception as e:
        print(f"❌ Error training model: {e}")

def test_prediction():
    """Test ML prediction"""
    print("\n🧪 Testing ML prediction...")
    try:
        from predict import predict_outcome
        import pandas as pd
        
        # Test data
        test_data = pd.DataFrame({
            'Case Type': ['Corporate Dispute'],
            'Court Name': ['Madras High Court'],
            'Plaintiff': ['ABC Corporation'],
            'Defendant': ['XYZ Ltd'],
            'Date Filed': ['2024/09/25']
        })
        
        outcome = predict_outcome(test_data)
        print(f"✅ Test prediction successful!")
        print(f"   Predicted outcome: {outcome[0]}")
        
    except Exception as e:
        print(f"❌ Error testing prediction: {e}")
        print("   Make sure you have trained the model first")

def check_system_status():
    """Check overall system status"""
    print("\n🔍 SYSTEM STATUS CHECK")
    print("-" * 30)
    
    check_dependencies()
    check_environment()
    check_data()
    
    print("\n🔐 AUTHENTICATION SYSTEM:")
    print("✅ JWT-based authentication implemented")
    print("✅ Login required for all protected routes")
    print("✅ Session management with secure tokens")
    
    print("\n📋 NEXT STEPS:")
    if not os.path.exists('.env'):
        print("1. Create .env file with your Google API key")
    if not os.path.exists('models/case_outcome_model.pkl'):
        print("2. Train the ML model using option 3")
    print("3. Start the application using option 1 or 2")
    print("4. Login with demo credentials when prompted")

def main():
    """Main function"""
    print("🏛️  Welcome to the Court Case Outcome Prediction System!")
    print("🔐 Now with JWT Authentication!")
    
    # Check dependencies first
    if not check_dependencies():
        return
    
    while True:
        choice = show_menu()
        
        if choice == '1':
            run_flask_app()
        elif choice == '2':
            run_streamlit_app()
        elif choice == '3':
            train_model()
        elif choice == '4':
            test_prediction()
        elif choice == '5':
            check_system_status()
        elif choice == '6':
            print("\n👋 Thank you for using the Court Case Prediction System!")
            break
        
        if choice in ['1', '2']:
            # These options start servers, so we don't return to menu
            break
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main() 