import sys
import os

# Add your project directory to the sys.path
project_home = '/home/patrick123456/rehub/FYD_project_rehub_sys'
if project_home not in sys.path:
    sys.path.append(project_home)

# Set environment variables if needed
os.environ['FLASK_ENV'] = 'production'

# Import the Flask app
from app import app as application
