from flask import Flask, render_template

app = Flask(__name__)

# Route for the homepage
@app.route('/')
def homepage():
    return render_template('homepage.html')

# Route for the About page
@app.route('/about')
def about():
    return render_template('about.html')

# Route for the Services page
@app.route('/services')
def services():
    return render_template('services.html')

# Route for the Cases page
@app.route('/cases')
def cases():
    return render_template('cases.html')

# Route for the Contact page
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Route for the Login page
@app.route('/login')
def login():
    return render_template('login.html')

# Route for ML Model Interaction page
@app.route('/ml-model-interaction')
def ml_model_interaction():
    return render_template('ml_model_interaction.html')

if __name__ == '__main__':
    app.run(debug=True)
