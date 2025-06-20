from datetime import timedelta
from flask import Flask, render_template, request, flash, redirect, url_for, session
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.permanent_session_lifetime = timedelta(minutes=10)  # Updated auto logout time

# Load the Excel file
try:
    data = pd.read_excel('data.xlsx')
    #data = pd.read_excel('data_without_closed.xlsx')
except Exception as e:
    data = pd.DataFrame()
    print(f"Error loading Excel file: {e}")

# Define the required columns
required_columns = ['Ref Number', 'Company Name', 'Status', 'Sub Status', 'Complaint Received Date', 'Target Date','AM / Complained By', 'Customer Name', 'Area', 'Special Remarks']

USERNAME = "admin"
PASSWORD = "admin"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == USERNAME and password == PASSWORD:
            session.permanent = True
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error-message')
    
    return render_template('login.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    filtered_data = None
    if 'search_history' not in session:
        session['search_history'] = []

    if request.method == 'POST':
        am_complained_by = request.form.get('am_complained_by', '').strip()
        company_name = request.form.get('company_name', '').strip()
        ref_number = request.form.get('ref_number', '').strip()

        conditions = []

        if am_complained_by:
            conditions.append(data['AM / Complained By'].str.contains(am_complained_by, case=False, na=False))
        if company_name:
            conditions.append(data['Company Name'].str.contains(company_name, case=False, na=False))
        if ref_number:
            conditions.append(data['Ref Number'].astype(str).str.lower() == ref_number.lower())

        if conditions:
            filtered_data = data[pd.concat(conditions, axis=1).all(axis=1)][required_columns]
            
        if filtered_data is not None and not filtered_data.empty:
            filtered_data['Complaint Received Date'] = pd.to_datetime(filtered_data['Complaint Received Date'], errors='coerce')
            filtered_data = filtered_data.sort_values(by='Complaint Received Date', ascending=False)
            filtered_data['Complaint Received Date'] = filtered_data['Complaint Received Date'].dt.strftime('%Y-%m-%d')

            # Convert Target Date to datetime and format (but no sorting by it)
            filtered_data['Target Date'] = pd.to_datetime(filtered_data['Target Date'], errors='coerce')
            filtered_data['Target Date'] = filtered_data['Target Date'].dt.strftime('%Y-%m-%d')
            # Replace NaN values with 'N/A' (for all columns)
            filtered_data = filtered_data.fillna('N/A')

            search_key = f"{am_complained_by} | {company_name} | {ref_number}".strip(' |')
            if search_key not in session['search_history']:
                session['search_history'].append(search_key)
            if len(session['search_history']) > 10:
                session['search_history'] = session['search_history'][-10:]
        else:
            flash("No results found for the given search criteria.", 'error-message')

    return render_template('index.html', data=filtered_data, columns=required_columns, search_history=session['search_history'])

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('search_history', None)
    return redirect(url_for('login'))
    
if __name__ == '__main__':
    app.run(debug=True) 
    

# http://172.22.126.46:8080/
# python app.py
# cloudflared tunnel --url http://localhost:5000
