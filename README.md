# QA Pilot: Product Validation Dashboard

QA Pilot is a lightweight, intuitive web application designed to help startup engineering and QA teams track product validation work. It provides a centralized dashboard for managing users, tracking issues, executing test cases, and evaluating release readiness.

## Features
* **Dashboard Overview:** Dynamic metrics and charts visualizing issue status and pass rates.
* **User Management:** Full CRUD capabilities for managing team members and roles.
* **Issue Tracking:** Report bugs and tasks with severity and status tracking.
* **Kanban Board:** Visual workflow board organizing issues by state (Open, In QA, Resolved).
* **Test Case Execution:** Create tests, link them to specific issues, and track Pass/Fail/Blocked status.
* **Release Readiness:** Automated launch status calculator with CSV data export.

## Technology Stack
* **Frontend:** HTML, CSS, JavaScript, Chart.js
* **Backend:** Python, Flask
* **Database:** SQLite, Flask-SQLAlchemy

## Local Setup Instructions

1. **Clone the repository**
```bash
git clone [https://github.com/Aafia19/qa-pilot.git](https://github.com/Aafia19/qa-pilot.git)
cd qa-pilot


# to set up a virtual environment, do this
python3 -m venv venv
source venv/bin/activate

#then install the dependencies
pip install -r requirements.txt

#initialise the database and run the application
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"
python3 seed.py

python3 app.py

#Default Login Credentials (from seed data)
Email: admin@test.com 
Password: password123