echo "Setting up Python virtual environment..."
python -m venv venv
source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Setup completed successfully!"