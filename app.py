from flask import Flask, render_template, request, redirect, url_for, Response
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

class TestCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Not Run')
    issue_id = db.Column(db.Integer, nullable=True)
    
    def __repr__(self):
        return f'<TestCase {self.title}>'

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
    return render_template('add_user.html')
@app.route('/delete_user/<int:id>')
def delete_user(id):
    user_to_delete = User.query.get_or_404(id)
    db.session.delete(user_to_delete)
    db.session.commit()
    return redirect(url_for('users'))
        
@app.route('/edit_user/<int:id>', methods=['GET', 'POST']) #this function helps to edit a user information without having to delete the whole thing
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

@app.route('/issues')
def issues():
    all_issues = Issue.query.order_by(Issue.date_created.desc()).all()
    return render_template('issues.html', issues=all_issues)

@app.route('/add_issue', methods=['GET', 'POST'])
def add_issue():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        status = request.form['status']
        severity = request.form['severity']
        
        new_issue = Issue(title=title, description=description, status=status, severity=severity)
        db.session.add(new_issue)
        db.session.commit()
        
        return redirect(url_for('issues'))
        
    return render_template('add_issue.html')

@app.route('/edit_issue/<int:id>', methods=['GET', 'POST'])
def edit_issue(id):
    issue_to_edit = Issue.query.get_or_404(id)
    
    if request.method == 'POST':
        issue_to_edit.title = request.form['title']
        issue_to_edit.description = request.form['description']
        issue_to_edit.status = request.form['status']
        issue_to_edit.severity = request.form['severity']
        
        db.session.commit()
        return redirect(url_for('issues'))
        
    return render_template('edit_issue.html', issue=issue_to_edit)

@app.route('/kanban')
def kanban():
    open_issues = Issue.query.filter_by(status='Open').all()
    in_qa_issues = Issue.query.filter_by(status='In QA').all()
    resolved_issues = Issue.query.filter_by(status='Resolved').all()
    
    return render_template(
        'kanban.html', 
        open_issues=open_issues, 
        in_qa_issues=in_qa_issues, 
        resolved_issues=resolved_issues
    )

@app.route('/test_cases')
def test_cases():
    all_tests = TestCase.query.all()
    return render_template('test_cases.html', test_cases=all_tests)

@app.route('/add_test_case', methods=['GET', 'POST'])
def add_test_case():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        issue_id = request.form['issue_id']
        
        if issue_id == "":
            issue_id = None
            
        new_test = TestCase(title=title, description=description, issue_id=issue_id)
        db.session.add(new_test)
        db.session.commit()
        
        return redirect(url_for('test_cases'))
        
    active_issues = Issue.query.filter(Issue.status != 'Resolved').all()
    return render_template('add_test_case.html', issues=active_issues)

@app.route('/edit_test_case/<int:id>', methods=['GET', 'POST'])
def edit_test_case(id):
    test_to_edit = TestCase.query.get_or_404(id)
    
    if request.method == 'POST':
        test_to_edit.title = request.form['title']
        test_to_edit.description = request.form['description']
        test_to_edit.status = request.form['status']
        issue_id = request.form['issue_id']
        
        if issue_id == "":
            test_to_edit.issue_id = None
        else:
            test_to_edit.issue_id = issue_id
            
        db.session.commit()
        return redirect(url_for('test_cases'))
        
    active_issues = Issue.query.filter(Issue.status != 'Resolved').all()
    return render_template('edit_test_case.html', test_case=test_to_edit, issues=active_issues)

@app.route('/release')
def release():
    total_open = Issue.query.filter(Issue.status != 'Resolved').count()
    critical_open = Issue.query.filter(Issue.status != 'Resolved', Issue.severity == 'Critical').count()
    
    total_tests = TestCase.query.count()
    passed_tests = TestCase.query.filter_by(status='Passed').count()
    blocked_tests = TestCase.query.filter_by(status='Blocked').count()
    
    pass_rate = 0
    if total_tests > 0:
        pass_rate = int((passed_tests / total_tests) * 100)
        
    if critical_open > 0 or blocked_tests > 0:
        status = "Not Ready"
        color = "#C0392B"
    elif pass_rate < 80:
        status = "Needs Review"
        color = "#F39C12"
    else:
        status = "Ready for Release"
        color = "#27AE60"
        
    return render_template('release.html', 
                           total_open=total_open, 
                           critical_open=critical_open,
                           total_tests=total_tests,
                           pass_rate=pass_rate,
                           status=status,
                           color=color)

@app.route('/export')
def export():
    issues = Issue.query.all()
    
    def generate():
        yield 'ID,Title,Status,Severity,Date\n'
        for issue in issues:
            yield f'{issue.id},"{issue.title}",{issue.status},{issue.severity},{issue.date_created.strftime("%Y-%m-%d")}\n'

    return Response(generate(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=issues_export.csv'})


if __name__ == '__main__':
    app.run(debug=True, port=5001)