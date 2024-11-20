from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a strong, unique key

# Paths to the files
SETTINGS_FILE = 'form_settings.json'
DATA_FILE = 'form_data.json'


# Function to retrieve form settings
def get_form_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as file:
            return json.load(file)
    # Default settings if the file doesn't exist
    return {
        "header": "Event Registration Form",
        "name_label": "Name",
        "email_label": "Email",
        "phone_label": "Phone No",
        "id_label": "ID",
        "extra_fields": []
    }


# Function to save form settings
def save_form_settings(settings):
    with open(SETTINGS_FILE, 'w') as file:
        json.dump(settings, file, indent=4)


# Function to retrieve form data
def get_form_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    return []


# Function to save form data
def save_form_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)


@app.route('/')
def form():
    form_settings = get_form_settings()
    return render_template('form.html', form_settings=form_settings)


@app.route('/admin/', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Hardcoded admin credentials (replace with secure storage in production)
        admin_email = "admin@example.com"
        admin_password = "password123"

        if email == admin_email and password == admin_password:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_panel'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
            return redirect(url_for('admin_login'))

    response = make_response(render_template('admin_login.html'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/admin_panel')
def admin_panel():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    form_data = get_form_data()  # Load data from the file

    # Load form settings from form_settings.json
    form_settings = get_form_settings()

    return render_template('admin_panel.html', form_data=form_data, form_settings=form_settings)


@app.route('/submit_form', methods=['POST'])
def submit_form():
    form_data = request.form.to_dict()
    form_data = {k: v.strip() for k, v in form_data.items() if v.strip()}  # Clean empty fields

    stored_data = get_form_data()  # Load existing data from the file
    for data in stored_data:
        if data.get('name') == form_data.get('name') or data.get('email') == form_data.get('email'):
            flash('Name or email already submitted!', 'error')
            return redirect(url_for('form'))

    stored_data.append(form_data)
    save_form_data(stored_data)  # Save updated data to the file

    flash('Form submitted successfully!', 'success')
    return redirect(url_for('form'))


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    form_settings = get_form_settings()

    if request.method == 'POST':
        form_settings['header'] = request.form.get('form_header')
        form_settings['name_label'] = request.form.get('name_label')
        form_settings['email_label'] = request.form.get('email_label')
        form_settings['phone_label'] = request.form.get('phone_label')
        form_settings['id_label'] = request.form.get('id_label')

        updated_extra_fields = []
        for key, value in request.form.items():
            if key.startswith("extra_fields"):
                try:
                    index = int(key.split('[')[1].split(']')[0])
                except ValueError:
                    continue
                while len(updated_extra_fields) <= index:
                    updated_extra_fields.append({})
                if 'label' in key:
                    updated_extra_fields[index]['label'] = value
                elif 'type' in key:
                    updated_extra_fields[index]['type'] = value

        form_settings['extra_fields'] = updated_extra_fields

        save_form_settings(form_settings)

        # Clear form data upon settings update
        save_form_data([])  # Save an empty list to the file
        flash("Form settings updated successfully. All form data has been cleared.", "success")
        return redirect(url_for('settings'))

    return render_template('settings.html', form_settings=form_settings)


if __name__ == '__main__':
    app.run(debug=True)
