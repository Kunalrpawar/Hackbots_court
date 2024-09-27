from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
import joblib
import pandas as pd

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API client
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("API key not found! Please set the GOOGLE_API_KEY in your environment.")
    st.stop()

# Initialize the Gemini Pro model
model = genai.GenerativeModel("gemini-pro")

# Load ML models and encoders
# Uncomment and ensure these files exist and are correctly loaded
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

# Function to get a response from the Gemini model
def get_gemini_response(question):
    try:
        response = model.generate_content(question)
        return response.text
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# Set page config
st.set_page_config(page_title="Court Case Prediction", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stApp {
        background-color: #f8fafc;
    }
    .stButton>button {
        width: 100%;
        background-color: #3b82f6;
        color: white;
        padding: 0.75rem;
        margin-top: 0.25rem; /* Reduced margin to minimize gap */
    }
    .stButton>button:hover {
        background-color: #2563eb;
    }
    
            
            
    .user-message {
        background-color: #e0f2fe;
        color: #0c4a6e;
        padding: 0.75rem;
        border-radius: 10px;
        margin-bottom: 0.75rem;
    }
    .bot-message {
        background-color: #f0fdf4;
        color: #14532d;
        padding: 0.75rem;
        border-radius: 10px;
        margin-bottom: 0.75rem;
    }
    .stTextInput>div>div>input {
        background-color: white;
        border: 1px solid #e2e8f0;
        color: #1e293b;
    }
    .stSelectbox>div>div>div {
        background-color: white;
        border: 1px solid #e2e8f0;
        color: #1e293b;
    }
    .stDateInput>div>div>input {
        background-color: white;
        border: 1px solid #e2e8f0;
        color: #1e293b;
    }
    h1, h2, h3 {
        color: #1e293b;
    }
    .stAlert {
        background-color: #fef2f2;
        color: #991b1b;
    }
    .form-label {
        font-weight: bold;
        color: #1e293b;
        margin-bottom: 0.25rem;
        display: block;
    }
    </style>
    """, unsafe_allow_html=True)

# App title
st.title("Court Case Prediction and Chatbot")

# Create two columns
col1, col2 = st.columns([2, 1])

# Column 1: Case Prediction
with col1:
    st.header("Case Prediction")
    with st.form(key='case_form'):
        st.markdown('<p class="form-label">Case Title</p>', unsafe_allow_html=True)
        case_title = st.text_input("", placeholder="Enter case title", key="case_title")
        
        st.markdown('<p class="form-label">Date Filed</p>', unsafe_allow_html=True)
        date_filed = st.date_input("", key="date_filed")
        
        st.markdown('<p class="form-label">Case Type</p>', unsafe_allow_html=True)
        case_type = st.selectbox("", ["Civil", "Criminal", "Family", "Other"], key="case_type")
        
        st.markdown('<p class="form-label">Court Name</p>', unsafe_allow_html=True)
        court_name = st.text_input("", placeholder="Enter court name", key="court_name")
        
        st.markdown('<p class="form-label">Plaintiff</p>', unsafe_allow_html=True)
        plaintiff = st.text_input("", placeholder="Enter plaintiff's name", key="plaintiff")
        
        st.markdown('<p class="form-label">Defendant</p>', unsafe_allow_html=True)
        defendant = st.text_input("", placeholder="Enter defendant's name", key="defendant")
        
        submit = st.form_submit_button("Predict Outcome")

    if submit:
        input_data = {
            'Case Title': case_title,
            'Date Filed': date_filed,
            'Case Type': case_type,
            'Court Name': court_name,
            'Plaintiff': plaintiff,
            'Defendant': defendant
        }
        
        try:
            preprocessed_input = preprocess_input(input_data)
            prediction = case_outcome_model.predict(preprocessed_input)
            st.success(f"Predicted Outcome: {prediction[0]}")
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Column 2: Chatbot
with col2:
    st.header("Chat with the Bot")

    # Initialize session state for chat history if it doesn't exist
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    # User input for chatbot
    input_text = st.text_input("Ask the Bot:", key="chat_input")

    # Send button for chatbot
    if st.button("Send", key="send_button"):
        if input_text:
            # Add user message to chat history
            st.session_state['chat_history'].append(("You", input_text))
            
            # Get response from Gemini
            response = get_gemini_response(input_text)
            
            if response:
                # Add bot response to chat history
                st.session_state['chat_history'].append(("Bot", response))

    # Chat container (at the bottom)
    chat_container = st.container()

    # Display the chat history
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for role, text in st.session_state['chat_history']:
            if role == "You":
                st.markdown(f'<div class="user-message"><strong>{role}:</strong> {text}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bot-message"><strong>{role}:</strong> {text}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Display a message if the chat history is empty
    if not st.session_state['chat_history']:
        st.info("Start chatting by entering a message above!")
