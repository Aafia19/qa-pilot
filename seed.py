from app import app, db, User, Issue, TestCase
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

with app.app_context():
    # 1. Clear existing data to avoid duplicates
    db.drop_all()
    db.create_all()

    # 2. Generate Users
    hashed_pw = generate_password_hash('password123', method='pbkdf2:sha256')
    
    users = [
        User(full_name='Aafia Irfan', department='Engineering', email='aafia@startup.com', password_hash=hashed_pw, role='Admin', status='Active'),
        User(full_name='Marcus Chen', department='Development', email='marcus@startup.com', password_hash=hashed_pw, role='Developer', status='Active'),
        User(full_name='Sarah Jenkins', department='Quality Assurance', email='sarah@startup.com', password_hash=hashed_pw, role='QA Engineer', status='Active'),
        User(full_name='David Kim', department='Product', email='david@startup.com', password_hash=hashed_pw, role='Project Manager', status='Active'),
        User(full_name='Elena Rodriguez', department='Design', email='elena@startup.com', password_hash=hashed_pw, role='Viewer', status='Inactive')
    ]
    db.session.add_all(users)
    db.session.commit()

    # 3. Generate Issues (Spread across Kanban columns)
    issues = [
        # Done & Blocked
        Issue(title='Database connection timeout on production', description='API fails to connect during peak load.', status='Done', severity='Critical'),
        Issue(title='Update company logo on login screen', description='Use the new SVG asset provided by design.', status='Done', severity='Low'),
        Issue(title='Payment gateway API returning 500 errors', description='Stripe webhooks are failing.', status='Blocked', severity='Critical'),
        
        # QA Testing
        Issue(title='Fix memory leak in data processing job', description='Container crashes after 4 hours of uptime.', status='QA Testing', severity='High'),
        Issue(title='User profile images not loading', description='S3 bucket permissions are misconfigured.', status='QA Testing', severity='Normal'),
        
        # In Progress
        Issue(title='Implement Dark Mode toggle', description='Add CSS variables for dark theme support.', status='In Progress', severity='Normal'),
        Issue(title='Optimize dashboard chart rendering', description='Chart.js is lagging with over 1000 data points.', status='In Progress', severity='High'),
        
        # To Do & Backlog
        Issue(title='Add export to PDF functionality', description='Users want to download reports as PDFs.', status='To Do', severity='Normal'),
        Issue(title='Refactor authentication middleware', description='Clean up legacy session handling code.', status='Backlog', severity='Low'),
        Issue(title='Upgrade Flask to version 3.0', description='Security patch required for dependencies.', status='Backlog', severity='Normal')
    ]
    db.session.add_all(issues)
    db.session.commit()

    # 4. Generate Test Cases (Linked to issues)
    test_cases = [
        TestCase(title='Verify DB Connection Under Load', feature_module='Backend API', steps='1. Run Locust load test\n2. Monitor active connections', expected_result='Connections remain stable under 1000 concurrent requests.', actual_result='Passed load test without timeouts.', status='Passed', issue_id=1),
        
        TestCase(title='Validate SVG Logo Rendering', feature_module='Auth UI', steps='1. Open login page\n2. Inspect logo element', expected_result='Logo is crisp and scales on mobile.', actual_result='Looks good across devices.', status='Passed', issue_id=2),
        
        TestCase(title='Test Stripe Webhook Processing', feature_module='Billing', steps='1. Trigger test payment\n2. Check webhook logs', expected_result='200 OK received from Stripe.', actual_result='Failing due to missing API keys.', status='Blocked', issue_id=3),
        
        TestCase(title='Monitor RAM usage over 12 hours', feature_module='Data Pipeline', steps='1. Start pipeline\n2. Check Grafana dashboard', expected_result='Memory stays below 2GB.', actual_result='Climbs to 4GB and crashes.', status='Failed', issue_id=4),
        
        TestCase(title='Upload and view profile picture', feature_module='User Settings', steps='1. Upload JPG\n2. Refresh page', expected_result='Image displays in header.', actual_result='', status='Not Run', issue_id=5)
    ]
    db.session.add_all(test_cases)
    db.session.commit()

    print("✅ Database successfully seeded with startup data!")