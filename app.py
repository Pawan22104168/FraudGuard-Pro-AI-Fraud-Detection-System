from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import pandas as pd
import numpy as np
from fraud_detection import FraudDetectionSystem
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import requests

load_dotenv()

# Note: HF_API_TOKEN is no longer used, but kept for compatibility
# The chatbot now uses GEMINI_API_KEY
key = os.getenv("HF_API_TOKEN")
app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.secret_key = 'your-secret-key-here'  # Required for flashing messages

# Create uploads directory if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize fraud detection system
fraud_system = FraudDetectionSystem()
try:
    fraud_system.load_model('fraud_detection_model.joblib')
    print("Model loaded from fraud_detection_model.joblib")
    print("Model loaded successfully")
except Exception as e:
    print(f"Error loading model: {str(e)}")
    print("Please ensure fraud_detection_model.joblib exists in the current directory")

def format_time(seconds):
    """Convert seconds to readable time format"""
    try:
        return datetime.fromtimestamp(seconds).strftime('%H:%M:%S')
    except Exception:
        return str(seconds)

@app.route('/chat', methods=['POST'])
def chat():
    user_message = ''
    if request.is_json and request.json is not None:
        user_message = request.json.get('message', '')
    
    # Import and use the updated chatbot
    from chatbot import ask_huggingface
    try:
        reply = ask_huggingface(user_message)
    except Exception as e:
        reply = f"Error processing your question: {str(e)}"
    
    return jsonify({'reply': reply})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/saved_advice')
def saved_advice():
    return render_template('saved_advice.html')

