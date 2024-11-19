from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a strong, unique key

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/admin/', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        # Retrieve email and password from the login form
        email = request.form.get('email')
        password = request.form.get('password')

        # Hardcoded admin credentials (replace with secure storage in production)
        admin_email = "admin@example.com"
        admin_password = "password123"

        # Validate credentials
        if email == admin_email and password == admin_password:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_panel'))  # Redirect to the admin panel
        else:
            flash('Invalid credentials. Please try again.', 'error')
            return redirect(url_for('admin_login'))  # Redirect back to login form

    # For GET requests, render the login form with no-cache headers
    response = make_response(render_template('admin_login.html'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/admin_panel')
def admin_panel():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    form_data = session.get('form_data', [])
    return render_template('admin_panel.html', form_data=form_data)

@app.route('/submit_form', methods=['POST'])
def submit_form():
    form_data = request.form.to_dict()
    submitted_name = form_data.get('name')
    submitted_email = form_data.get('email')

    stored_data = session.get('form_data', [])

    for data in stored_data:
        if data.get('name') == submitted_name or data.get('email') == submitted_email:
            flash('Name or email already submitted!', 'error')
            return redirect(url_for('index'))

    stored_data.append(form_data)
    session['form_data'] = stored_data

    flash('Form submitted successfully!', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
