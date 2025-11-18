from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit
import threading
import subprocess
import os
from datetime import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
test_process = None
test_running = False

# Simple auth credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@socketio.on('start_tests')
def handle_start_tests():
    global test_process, test_running
    
    if test_running:
        emit('log', {'message': '[WARNING] Tests are already running!', 'type': 'warning'})
        return
    
    test_running = True
    emit('log', {'message': '[INFO] Starting Selenium tests...', 'type': 'info'})
    emit('test_status', {'status': 'running'})
    
    def run_tests():
        global test_process, test_running
        try:
            # Run pytest with JSON report
            test_process = subprocess.Popen(
                ['pytest', 'test_urls.py', '-v', '--tb=short'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Stream output
            for line in iter(test_process.stdout.readline, ''):
                if line:
                    socketio.emit('log', {
                        'message': line.strip(),
                        'type': 'info',
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    })
            
            test_process.wait()
            
            if test_process.returncode == 0:
                socketio.emit('log', {'message': '[SUCCESS] All tests passed!', 'type': 'success'})
                socketio.emit('test_status', {'status': 'completed'})
            else:
                socketio.emit('log', {'message': f'[ERROR] Tests failed with code {test_process.returncode}', 'type': 'error'})
                socketio.emit('test_status', {'status': 'failed'})
                
        except Exception as e:
            socketio.emit('log', {'message': f'[ERROR] {str(e)}', 'type': 'error'})
            socketio.emit('test_status', {'status': 'error'})
        finally:
            test_running = False
            test_process = None
    
    thread = threading.Thread(target=run_tests)
    thread.daemon = True
    thread.start()

@socketio.on('stop_tests')
def handle_stop_tests():
    global test_process, test_running
    
    if not test_running:
        emit('log', {'message': '[WARNING] No tests are running!', 'type': 'warning'})
        return
    
    if test_process:
        test_process.terminate()
        emit('log', {'message': '[INFO] Tests stopped by user', 'type': 'warning'})
        emit('test_status', {'status': 'stopped'})
    
    test_running = False

@socketio.on('connect')
def handle_connect():
    if not session.get('logged_in'):
        return False
    emit('log', {'message': '[INFO] Connected to server', 'type': 'success'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)