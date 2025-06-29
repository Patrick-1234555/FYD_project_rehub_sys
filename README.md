# Rehabilitation Monitoring System

A web-based application for doctors and caregivers to monitor and manage patient rehabilitation progress.

## Features
- User authentication for doctors and caregivers
- Doctor dashboard to view and manage patients
- Caregiver dashboard to view assigned patients and submit feedback
- Patient registration and management
- Feedback submission and tracking
- User management (add/delete caregivers and doctors)

## Technologies Used
- Python 3
- Flask
- SQLite
- HTML/CSS (Jinja2 templates)

## Getting Started

### Prerequisites
- Python 3.7+
- pip
- (Optional) [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) for deployment

### Installation
1. Clone the repository or download the source code.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables in a `.env` file:
   ```env
   SECRET_KEY=your_secure_secret_key_here
   FLASK_ENV=production
   DATABASE_URL=sqlite:///rehabilitation.db
   ```
4. Run the application locally:
   ```bash
   python app.py
   ```
   The app will be available at `http://localhost:5000`.

## Deployment (Heroku)
1. Initialize git and commit your code:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```
2. Login to Heroku and create an app:
   ```bash
   heroku login
   heroku create rehabilitation-monitoring-system
   ```
3. Set buildpack and environment variables:
   ```bash
   heroku buildpacks:set heroku/python
   heroku config:set SECRET_KEY=your_secure_secret_key_here
   ```
4. Push code to Heroku:
   ```bash
   git push heroku main
   ```
5. Open your app:
   ```bash
   heroku open
   ```

## Deployment (PythonAnywhere)
1. Upload your project files to your PythonAnywhere account. Place them in a directory, e.g., `/home/yourusername/rehub/FYD_project_rehub_sys`.
2. In the PythonAnywhere dashboard, go to the **Web** tab and set up a new web app:
   - Choose **Flask** as the framework.
   - Set the source code location to your project directory.
   - Set the WSGI configuration file path to your `wsgi.py` file (e.g., `/home/yourusername/rehub/FYD_project_rehub_sys/wsgi.py`).
3. Make sure your `wsgi.py` file contains:
   ```python
   import sys
   import os
   project_home = '/home/yourusername/rehub/FYD_project_rehub_sys'
   if project_home not in sys.path:
       sys.path.append(project_home)
   os.environ['FLASK_ENV'] = 'production'
   from app import app as application
   ```
4. Install dependencies in a virtual environment:
   ```bash
   pip install -r requirements.txt
   ```
5. Reload your web app from the PythonAnywhere dashboard.
6. The default doctor credentials for testing are:
   - Username: `dr_smith`
   - Password: `doctor123`
7. Access your deployed app at:
   - https://patrick123456.pythonanywhere.com/

## Notes
- The database is initialized automatically on first run.
- For production, use a strong `SECRET_KEY` and consider using a more robust database (e.g., PostgreSQL).
- Static files and templates are located in the `templates/` directory.

## License
This project is for educational purposes.
