from flask import Flask, render_template, redirect, url_for, request, session, flash
import requests
import os
from dotenv import load_dotenv
import json
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

# Get environment variables
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
API_BASE_URL = os.getenv('API_BASE_URL', 'https://api.n2g-ynni.net')
ELECTRICITY_MAP_TOKEN = os.getenv('ELECTRICITY_MAP_TOKEN')
APP_ROOT = os.getenv('APPLICATION_ROOT', '/')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev_secret_key')  # Change this in production

# Session timeout (30 minutes)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Support for running behind a proxy in a subdirectory
app.config['APPLICATION_ROOT'] = '/'

@app.route('/')
def index():
    if 'access_token' not in session:
        return redirect(APP_ROOT + url_for('login', _external=False))
    return redirect(APP_ROOT + url_for('dashboard', _external=False))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Authenticate user
        token_data = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'grant_type': 'password',
            'username': username,
            'password': password
        }

        try:
            response = requests.post(f"{API_BASE_URL}/v2/token", data=token_data)
            response.raise_for_status()
            token_info = response.json()

            # Check if MFA is required
            if 'challenge_name' in token_info:
                # Handle MFA challenge (not implemented in this basic version)
                flash('MFA is required but not supported in this demo', 'error')
                return render_template('login.html', APP_ROOT=APP_ROOT)

            # Store token in session
            session['access_token'] = token_info.get('access_token')
            session['refresh_token'] = token_info.get('refresh_token')
            session['token_expires'] = datetime.now().timestamp() + token_info.get('expires_in', 3600)

            return redirect(APP_ROOT + url_for('dashboard', _external=False))

        except requests.exceptions.RequestException as e:
            error_message = "Authentication failed"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('error_description', error_message)
                except:
                    pass
            flash(error_message, 'error')

    return render_template('login.html', APP_ROOT=APP_ROOT)

@app.route('/dashboard')
def dashboard():
    if 'access_token' not in session:
        return redirect(APP_ROOT + url_for('login', _external=False))

    # Check if token is expired
    if datetime.now().timestamp() > session.get('token_expires', 0):
        # Try to refresh token
        if 'refresh_token' in session:
            try:
                refresh_data = {
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET,
                    'grant_type': 'refresh_token',
                    'refresh_token': session['refresh_token']
                }

                response = requests.post(f"{API_BASE_URL}/v2/token", data=refresh_data)
                response.raise_for_status()
                token_info = response.json()

                session['access_token'] = token_info.get('access_token')
                session['refresh_token'] = token_info.get('refresh_token')
                session['token_expires'] = datetime.now().timestamp() + token_info.get('expires_in', 3600)
            except:
                return redirect(APP_ROOT + url_for('login', _external=False))
        else:
            return redirect(APP_ROOT + url_for('login', _external=False))

    return render_template('dashboard.html', APP_ROOT=APP_ROOT)

@app.route('/api/power')
def get_power_data():
    if 'access_token' not in session:
        return json.dumps({'error': 'Not authenticated'}), 401

    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    try:
        # Get instantaneous power data
        response = requests.get(f"{API_BASE_URL}/v2/instantaneous", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error_message = "Failed to fetch power data"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                error_message = error_data.get('error_description', error_message)
            except:
                pass
        return json.dumps({'error': error_message}), 500

@app.route('/api/home-energy')
def get_home_energy_data():
    if 'access_token' not in session:
        return json.dumps({'error': 'Not authenticated'}), 401

    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    try:
        # Calculate today's date
        today = datetime.now().strftime('%Y-%m-%d')

        # Get electricity offtake data for today
        response = requests.get(
            f"{API_BASE_URL}/v2/energy-measurements/electricity-offtake/real-time/days/{today}/{today}", 
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error_message = "Failed to fetch home energy data"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                error_message = error_data.get('error_description', error_message)
            except:
                pass
        return json.dumps({'error': error_message}), 500

@app.route('/api/gas')
def get_gas_data():
    if 'access_token' not in session:
        return json.dumps({'error': 'Not authenticated'}), 401

    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    try:
        # Calculate today's date
        today = datetime.now().strftime('%Y-%m-%d')

        # Get gas data for today using the correct endpoint
        response = requests.get(
            f"{API_BASE_URL}/v2/energy-measurements/gas/real-time/days/{today}/{today}",
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error_message = "Failed to fetch gas data"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                error_message = error_data.get('error_description', error_message)
            except:
                pass
        return json.dumps({'error': error_message}), 500

@app.route('/api/electricity-map')
def get_electricity_map_data():
    try:
        # Get power breakdown data from Electricity Map API
        headers = {
            'auth-token': ELECTRICITY_MAP_TOKEN
        }
        response = requests.get(
            "https://api.electricitymap.org/v3/power-breakdown/latest",
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error_message = "Failed to fetch electricity map data"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                error_message = error_data.get('error', error_message)
            except:
                pass
        return json.dumps({'error': error_message}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(APP_ROOT + url_for('login', _external=False))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5002)), debug=True)
