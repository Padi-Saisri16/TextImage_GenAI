from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pandas as pd
import numpy as np
import os
import uuid

app = Flask(__name__)
app.secret_key = 'consist_gen_secure_key'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Mock User Database
users = {"admin": "password123"}

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['user'] = username
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/generate_dataset', methods=['POST'])
def generate_dataset():
    records = 1000
    # Simulate CTS scores
    cts_scores = np.random.uniform(0.75, 0.99, records)
    
    # ICF Logic: A 'Retry' occurs if score < 0.85
    # We calculate the rate: (Number of scores below 0.85 / Total records) * 100
    retries = [1 if score < 0.85 else 0 for score in cts_scores]
    retry_rate = (sum(retries) / records) * 100

    data = {
        'timestamp': pd.date_range(start='2026-01-01', periods=records, freq='H'),
        'identity_consistency_score': cts_scores,
        'transition_latency_ms': np.random.normal(210, 30, records),
        'context_drift': np.random.uniform(0.01, 0.15, records),
        'icf_retry': retries # 1 for Fail/Retry, 0 for Pass
    }
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(UPLOAD_FOLDER, 'simulation_data.csv'), index=False)
    return jsonify({"status": "success", "retry_rate": f"{retry_rate:.1f}%"})

@app.route('/reports')
def reports():
    path = os.path.join(UPLOAD_FOLDER, 'simulation_data.csv')
    if not os.path.exists(path):
        return "Please run simulation on Dashboard first."
    
    df = pd.read_csv(path)
    # Parsing the "Huge Dataset" for accurate reporting
    chart_data = {
        "labels": df['timestamp'].tail(20).tolist(),
        "scores": df['identity_consistency_score'].tail(20).tolist(),
        "latency": df['transition_latency_ms'].tail(20).tolist(),
        "drift": df['context_drift'].tail(20).tolist(), # Measured by CX variance
        "avg_cts": round(df['identity_consistency_score'].mean(), 3)
    }
    return render_template('reports.html', data=chart_data)

if __name__ == '__main__':
    app.run(debug=True)