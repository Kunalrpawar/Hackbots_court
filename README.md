# 🏛️ Court Case Outcome Prediction System

An intelligent system that combines traditional Machine Learning with AI-powered analysis to predict court case outcomes and generate legal judgments.

## ✨ Features

- **Machine Learning Predictions**: Uses trained Random Forest models for case outcome prediction
- **AI-Powered Analysis**: Google Gemini AI integration for detailed case analysis
- **IPC Section Recommendations**: Automatic identification of applicable legal sections
- **Judgment Generation**: AI-generated legal judgments with reasoning
- **Dual Interface**: Both Flask web application and Streamlit interface
- **Professional UI**: Modern, responsive design with comprehensive styling
- **🔐 JWT Authentication**: Secure login system with session management

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in your project directory:

```env
# Google Gemini AI API Key
GOOGLE_API_KEY=your_google_api_key_here

# JWT Secret Key (optional - auto-generated if not provided)
JWT_SECRET_KEY=your_jwt_secret_key_here

# Flask Secret Key (optional - auto-generated if not provided)
FLASK_SECRET_KEY=your_flask_secret_key_here
```

**To get a Google API key:**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy and paste it into your `.env` file

### 3. Train the ML Model

```bash
python train_model.py
```

This will:
- Load your `cases.csv` dataset
- Train a Random Forest classifier
- Save the trained model and encoders to the `models/` directory

### 4. Run the Application

#### Option A: Use the Main Menu (Recommended)
```bash
python main.py
```

This provides an interactive menu to:
- Check system status
- Train/retrain models
- Test predictions
- Launch web applications

#### Option B: Run Flask App Directly
```bash
python app.py
```



## 🔐 Authentication System

The system now includes **JWT-based authentication** for enhanced security:

### Default Login Credentials
- **Admin User**: `admin` / `admin123`
- **Regular User**: `user` / `user123`

### Security Features
- JWT tokens with 24-hour expiration
- Protected routes requiring authentication
- Secure session management
- Automatic token validation
- Logout functionality

### How It Works
1. **First Visit**: Redirected to login page
2. **Authentication**: Enter credentials to get JWT token
3. **Access**: All protected routes become accessible
4. **Session**: Token stored securely in session
5. **Logout**: Clear session and return to login

## 📁 Project Structure

```
court/
├── app.py                 # Main Flask application with JWT auth
├── streamlit_app.py       # Streamlit interface
├── main.py               # Unified entry point
├── train_model.py        # ML model training
├── predict.py            # ML prediction functions
├── requirements.txt      # Python dependencies
├── cases.csv            # Training dataset
├── models/              # Trained ML models
├── templates/           # HTML templates
│   ├── login.html      # JWT authentication page
│   ├── homepage.html   # Protected main page
│   └── ...            # Other protected templates
├── static/              # CSS, images, and static files
├── utlis/               # Utility modules
└── README.md            # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GOOGLE_API_KEY` | Google Gemini AI API key | Yes | - |
| `JWT_SECRET_KEY` | JWT signing secret | No | Auto-generated |
| `FLASK_SECRET_KEY` | Flask session secret | No | Auto-generated |

### Model Configuration

The ML model uses these features:
- Case Type (encoded)
- Court Name (encoded)
- Plaintiff (encoded)
- Defendant (encoded)
- Date Filed (timestamp)

## 📊 Data Requirements

Your `cases.csv` should contain these columns:
- `Case Type`: Type of legal case
- `Court Name`: Name of the court
- `Plaintiff`: Plaintiff's name
- `Defendant`: Defendant's name
- `Date Filed`: Date when case was filed
- `Outcome`: Target variable for prediction

## 🎯 Usage

### Web Interface (Flask)

1. **First Access**: Navigate to `http://localhost:5000`
2. **Login**: Use provided credentials
3. **Access Features**: 
   - Main form for ML predictions
   - AI model page for AI-powered analysis
   - Other pages: About, Services, Cases, Contact
4. **Logout**: Use logout button in navigation

### Streamlit Interface

1. Run `streamlit run streamlit_app.py`
2. Use the sidebar navigation
3. Fill in case details
4. Get AI-powered predictions

### API Endpoints

- `POST /predict`: AI-powered case analysis (requires auth)
- `POST /ml_predict`: ML model predictions (requires auth)
- `GET /login`: Authentication page
- `POST /login`: Login endpoint
- `GET /logout`: Logout endpoint

## 🛠️ Development

### Adding New Features

1. **New ML Models**: Extend `train_model.py`
2. **New Predictions**: Add functions to `predict.py`
3. **New UI Pages**: Create templates and add routes to `app.py`
4. **New Utilities**: Add modules to the `utlis/` directory

### Authentication Extensions

1. **New Users**: Modify the `USERS` dictionary in `app.py`
2. **Role-Based Access**: Extend the `@token_required` decorator
3. **Database Integration**: Replace mock user system with real database
4. **Password Hashing**: Implement secure password storage

### Testing

```bash
# Test ML prediction
python predict.py

# Test model training
python train_model.py

# Check system status
python main.py
# Then select option 5
```

## 🐛 Troubleshooting

### Common Issues

1. **"Model file not found"**
   - Run `python train_model.py` first
   - Check if `models/` directory exists

2. **"API key not found"**
   - Create `.env` file with your Google API key
   - Restart the application

3. **"Missing dependencies"**
   - Run `pip install -r requirements.txt`
   - Check Python version compatibility

4. **"Dataset not found"**
   - Ensure `cases.csv` exists in the project root
   - Check file permissions

5. **"Authentication failed"**
   - Use correct credentials: admin/admin123 or user/user123
   - Check if JWT tokens are properly configured

### Debug Mode

Enable debug mode in Flask:
```python
app.run(debug=True)
```

## 📈 Performance

- **ML Model**: Random Forest with ~80-90% accuracy (varies by dataset)
- **AI Analysis**: Real-time Gemini AI responses
- **Response Time**: ML predictions < 100ms, AI analysis 2-5 seconds
- **Authentication**: JWT validation < 10ms

## 🔒 Security Notes

- **JWT tokens** with secure signing
- **Session management** with automatic expiration
- **Protected routes** requiring authentication
- **Input validation** on all endpoints
- **Error handling** prevents information leakage
- **API keys** stored in environment variables
- For production, use proper secret management and HTTPS

## 📝 License

This project is for educational and research purposes. Always consult qualified legal professionals for actual legal advice.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the code comments
3. Check system status with `python main.py` option 5
4. Verify authentication credentials

---

**Note**: This system is designed for educational purposes and should not replace professional legal consultation. 