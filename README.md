Selenium Pytest Automation with Flask Dashboard
📁 Project Structure
selenium-test-automation/
├── app.py                      # Main Flask application
├── test_urls.py               # Selenium pytest tests
├── requirements.txt           # Python dependencies
├── Procfile                   # Railway deployment config
├── railway.json              # Railway build config
├── nixpacks.toml             # Nixpacks configuration
├── runtime.txt               # Python version
├── pytest.ini                # Pytest configuration
└── templates/
    ├── login.html            # Login page
    └── index.html            # Main dashboard
🚀 Local Setup
Prerequisites

Python 3.11+
Chrome/Chromium browser
ChromeDriver

Installation Steps

Clone or create the project directory:

bashmkdir selenium-test-automation
cd selenium-test-automation

Create virtual environment:

bashpython -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install dependencies:

bashpip install -r requirements.txt

Install ChromeDriver:

bash# Using webdriver-manager (automatic)
# Or manually download from: https://chromedriver.chromium.org/

Create templates folder:

bashmkdir templates

Add all files to their respective locations
Run the application:

bashpython app.py

Access the dashboard:


Open browser: http://localhost:5000
Login: admin / admin

🌐 Railway Deployment
Step 1: Prepare Repository

Initialize Git repository:

bashgit init
git add .
git commit -m "Initial commit"

Create GitHub repository and push:

bashgit remote add origin <your-repo-url>
git push -u origin main
Step 2: Deploy on Railway

Go to Railway.app
Sign in with GitHub
Click "New Project"
Select "Deploy from GitHub repo"
Choose your repository

Step 3: Configure Environment
Railway will automatically:

Detect Python
Install Chrome and ChromeDriver via nixpacks.toml
Install dependencies from requirements.txt
Start the application

Step 4: Configure Variables (Optional)
In Railway dashboard, add environment variables:

PORT: Auto-set by Railway
SECRET_KEY: Your secret key for Flask sessions

Step 5: Access Your App
Railway will provide a URL like: https://your-app.railway.app
🔐 Login Credentials

Username: admin
Password: admin

⚠️ Important: Change these credentials in app.py for production!
🎮 How to Use

Login with credentials
Click "START TESTS" to begin URL testing
Watch real-time logs in the dashboard
Monitor statistics: Total URLs, Tested, Passed, Failed
Click "STOP TESTS" to halt execution
Click "CLEAR LOGS" to reset the log panel

📊 Features
✅ Real-time WebSocket communication
✅ Live log streaming
✅ URL status code validation
✅ Page load testing
✅ Hacker-themed UI with Matrix effect
✅ Start/Stop/Clear controls
✅ Statistics dashboard
✅ Session-based authentication
✅ Mobile responsive design
✅ Railway deployment ready
🧪 Testing Features
The Selenium tests check:

HTTP status code (200)
Page load success
Page title presence
Body element existence
Load time measurement

📝 Pytest Configuration
Create pytest.ini for better output:
ini[pytest]
addopts = -v --tb=short --color=yes
testpaths = .
python_files = test_*.py
python_classes = Test*
python_functions = test_*
🐛 Troubleshooting
Local Issues
ChromeDriver not found:
bashpip install webdriver-manager
Port already in use:
Change port in app.py:
pythonport = int(os.environ.get('PORT', 5001))  # Change to 5001
Railway Issues
Build fails:

Check nixpacks.toml has correct Chrome packages
Verify all files are committed to Git

App crashes:

Check Railway logs for errors
Ensure Procfile and railway.json are correct

Tests don't run:

ChromeDriver might not be installed
Check Railway build logs

🔒 Security Notes

Change default credentials before deployment
Use environment variables for sensitive data
Enable HTTPS on Railway (automatic)
Add rate limiting for production use
Implement proper session management

📈 Scaling
For large-scale testing:

Use Railway Pro plan (more resources)
Implement job queues (Celery + Redis)
Add database for test history
Implement test scheduling
Add email notifications

🎨 UI Customization
To modify the theme, edit CSS in templates:

Change colors: #00ff41 (green) to your preference
Modify fonts in font-family properties
Adjust animations and effects
Customize Matrix rain effect

📦 Additional Dependencies
If you need more features, install:
bash# For database
pip install flask-sqlalchemy

# For Redis/Celery
pip install celery redis

# For email notifications
pip install flask-mail

# For API endpoints
pip install flask-restful
🌟 Future Enhancements

 Test history database
 Scheduled test runs
 Email/Slack notifications
 CSV export of results
 Screenshot capture on failures
 Multiple user accounts
 Test configuration UI
 API endpoints for CI/CD

📄 License
MIT License - Feel free to modify and use!
👨‍💻 Support
For issues or questions:

Check Railway logs
Review pytest output
Verify ChromeDriver compatibility
Check network connectivity


Built with: Flask, Selenium, Pytest, SocketIO, Railway