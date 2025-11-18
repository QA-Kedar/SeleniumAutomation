from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit, disconnect
import threading
import subprocess
import os
from datetime import datetime
import json
import logging
from collections import deque

# Configure logging to suppress socket errors
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Suppress eventlet warnings
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'

# Configure SocketIO with proper settings
socketio = SocketIO(
    app, 
    cors_allowed_origins="*",
    logger=False,
    engineio_logger=False,
    ping_timeout=60,
    ping_interval=25
)

# Global variables
test_process = None
test_running = False
test_logs = deque(maxlen=1000)  # Store last 1000 log entries
test_stats = {
    'total': 52,
    'tested': 0,
    'passed': 0,
    'failed': 0,
    'status': 'idle'
}

# Simple auth credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"

def add_log(message, log_type='info', timestamp=None):
    """Add log to buffer and emit to connected clients"""
    if timestamp is None:
        timestamp = datetime.now().strftime('%H:%M:%S')
    
    log_entry = {
        'message': message,
        'type': log_type,
        'timestamp': timestamp
    }
    
    # Store in buffer
    test_logs.append(log_entry)
    
    # Try to emit to connected clients (won't crash if none connected)
    try:
        socketio.emit('log', log_entry)
    except:
        pass  # No clients connected, that's okay

def update_stats():
    """Emit current stats to connected clients"""
    try:
        socketio.emit('stats_update', test_stats)
    except:
        pass

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

@app.route('/api/logs')
def get_logs():
    """API endpoint to get buffered logs"""
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({'logs': list(test_logs), 'stats': test_stats})

@app.route('/api/status')
def get_status():
    """API endpoint to get current test status"""
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({
        'running': test_running,
        'stats': test_stats
    })

@socketio.on('start_tests')
def handle_start_tests():
    global test_process, test_running, test_stats
    
    if test_running:
        add_log('[WARNING] Tests are already running!', 'warning')
        return
    
    test_running = True
    test_stats['status'] = 'running'
    test_stats['tested'] = 0
    test_stats['passed'] = 0
    test_stats['failed'] = 0
    
    add_log('[INFO] Starting Selenium tests...', 'info')
    try:
        socketio.emit('test_status', {'status': 'running'})
    except:
        pass
    
    def run_tests():
        global test_process, test_running, test_stats
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
                if line and test_running:
                    # Update stats based on output
                    if '✓' in line or 'PASSED' in line:
                        test_stats['passed'] += 1
                    if 'FAILED' in line or 'ERROR' in line:
                        test_stats['failed'] += 1
                    if 'PASSED' in line or 'FAILED' in line or 'ERROR' in line:
                        test_stats['tested'] += 1
                    
                    add_log(line.strip(), 'info')
                    update_stats()
            
            test_process.wait()
            
            if test_process.returncode == 0:
                test_stats['status'] = 'completed'
                add_log('[SUCCESS] All tests passed!', 'success')
                try:
                    socketio.emit('test_status', {'status': 'completed'})
                except:
                    pass
            else:
                test_stats['status'] = 'failed'
                add_log(f'[ERROR] Tests failed with code {test_process.returncode}', 'error')
                try:
                    socketio.emit('test_status', {'status': 'failed'})
                except:
                    pass
                
        except Exception as e:
            test_stats['status'] = 'error'
            add_log(f'[ERROR] {str(e)}', 'error')
            try:
                socketio.emit('test_status', {'status': 'error'})
            except:
                pass
        finally:
            test_running = False
            test_process = None
    
    thread = threading.Thread(target=run_tests)
    thread.daemon = True
    thread.start()

@socketio.on('stop_tests')
def handle_stop_tests():
    global test_process, test_running, test_stats
    
    if not test_running:
        add_log('[WARNING] No tests are running!', 'warning')
        return
    
    if test_process:
        test_process.terminate()
        add_log('[INFO] Tests stopped by user', 'warning')
        try:
            socketio.emit('test_status', {'status': 'stopped'})
        except:
            pass
    
    test_running = False
    test_stats['status'] = 'stopped'

@socketio.on('get_buffered_logs')
def handle_get_logs():
    """Send all buffered logs to newly connected client"""
    for log_entry in test_logs:
        try:
            emit('log', log_entry)
        except:
            pass
    
    # Send current stats
    try:
        emit('stats_update', test_stats)
        emit('test_status', {'status': test_stats['status']})
    except:
        pass

@socketio.on('connect')
def handle_connect():
    if not session.get('logged_in'):
        return False
    add_log('[INFO] Client connected', 'success')
    
    # Send buffered logs to new client
    handle_get_logs()

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnect gracefully"""
    pass

@socketio.on_error_default
def default_error_handler(e):
    """Handle all socket errors gracefully"""
    pass

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)