@app.route('/transaction_history')
def transaction_history():
    # Sample transaction history data for demonstration
    # In a real app, this would come from a database
    sample_history = [
        {
            'date': '2024-01-15',
            'amount': 1250.50,
            'status': 'Legitimate',
            'risk_score': 0.15,
            'category': 'Online Purchase'
        },
        {
            'date': '2024-01-14',
            'amount': 5000.00,
            'status': 'Fraudulent',
            'risk_score': 0.89,
            'category': 'ATM Withdrawal'
        },
        {
            'date': '2024-01-13',
            'amount': 75.25,
            'status': 'Legitimate',
            'risk_score': 0.12,
            'category': 'Restaurant'
        },
        {
            'date': '2024-01-12',
            'amount': 2500.00,
            'status': 'Fraudulent',
            'risk_score': 0.92,
            'category': 'Online Transfer'
        },
        {
            'date': '2024-01-11',
            'amount': 45.80,
            'status': 'Legitimate',
            'risk_score': 0.08,
            'category': 'Gas Station'
        },
        {
            'date': '2024-01-10',
            'amount': 1200.00,
            'status': 'Legitimate',
            'risk_score': 0.22,
            'category': 'Shopping'
        },
        {
            'date': '2024-01-09',
            'amount': 3500.00,
            'status': 'Fraudulent',
            'risk_score': 0.87,
            'category': 'Online Purchase'
        },
        {
            'date': '2024-01-08',
            'amount': 89.99,
            'status': 'Legitimate',
            'risk_score': 0.11,
            'category': 'Subscription'
        }
    ]
    
    # Calculate statistics
    total_transactions = len(sample_history)
    fraud_count = sum(1 for t in sample_history if t['status'] == 'Fraudulent')
    legitimate_count = total_transactions - fraud_count
    total_amount = sum(t['amount'] for t in sample_history)
    fraud_amount = sum(t['amount'] for t in sample_history if t['status'] == 'Fraudulent')
    
    # Calculate percentages
    fraud_percentage = (fraud_count / total_transactions * 100) if total_transactions > 0 else 0
    legitimate_percentage = (legitimate_count / total_transactions * 100) if total_transactions > 0 else 0
    
    # Prepare chart data
    chart_data = {
        'labels': ['Legitimate', 'Fraudulent'],
        'data': [legitimate_count, fraud_count],
        'colors': ['#10b981', '#dc2626']
    }
    
    # Monthly trend data
    monthly_data = {
        'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'legitimate': [12, 15, 18, 14, 16, 20],
        'fraudulent': [2, 3, 1, 4, 2, 1]
    }
    
    return render_template('transaction_history.html',
                         transactions=sample_history,
                         total_transactions=total_transactions,
                         fraud_count=fraud_count,
                         legitimate_count=legitimate_count,
                         fraud_percentage=round(fraud_percentage, 1),
                         legitimate_percentage=round(legitimate_percentage, 1),
                         total_amount="{:,.2f}".format(total_amount),
                         fraud_amount="{:,.2f}".format(fraud_amount),
                         chart_data=chart_data,
                         monthly_data=monthly_data)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    if not file or not file.filename or file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and file.filename and file.filename.endswith('.csv'):
        try:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            print(f"File saved to: {filepath}")
            
            try:
                df = pd.read_csv(filepath)
                print(f"CSV loaded with columns: {list(df.columns)}")
                print(f"CSV shape: {df.shape}")
                
                # Try to find the required features
                required_features = ['V1', 'V2', 'V3']
                
                # If V1, V2, V3 don't exist, try to use first 3 numeric columns
                if not all(col in df.columns for col in required_features):
                    print("V1, V2, V3 not found, looking for alternative columns...")
                    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                    
                    # Remove common non-feature columns
                    exclude_cols = ['Class', 'IsFraud', 'Time', 'Amount', 'TransactionAmount', 'TimeSinceLast']
                    feature_cols = [col for col in numeric_cols if col not in exclude_cols]
                    
                    if len(feature_cols) >= 3:
                        required_features = feature_cols[:3]
                        print(f"Using first 3 numeric columns as features: {required_features}")
                    else:
                        flash(f"Not enough numeric columns found. Found: {feature_cols}. Need at least 3 numeric columns for analysis.")
                        return redirect(url_for('index'))
                
                try:
                    # Use the required features for prediction
                    X = df[required_features].fillna(0)
                    print(f"Features shape: {X.shape}")
                    print(f"Using features: {required_features}")
                    
                    predictions, probabilities = fraud_system.predict(X)
                    print(f"Predictions made: {len(predictions)}")
                    
                    results_data = []
                    for idx, row in df.iterrows():
                        row_dict = dict(row)
                        
                        # Try to get Time and Amount from various possible column names
                        time_col = next((col for col in ['Time', 'TimeSinceLast'] if col in row_dict), '')
                        amount_col = next((col for col in ['Amount', 'TransactionAmount'] if col in row_dict), '')
                        
                        result = {
                            'Time': row_dict.get(time_col, ''),
                            'Amount': row_dict.get(amount_col, ''),
                            'prediction': int(predictions[idx]),
                            'probability': float(probabilities[idx]),
                            'features': required_features
                        }
                        for feature in result['features']:
                            result[feature] = row_dict.get(feature, '')
                        results_data.append(result)
                    
                    total_transactions = len(df)
                    fraud_count = sum(predictions)
                    legitimate_count = total_transactions - fraud_count
                    
                    # Try to get total amount from various possible column names
                    amount_col = next((col for col in ['Amount', 'TransactionAmount'] if col in df.columns), None)
                    total_amount = df[amount_col].sum() if amount_col else 0
                    
                    fraud_percentage = (fraud_count / total_transactions * 100) if total_transactions else 0
                    legitimate_percentage = (legitimate_count / total_transactions * 100) if total_transactions else 0
                    
                    page = request.args.get('page', 1, type=int)
                    per_page = 10
                    total_pages = (total_transactions + per_page - 1) // per_page
                    start_idx = (page - 1) * per_page
                    end_idx = start_idx + per_page
                    
                    print(f"Rendering results: {total_transactions} transactions, {fraud_count} fraud, {legitimate_count} legitimate")
                    
                    return render_template('display.html',
                                        data=results_data[start_idx:end_idx],
                                        total_transactions=total_transactions,
                                        fraud_count=fraud_count,
                                        legitimate_count=legitimate_count,
                                        fraud_percentage=round(fraud_percentage, 1),
                                        legitimate_percentage=round(legitimate_percentage, 1),
                                        total_amount="{:,.2f}".format(total_amount),
                                        current_page=page,
                                        total_pages=total_pages)
                
                except Exception as e:
                    flash(f"Error in fraud detection: {str(e)}")
                    print(f"Error in fraud detection: {str(e)}")
                    return redirect(url_for('index'))
                    
            except Exception as e:
                flash(f"Error reading CSV file: {str(e)}")
                print(f"Error reading CSV: {str(e)}")
                return redirect(url_for('index'))
                
        except Exception as e:
            flash(f"Error saving file: {str(e)}")
            print(f"Error saving file: {str(e)}")
            return redirect(url_for('index'))
    
    flash('Please upload a valid CSV file')
    return redirect(url_for('index'))

@app.errorhandler(413)
def request_entity_too_large(error):
    flash('File too large. Maximum size is 16MB.')
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(error):
    flash('An internal error occurred. Please try again.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    try:
        print("Starting Flask application...")
        print(f"Debug mode: {'on' if app.debug else 'off'}")
        print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
        print(f"Templates folder: {app.template_folder}")
        port = int(os.environ.get('PORT', 5000))
        app.run(debug=True, host='0.0.0.0', port=port)
    except Exception as e:
        print(f"Error starting Flask application: {str(e)}")
        sys.exit(1)