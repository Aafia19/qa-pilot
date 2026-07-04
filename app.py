from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'qa_pilot.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# --- Database Models ---

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='Tester') # Admin, Developer, or Tester
    
    def __repr__(self):
        return f'<User {self.email}>'

class Issue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Open') # Open, In QA, Resolved
    severity = db.Column(db.String(20), default='Normal') # Critical, High, Normal, Low
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Issue {self.title}>'

# --- Routes ---

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # Fetch actual counts from the database
    total_issues = Issue.query.count()
    critical_issues = Issue.query.filter_by(severity='Critical').count()
    in_qa_issues = Issue.query.filter_by(status='In QA').count()
    
    # Send those numbers to the HTML template
    return render_template(
        'dashboard.html', 
        total_issues=total_issues, 
        critical_issues=critical_issues,
        in_qa_issues=in_qa_issues
    )

if __name__ == '__main__':
    app.run(debug=True, port=5001)