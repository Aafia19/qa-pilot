from flask import Flask, render_template, request, redirect, url_for
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
@app.route('/users')
def users():
    all_users = User.query.all()
    return render_template('users.html', users=all_users)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        new_user = User(email=email, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('users'))
@app.route('/delete_user/<int:id>')
def delete_user(id):
    user_to_delete = User.query.get_or_404(id)
    db.session.delete(user_to_delete)
    db.session.commit()
    return redirect(url_for('users'))
        
@app.route('/edit_user/<int:id>', methods=['GET', 'POST']). #this functions helps to edit a user information without having to delete the whole thing
def edit_user(id):
    user_to_edit = User.query.get_or_404(id)
    
    if request.method == 'POST':
        user_to_edit.email = request.form['email']
        user_to_edit.role = request.form['role']
        
        if request.form['password']:
            user_to_edit.password = request.form['password']
            
        db.session.commit()
        return redirect(url_for('users'))
        
    return render_template('edit_user.html', user=user_to_edit)
    return render_template('add_user.html')
if __name__ == '__main__':
    app.run(debug=True, port=5001)