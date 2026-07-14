from werkzeug.security import generate_password_hash, check_password_hash
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
    full_name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='Active')

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
    # Calculate top metric cards
    total_open = Issue.query.filter(Issue.status != 'Done').count()
    critical_issues = Issue.query.filter(Issue.severity == 'Critical', Issue.status != 'Done').count()
    in_qa_issues = Issue.query.filter_by(status='QA Testing').count()
    blockers = Issue.query.filter_by(status='Blocked').count()
    
    # Calculate live Pass Rate
    total_tests = TestCase.query.count()
    passed_tests = TestCase.query.filter_by(status='Passed').count()
    pass_rate = int((passed_tests / total_tests) * 100) if total_tests > 0 else 0
    
    # Calculate Launch Readiness Status
    if critical_issues > 0 or blockers > 0:
        readiness_status = "Not Ready"
        readiness_color = "#C0392B"
    elif pass_rate < 80:
        readiness_status = "Needs Review"
        readiness_color = "#F39C12"
    else:
        readiness_status = "Ready for Release"
        readiness_color = "#27AE60"
    
    # Data for the Chart.js Doughnut Chart
    to_do_count = Issue.query.filter(Issue.status.in_(['Backlog', 'To Do'])).count()
    in_progress_count = Issue.query.filter_by(status='In Progress').count()
    
    # Fetch 5 most recent issues for the activity feed
    recent_issues = Issue.query.order_by(Issue.date_created.desc()).limit(5).all()
    
    return render_template(
        'dashboard.html', 
        total_open=total_open, 
        critical_issues=critical_issues,
        in_qa_issues=in_qa_issues,
        blockers=blockers,
        pass_rate=pass_rate,
        to_do_count=to_do_count,
        in_progress_count=in_progress_count,
        readiness_status=readiness_status,
        readiness_color=readiness_color,
        recent_issues=recent_issues
    )
@app.route('/users')
def users():
    all_users = User.query.all()
    return render_template('users.html', users=all_users)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        full_name = request.form['full_name']
        department = request.form['department']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        
        new_user = User(full_name=full_name, department=department, email=email, password_hash=hashed_pw, role=role)
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('users'))
        
    return render_template('add_user.html')

@app.route('/delete_user/<int:id>')
def delete_user(id):
    user_to_deactivate = User.query.get_or_404(id)
    user_to_deactivate.status = 'Inactive'
    db.session.commit()
    return redirect(url_for('users'))
        
@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    user_to_edit = User.query.get_or_404(id)
    
    if request.method == 'POST':
        user_to_edit.full_name = request.form['full_name']
        user_to_edit.department = request.form['department']
        user_to_edit.email = request.form['email']
        user_to_edit.role = request.form['role']
        user_to_edit.status = request.form['status']
        
        if request.form['password']:
            user_to_edit.password_hash = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
            
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
    backlog = Issue.query.filter_by(status='Backlog').all()
    to_do = Issue.query.filter_by(status='To Do').all()
    in_progress = Issue.query.filter_by(status='In Progress').all()
    qa_testing = Issue.query.filter_by(status='QA Testing').all()
    blocked = Issue.query.filter_by(status='Blocked').all()
    done = Issue.query.filter_by(status='Done').all()
    
    return render_template(
        'kanban.html', 
        backlog=backlog, 
        to_do=to_do, 
        in_progress=in_progress, 
        qa_testing=qa_testing,
        blocked=blocked,
        done=done
    )

class TestCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    feature_module = db.Column(db.String(100), nullable=False)
    preconditions = db.Column(db.Text, nullable=True)
    steps = db.Column(db.Text, nullable=False)
    expected_result = db.Column(db.Text, nullable=False)
    actual_result = db.Column(db.Text, nullable=True)
    execution_notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Not Run')
    issue_id = db.Column(db.Integer, nullable=True)
    
    def __repr__(self):
        return f'<TestCase {self.title}>'

@app.route('/test_cases')
def test_cases():
    all_tests = TestCase.query.all()
    return render_template('test_cases.html', test_cases=all_tests)

@app.route('/add_test_case', methods=['GET', 'POST'])
def add_test_case():
    if request.method == 'POST':
        title = request.form['title']
        feature_module = request.form['feature_module']
        preconditions = request.form['preconditions']
        steps = request.form['steps']
        expected_result = request.form['expected_result']
        issue_id = request.form['issue_id']
        
        if issue_id == "":
            issue_id = None
            
        new_test = TestCase(
            title=title, 
            feature_module=feature_module,
            preconditions=preconditions,
            steps=steps,
            expected_result=expected_result,
            issue_id=issue_id
        )
        db.session.add(new_test)
        db.session.commit()
        
        return redirect(url_for('test_cases'))
        
    active_issues = Issue.query.all()
    return render_template('add_test_case.html', issues=active_issues)

@app.route('/edit_test_case/<int:id>', methods=['GET', 'POST'])
def edit_test_case(id):
    test_to_edit = TestCase.query.get_or_404(id)
    
    if request.method == 'POST':
        test_to_edit.title = request.form['title']
        test_to_edit.feature_module = request.form['feature_module']
        test_to_edit.preconditions = request.form['preconditions']
        test_to_edit.steps = request.form['steps']
        test_to_edit.expected_result = request.form['expected_result']
        test_to_edit.actual_result = request.form['actual_result']
        test_to_edit.execution_notes = request.form['execution_notes']
        test_to_edit.status = request.form['status']
        issue_id = request.form['issue_id']
        
        if issue_id == "":
            test_to_edit.issue_id = None
        else:
            test_to_edit.issue_id = issue_id
            
        db.session.commit()
        return redirect(url_for('test_cases'))
        
    active_issues = Issue.query.all()
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