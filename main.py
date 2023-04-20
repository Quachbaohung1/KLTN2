from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import hashlib
from datetime import datetime, timedelta

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'Baohung0303'

# Enter your database connection details below
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_PORT'] = 9090
app.config['MYSQL_USER'] = 'Hungqb'
app.config['MYSQL_PASSWORD'] = '123456'
app.config['MYSQL_DB'] = 'khoaluan'

# Intialize MySQL
mysql = MySQL(app)


@app.route('/login/', methods=["GET", "POST"])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Hash the password input by the user
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Auth_user WHERE username = %s ', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in our database
        if account:
            # Check if the account is locked
            if account['is_active'] == 0 and (datetime.now() - account['Last_login_time']) < timedelta(minutes=1):
                msg = 'Your account has been locked!'
            else:
                # Get the stored hashed password from the account data
                stored_password = account['Password_reset_token']
                # Get the failed login attempts count from the account data
                Failed_login_attempts = account['Failed_login_attemps']
                # Compare the hashed password input by the user with the stored hashed password
                if hashed_password == stored_password:
                    # Reset failed login attempts and update last login time
                    cursor.execute(
                        'UPDATE Auth_user SET Failed_login_attemps = 0, Last_login_time = %s, is_active = 1 WHERE id = %s',
                        (datetime.now(), account['id'],))
                    mysql.connection.commit()
                    # Create session data, we can access this data in other routes
                    session['loggedin'] = True
                    session['id'] = account['id']
                    session['username'] = account['username']
                    # Redirect to home page
                    return redirect(url_for('home'))
                else:
                    # Increment failed login attempts
                    Failed_login_attempts += 1
                    cursor.execute('UPDATE Auth_user SET Failed_login_attemps = Failed_login_attemps + 1 WHERE id = %s',
                                   (account['id'],))
                    mysql.connection.commit()
                    # Check if the account should be locked
                    if account['Failed_login_attemps'] >= 4:
                        # Lock the account
                        cursor.execute('UPDATE Auth_user SET is_active = 0 WHERE id = %s', (account['id'],))
                        mysql.connection.commit()
                        msg = 'Your account has been locked!'
                    else:
                        msg = f'Incorrect username/password! Failed login attempts: {Failed_login_attempts}'
        else:
            msg = 'Invalid username or password!'

    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)

@app.route('/login/home')
def home():
# Check if user is logged-in
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'select Employee.id as id, Employee.FirstName as firstname, Employee.LastName as lastname, info.jobname as job, info.departmentname as department, Employee.Age as age, Employee.Phone_no as phone_no, Employee.Email_Address as email, Employee.Address as address from Employee left join ( select Job.id as id, Job.Name as jobname, Department.Name as departmentname from Job left join Department on Job.department_id=Department.id ) as info on Employee.Job_ID=info.id')
        account = cursor.fetchone()
        return render_template('home.html', account=account)
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)