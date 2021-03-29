""" This is the app"""
from flask import Flask, session, request, render_template, url_for
from flaskext.mysql import MySQL
from werkzeug.utils import redirect
from datetime import datetime

from project import Project
from userFactory import UserFactory

mysql = MySQL()

# initializing a variable of Flask
app = Flask(__name__, template_folder="templates")

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'project_tracker'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


@app.route('/login', methods=['GET', "POST"]) #gets the login page
def login():
    if request.method == 'POST':
        try:
            con = mysql.connect()  # set up database connection
            cur = con.cursor()
            username = request.form['username']
            password = request.form['password']
        except:
            con.rollback()
        finally:
            cur.execute("SELECT role, userID FROM user WHERE username=%s AND password=%s", (username, password))
            rows = cur.fetchall()
            con.commit()
            con.close()
            if(len(rows)!=0):
                session['projects'] = []
                session['role'] = rows[0][0]
                session['userID'] = rows[0][1]
                return redirect(url_for('home'))  # route to home page
            else:
                error = "Invalid login details"
                return render_template('login.html', error=error)
    return render_template('login.html') #if get, return template

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('userID', None)
    session.pop('projects', None)
    session.pop('role', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', "POST"]) #gets the register page
def register():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            role = request.form['role']
            email = request.form['email']
            con = mysql.connect()  # set up database connection
            cur = con.cursor()
            cur.execute("SELECT * FROM user WHERE email=%s", email)
            rows = cur.fetchall()
            if (len(rows) != 0):
                return render_template("login.html", error="email already in use")
            cur.execute("SELECT * FROM user WHERE username=%s", username)
            rows = cur.fetchall()
            if (len(rows) != 0):
                return render_template("login.html", error="username already in use")
            con.commit()

            # create user object here



            factory = UserFactory()

            newUser = factory.get_user(role) # create the new user object here

            newUser.set_username(username)
            newUser.set_password(password)
            newUser.set_email(email)
            newUser.set_role(role)

            #if a worker:
            #   add more stuff (null manager stuffs in dB)
            #if a manager:
            #   add more stuff (null worker stuff in dB)





            cur.execute('INSERT INTO user (username, password, email, role)'
                        'VALUES( %s, %s, %s, %s)',
                        (newUser.get_username(), newUser.get_password(), newUser.get_email(), newUser.get_role()))
            con.commit()
        except:
            con.rollback()
        finally:
            print("All good")
        return render_template("login.html")
    return render_template('register.html')

@app.route('/createProject', methods=['GET', "POST"]) #gets the create project page / creates a new project
def createProject():
    if 'userID' not in session: #if not logged in
        return render_template('login.html')
    if ("worker"):
        home()
    if request.method == 'POST':
        try:
            con = mysql.connect()  # set up database connection
            cur = con.cursor()
            name = request.form['name']
            deadline = request.form['deadline']
            description = request.form['description']
            projectLeader = session['userID']


            if(name=="" or deadline==""):
                print("here")
                date = datetime.date(datetime.today())
                return render_template('create_project.html', date=date, error="Please give a name and a deadline")


            newProject = Project()
            newProject.set_project_leader(projectLeader)
            newProject.set_name(name)
            newProject.set_deadline(deadline)
            newProject.set_description(description)
            session['projects'].append(newProject)  # add to the project list



            cur.execute('INSERT INTO project (name, deadline, description, projectLeader)'
                        'VALUES( %s, %s, %s, %s)',
                        (name, deadline, description, projectLeader))
            con.commit()
        except:
            con.rollback()
        finally:

            con.close()
        return redirect(url_for('home'))

    date = datetime.date(datetime.today())
    return render_template('create_project.html', date=date)

@app.route('/createTask', methods=['GET', "POST"])  #gets the create task page / creates a new task
def createTask():
    if 'userID' not in session: #if not logged in
        return render_template('login.html')
    if request.method == 'POST':
        return
    return render_template('create_task.html')

@app.route("/task", methods=['GET']) #gets a tasks details page
def taskDetails():
    if 'userID' not in session: #if not logged in
        return render_template('login.html')
    return render_template("manager_home.html", rows="rows")

@app.route("/project", methods=['GET'])  #gets a projects details page
def projectDetails():
    if 'userID' not in session: #if not logged in
        return render_template('login.html')
    return render_template("manager_home.html", rows="rows")


@app.route("/", methods=['GET']) #gets the home page
def home():
    if 'userID' not in session: #if not logged in
        return render_template('login.html')
    if session['role'] == "worker":
        return render_template('worker_home.html')
    if session['role'] == "manager":
        return render_template('manager_home.html')
    return





@app.route('/assign_user', methods=['POST'])
def assign_user(): #post request for managers to assign users to a project
    if("worker"):
        home()
    return

@app.route('/remove_user', methods=['DELETE'])
def remove_user(): #DELETE request for managers to remove users from a project
    if("worker"):
        home()
    return

@app.route('/delete_task', methods=['DELETE'])
def delete_task(): #DELETE request for managers to remove a task from a project
    if("worker"):
        home()
    return

@app.route('/delete_project', methods=['DELETE'])
def delete_project(): #DELETE request for managers to remove a task from a project
    if("worker"):
        home()
    return

@app.route('/update_task', methods=['PATCH'])
def update_task(): #patch request for users to update the status of a task
    return

@app.route('/update_effort', methods=['PATCH'])
def update_effort(): #patch request for managers to update the relative effort of a task
    if ("worker"):
        home()
    return

# @app.route('/register_advisor', methods=['POST', 'GET'])
# def register_advisor():
#     if request.method == 'POST':
#         con = mysql.connect()  # set up database connection
#         cur = con.cursor()
#         rows = []
#         try:
#             print("--------------------------Demo Start----------------------------------------")
#             username = request.form['username']  # retrieve form data
#             email = request.form['email']
#             start_year = request.form['start_year']
#             remote = request.form['remote']
#             profile_type = request.form['profile']
#             project = request.form['project']
#             contract_pay = float(request.form.get("pay"))  # get the default value
#
#             print("to register an advisor")
#             staff = Advisor()
#             staff.set_user_name(username)
#             staff.set_email(email)
#             staff.set_start_year(start_year)
#             role = "advisor"
#             staff.set_role(role)
#             staff.set_remote(remote)
#
#             if profile_type.lower() == "video":
#                 staff.set_profile(profile_type)
#                 video = Video()
#                 video.set_username(username)
#                 video.set_type(profile_type)
#             elif profile_type.lower() == "text":
#                 staff.set_profile(profile_type)
#                 text = Text()
#                 text.set_username(username)
#                 text.set_type(profile_type)
#
#             staff.set_contract(contract_pay)  # composition
#             contract = Contract()
#             contract.set_username(username)
#             contract.set_pay(contract_pay)
#
#             the_project = Project()  # set the Project
#             the_project.set_name(project)
#
#             staff_project = StaffProject()  # set the StaffProject
#             staff_project.set_project(the_project)  # aggregation
#             staff_project.set_staff(staff)  # aggregation
#             the_list.append(staff_project)  # add to the list of StaffProject objects
#
#             # insert data to the database
#             cur.execute('INSERT INTO staff (username, email, start_date, role, remote)'
#                         'VALUES( %s, %s, %s, %s, %s)',
#                         (username, email, start_year, role, remote))
#             con.commit()
#             print("write to the staff table")
#
#             cur.execute('INSERT INTO project (name)VALUES( %s)', project)  # note: name is primary key
#             con.commit()
#             print("write to the project table")
#
#             cur.execute('INSERT INTO staff_project (username, project)VALUES( %s, %s)', (username, project))
#             con.commit()
#             print("write to the staff_project table")
#
#             cur.execute('INSERT INTO contract (username, pay)VALUES( %s, %s)', (username, contract_pay))
#             con.commit()
#             print("write to the contract table")
#
#             if profile_type.lower() == "video":
#                 time_limit = video.get_time_limit()
#                 cur.execute('INSERT INTO profile (username, type, time_limit)VALUES( %s, %s, %s)',
#                             (username, profile_type, time_limit))
#             elif profile_type.lower() == "text":
#                 word_limit = text.get_word_limit()
#                 cur.execute('INSERT INTO profile (username, type, word_limit)VALUES( %s, %s, %s)',
#                             (username, profile_type, word_limit))
#             con.commit()
#             print("write to the profile table")
#
#             # testing - retrieve data from the database
#             cur.execute('SELECT staff.username, staff.email, staff.start_date, staff.role, '
#                         'profile.type, staff_project.project, contract.pay '
#                         'FROM staff, profile, staff_project, contract '
#                         'WHERE staff.username = profile.username AND '
#                         'staff.username = staff_project.username AND '
#                         'staff.username = contract.username')
#             rows = cur.fetchall()
#             row_num = len(rows)
#             print("staff:  ", row_num)
#             for row in rows:
#                 print("username: ", row[0])
#                 print("email: ", row[1])
#
#             con.commit()
#             rows = rows
#             return render_template("manager_home.html", rows=rows)
#         except:
#             con.rollback()
#         finally:
#             rows = rows
#             return render_template("manager_home.html", rows=rows)
#             con.close()



if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.run()
