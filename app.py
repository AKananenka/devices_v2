from flask import Flask, render_template, flash, request, redirect, url_for, session, logging, session
from data import Devices
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'test007'
app.config['MYSQL_DB'] = 'devices'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MySQL
mysql = MySQL(app)

Devices = Devices()

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unathorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/devices')
@is_logged_in
def devices():
    # Create cursor
    cur = mysql.connection.cursor()

    # Execute query
    result = cur.execute("SELECT id, model, hostname, ip_address, user, added_date FROM nw_devices")

    nw_devices = cur.fetchall()

    if result > 0:
        return render_template('devices.html', nw_devices = nw_devices)
    else:
        msg = 'No devices added yet'
        return render_template('devices.html', msg = msg)
    cur.close()

@app.route('/device/<string:id>/')
@is_logged_in
def device(id):
    return render_template('device.html', id=id)

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Password do not match')
    ])
    confirm = PasswordField('Confirm Password')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO users (name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get From Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create Cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            data = cur.fetchone()
            password = data['password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Wrong password'
                return render_template('login.html', error=error)
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)
    
    return render_template('login.html')

@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')

# Devices Form Class
class DeviceForm(Form):
    model = StringField('Model', [validators.Length(min=1, max=50)])
    hostname = StringField('Hostname', [validators.Length(min=1, max=50)])
    ip_address = StringField('IP Address', [validators.Length(min=8, max=25)])
    user = StringField('User', [validators.Length(min=4, max=25)])
    passw = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Password do not match')
    ])
    confirm = PasswordField('Confirm Password')

# Add Device
@app.route('/add_device', methods=['GET', 'POST'])
@is_logged_in
def add_device():
    form = DeviceForm(request.form)
    if request.method == 'POST' and form.validate():
        model = form.model.data
        hostname = form.hostname.data
        ip_address = form.ip_address.data
        user = form.user.data
        passw = sha256_crypt.encrypt(str(form.passw.data))

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO nw_devices (model, hostname, ip_address, user, password) VALUES(%s, %s, %s, %s, %s)", (model, hostname, ip_address, user, passw))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Device successfuly added', 'success')

        return redirect(url_for('add_device'))
    return render_template('add_device.html', form=form)

class DeviceEditForm(Form):
    model = StringField('Model', [validators.Length(min=1, max=50)])
    hostname = StringField('Hostname', [validators.Length(min=1, max=50)])
    ip_address = StringField('IP Address', [validators.Length(min=8, max=25)])
    user = StringField('User', [validators.Length(min=4, max=25)])

@app.route('/edit_device/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_device(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get device
    result = cur.execute("SELECT * FROM nw_devices WHERE id=%s", [id])

    device = cur.fetchone()
    
    # Get form
    form = DeviceEditForm(request.form)

    # Populate device form fields
    form.model.data = device['model']
    form.hostname.data = device['hostname']
    form.ip_address.data = device['ip_address']
    form.user.data = device['user']

    if request.method == 'POST' and form.validate():
        model = request.form['model']   
        hostname = request.form['hostname']
        ip_address = request.form['ip_address']
        user = request.form['user']

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("UPDATE nw_devices SET model=%s, hostname=%s, ip_address=%s, user=%s WHERE id=%s", (model, hostname, ip_address, user, id))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Device successfuly edited', 'success')

        return redirect(url_for('devices'))
    return render_template('edit_device.html', form=form)

@app.route('/delete_device/<string:id>', methods=['POST'])
@is_logged_in
def delete_device(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Execute query
    cur.execute("DELETE from nw_devices where id = %s", [id])

    # Commit to DB
    mysql.connection.commit()

    flash('Device successfuly deleted', 'success')
    return redirect(url_for('devices'))

if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)
