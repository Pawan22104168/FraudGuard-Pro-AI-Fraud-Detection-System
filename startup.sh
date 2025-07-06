#!/bin/bash
echo "Starting FraudGuard Pro AI System..."
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Installing dependencies..."
pip install -r requirements.txt
echo "Starting Flask application..."
python app.py 