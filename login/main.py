from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import hashlib

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'Baohung0303'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Bungmobanhbao0303'
app.config['MYSQL_DB'] = 'login'

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
        cursor.execute('SELECT * FROM accounts WHERE username = %s ', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Get the stored hashed password from the account data
            stored_password = account['password']
            # Compare the hashed password input by the user with the stored hashed password
            if hashed_password == stored_password:
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                # Redirect to home page
                return redirect(url_for('home'))
            else:
                msg = 'Incorrect username/password!'
        else:
            msg = 'Invalid username or password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)


@app.route('/login/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))


# Get the maximum employee_id in the database
def get_max_employee_id(cursor):
    cursor.execute('SELECT MAX(employee_id) FROM accounts')
    result = cursor.fetchone()
    max_employee_id = result['MAX(employee_id)'] if result['MAX(employee_id)'] else 0
    return max_employee_id

@app.route('/login/register', methods=["GET", "POST"])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        # Hash password using SHA256
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        is_active = 1
        # Get the maximum employee_id in the database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        max_employee_id = get_max_employee_id(cursor)
        # Generate a new employee_id
        employee_id = max_employee_id + 1
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password:
            msg = 'Please fill out the form!'
        else:
            # Account doesn't exist and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES ( NULL, %s, %s, %s, %s)', (username, password, employee_id, is_active,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == "POST":
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

@app.route('/login/home')
def home():
    # Check if user is logged-in
    if 'loggedin' in session:
        # User is logged-in show them the home page
        return render_template('home.html', username=session['username'])
    # User is not logged-in redirect to login page
    return redirect(url_for('login'))

@app.route('/login/profile')
def profile():
    # Check if user is logged-in
    if 'loggedin' in session:
        # We need all the account info for the user, so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not logged-in redirect to login page
    return redirect(url_for('login'))

@app.route('/login/users')
def load_users():
    # Check if user is logged-in
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM employee')
        employee = cursor.fetchall()
        return render_template('user.html', employee=employee)
    return redirect(url_for('login'))

# Xử lý yêu cầu xoá user
@app.route('/delete_employee/<int:id>', methods=['DELETE'])
def delete_employee(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM employee WHERE id = %s", (id,))
    mysql.connection.commit()
    message = f"Employee with id {id} has been deleted."
    return jsonify({"message": message})

# Xử lý yêu cầu edit user
@app.route('/edit_employee/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    # Lấy thông tin của employee từ MySQL
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM employee WHERE id = %s", [id])
    employee = cursor.fetchone()
    cursor.close()
    if request.method == 'POST':
        # Lấy thông tin employee từ form
        lastname = request.form['lastname']
        firstname = request.form['firstname']
        department = request.form['department']
        age = request.form['age']
        phone_no = request.form['phone_no']
        email = request.form['email']
        address = request.form['address']
        # Cập nhật thông tin của employee vào MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "UPDATE employee SET lastname=%s, firstname=%s, department=%s, age=%s, phone_no=%s, email=%s, address=%s WHERE id=%s",
            (lastname, firstname, department, age, phone_no, email, address, id))
        mysql.connection.commit()
        cursor.close()
        message = f"Employee information id {id} updated successfully"
        return jsonify({"message": message})
    return jsonify(employee)

# Xử lý yêu cầu add user
@app.route('/add_employee', methods=['POST'])
def add_employee():
    # Lấy thông tin của employee từ form
    lastname = request.form['lastname']
    firstname = request.form['firstname']
    department = request.form['department']
    age = request.form['age']
    phone_no = request.form['phone_no']
    email = request.form['email']
    address = request.form['address']
    # Thêm thông tin của employee vào MySQL
    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO employee (lastname, firstname, department, age, phone_no, email, address) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (lastname, firstname, department, age, phone_no, email, address))
    mysql.connection.commit()
    cursor.close()
    # Trả về thông báo và địa chỉ URL cho việc hiển thị danh sách nhân viên
    message = f"Employee {firstname} {lastname} added successfully"
    return jsonify({"message": message, "url": "/employee_list"})

if __name__ == "__main__":
    app.run(debug=True)