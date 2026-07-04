from app import app, db, User, Issue

with app.app_context():
    # 1. Create a test admin user
    admin = User(email='admin@test.com', password='password123', role='Admin')
    db.session.add(admin)

    # 2. Create a couple of sample issues to populate the dashboard
    bug1 = Issue(title='Login button not working', description='Clicking login throws a 404 error.', status='Open', severity='Critical')
    bug2 = Issue(title='Dashboard text too small', description='Metric cards are hard to read.', status='In QA', severity='Normal')
    
    # 3. Add them to the database and save (commit) the changes
    db.session.add(bug1)
    db.session.add(bug2)
    db.session.commit()
    
    print("Test data added successfully!")