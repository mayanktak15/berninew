import os
import csv
import requests
import ipaddress
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
try:
    from evaluate_different_modules import process_query5,process_query2,process_query4,process_query,process_query3
    ADVANCED_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Advanced modules not available: {e}")
    ADVANCED_MODULES_AVAILABLE = False

# Import the simple FAQ responses as fallback (from existing helper module)
try:
    from evaluate_different_modules import get_simple_faq_response
    FAQ_AVAILABLE = True
except ImportError:
    print("Warning: Simple FAQ responses not available from evaluate_different_modules")
    FAQ_AVAILABLE = False

# Define safe stubs to satisfy linters and ensure symbols exist
if not ADVANCED_MODULES_AVAILABLE:
    def process_query5(query, symptoms=None):
        return None
    def process_query2(query, symptoms=None):
        return None
    def process_query4(query, symptoms=None):
        return None
    def process_query(query, symptoms=None):
        return None
    def process_query3(query, symptoms=None):
        return None

if not FAQ_AVAILABLE:
    def get_simple_faq_response(query):
        return None

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not available")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-fallback-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///docify.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configure allowed IP addresses/CIDR ranges
ALLOWED_IPS = os.getenv('ALLOWED_IPS', '127.0.0.1/32').split(',')

def is_ip_allowed(ip_address):
    """Check if the IP address is in the allowed list"""
    try:
        client_ip = ipaddress.ip_address(ip_address)
        for allowed_range in ALLOWED_IPS:
            if client_ip in ipaddress.ip_network(allowed_range, strict=False):
                return True
        return False
    except ValueError:
        return False

@app.before_request
def limit_remote_addr():
    """Middleware to check IP address before processing requests"""
    # Get client IP (handle proxy headers if behind load balancer)
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    if client_ip:
        # If behind proxy, get the first IP
        client_ip = client_ip.split(',')[0].strip()
    
    # Skip IP check for health check endpoints (optional)
    if request.endpoint in ['health', 'status']:
        return
    
    if not is_ip_allowed(client_ip):
        abort(403)  # Forbidden


@app.route('/health', methods=['GET'])
def health():
    """Simple health check endpoint"""
    return jsonify(status="ok"), 200


# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


class Consultation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    symptoms = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('consultations', lazy=True))


# Initialize Database
with app.app_context():
    db.create_all()


# Export User Details to CSV
def export_users_to_csv():
    users = User.query.all()
    with open('users.csv', 'w', newline='') as csvfile:
        fieldnames = ['id', 'name', 'phone', 'email']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for user in users:
            writer.writerow({
                'id': user.id,
                'name': user.name,
                'phone': user.phone,
                'email': user.email

            })


# Routes
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered.', 'error')
            return redirect(url_for('register'))

        new_user = User(name=name, phone=phone, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        export_users_to_csv()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'error')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        symptoms = request.form['symptoms']
        consultation = Consultation(user_id=user.id, symptoms=symptoms)
        db.session.add(consultation)
        db.session.commit()
        flash('Consultation form submitted successfully!', 'success')
        return redirect(url_for('dashboard'))

    consultations = Consultation.query.filter_by(user_id=user.id).all()
    return render_template('dash.html', user=user, consultations=consultations)


@app.route('/update_consultation/<int:id>', methods=['GET', 'POST'])
def update_consultation(id):
    if 'user_id' not in session:
        flash('Please log in to update consultations.', 'error')
        return redirect(url_for('login'))

    consultation = Consultation.query.get_or_404(id)
    if consultation.user_id != session['user_id']:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        consultation.symptoms = request.form['symptoms']
        consultation.created_at = datetime.utcnow()
        db.session.commit()
        flash('Consultation updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('update_consultation.html', consultation=consultation)


@app.route('/faq')
def faq():
    return render_template('faq.html')


# Updated Chatbot Route
@app.route('/chatbot', methods=['POST'])
def chatbot():

    data = request.json
    query = data.get('message')
    print("user query=",query)
    if not query:
        return jsonify({"reply": "Please provide a message."}), 400
    try:
        with open("query_dataset.csv", "a") as file:
            file.write(query + "\n")
    except Exception as e:
        print(f"Error while writing to file: {e}")
    # Get latest symptoms from user's consultations
    if 'user_id' in session:
        latest_consultation = Consultation.query.filter_by(user_id=session['user_id']).order_by(
            Consultation.created_at.desc()).first()
        symptoms = latest_consultation.symptoms if latest_consultation else None
    else:
        symptoms = None


    try:
        # Try advanced chatbot function first
        if ADVANCED_MODULES_AVAILABLE:
            response = process_query5(query, symptoms)
            print("Chatbot response:", response)
            
            # Check if response is valid
            if response and response.strip():
                return jsonify({"reply": response})
        
        # Fall back to simple FAQ responses
        if FAQ_AVAILABLE:
            response = get_simple_faq_response(query)
            return jsonify({"reply": response})
        else:
            # Last resort fallback
            return jsonify({"reply": "I'm sorry, I couldn't generate a response. Please try asking about Docify Online services."})
            
    except Exception as e:
        print(f"Error in chatbot endpoint: {e}")
        
        # Try FAQ fallback
        if FAQ_AVAILABLE:
            try:
                response = get_simple_faq_response(query)
                return jsonify({"reply": response})
            except Exception as e2:
                print(f"Error in FAQ fallback: {e2}")
        
        # Final fallback response
        fallback_response = """
        Welcome to Docify Online! I'm here to help you with:
        - Information about our medical consultation services
        - How to submit consultation forms
        - FAQ about our platform
        - General health information guidance
        
        What would you like to know about Docify Online?
        """
        return jsonify({"reply": fallback_response.strip()})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=5000)
