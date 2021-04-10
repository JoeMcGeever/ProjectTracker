""" This is the app"""
from flask import Flask, session, request, render_template, url_for
from flaskext.mysql import MySQL
from werkzeug.utils import redirect
from datetime import datetime

from assignedState import AssignedState
from completedState import CompletedState
from newState import NewState
from reviewingState import ReviewingState
from task import Task
from userFactory import UserFactory
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

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
            cur.execute("SELECT role, userID FROM user WHERE username=%s AND password=%s", (username, password))
            rows = cur.fetchall()
            if (len(rows) != 0):
                session['role'] = rows[0][0]
                session['userID'] = rows[0][1]
                return redirect(url_for('home'))  # route to home page
            else:
                error = "Invalid login details"
                return render_template('login.html', error=error)
        except:
            con.rollback()
        finally:
            con.commit()
            con.close()


    return render_template('login.html') #if get, return template

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('userID', None)
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


            factory = UserFactory()

            newUser = factory.get_user(role) # create the new user object here

            newUser.set_username(username)
            newUser.set_password(password)
            newUser.set_email(email)
            newUser.set_role(role)

            cur.execute('INSERT INTO user (username, password, email, role)'
                        'VALUES( %s, %s, %s, %s)',
                        (newUser.get_username(), newUser.get_password(), newUser.get_email(), newUser.get_role()))
            con.commit()
        except:
            con.rollback()
        finally:
            con.close()
        return render_template("login.html")
    return render_template('register.html')

@app.route('/createProject', methods=['GET', "POST"]) #gets the create project page / creates a new project
def createProject():
    if 'userID' not in session: #if not logged in
        return render_template('login.html')
    if ("worker"=="ke"):
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


            cur.execute('INSERT INTO project (name, deadline, description, projectLeader)'
                        'VALUES( %s, %s, %s, %s)',
                        (name, deadline, description, projectLeader))

            con.commit()
        except:
            cur.execute('SELECT * FROM user')
            print(cur.fetchall())
            cur.execute('INSERT INTO project (name, deadline, description, projectLeader)'
                        'VALUES( %s, %s, %s, %s)',
                        (name, deadline, description, projectLeader))
            con.rollback()
        finally:

            con.close()
        return redirect(url_for('home'))

    date = datetime.date(datetime.today())
    return render_template('create_project.html', date=date)

@app.route('/createTask', methods=['GET', "POST"])  #gets the create task page / creates a new task
def createTask():
    projectID = request.args.get('id', None)
    if 'userID' not in session: #if not logged in, or no parent projectID is given
        print("NO USERID")
        return render_template('login.html')
    if request.method=="GET" and projectID is None: #if the projectID is not specified in the url for GET request
        print("No projectID")
        return redirect(url_for('home'))
    elif request.method == "POST":
        projectID = request.form['projectID'] #otherwise, the projectID is send in the request form
    #get the project details
    try:
        con = mysql.connect()  # set up database connection
        cur = con.cursor()
        cur.execute("SELECT * FROM project WHERE projectID=%s", (projectID))
        data = cur.fetchone()
    except:
        con.rollback()
    finally:
        con.commit()
        con.close()

    date = datetime.date(datetime.today()) #the current date (for deadline picker)
    projectDeadline = data[2] #the deadline of the project (for deadline picker)


    if request.method == 'POST':
        name = request.form['name']
        deadline = request.form['deadline']
        description = request.form['description']
        if name == "" or deadline == "":
            return render_template('create_task.html', date=date, deadline=projectDeadline, projectID=projectID, error="Please enter a name and a deadline for the task")
        try:
            con = mysql.connect()  # set up database connection
            cur = con.cursor()
            cur.execute('INSERT INTO task (name, deadline, description, projectID)'
                        'VALUES( %s, %s, %s, %s)',
                        (name, deadline, description, projectID))
            con.commit()
        except:
            con.rollback()
            return redirect(url_for('project', id=projectID, error="Error creating task"))
        finally:
            con.close()
        return redirect(url_for('project', id = projectID))
    return render_template('create_task.html', date=date, deadline=projectDeadline, projectID=projectID)

@app.route('/createSubTask', methods=['GET', "POST"])  #gets the create task page / creates a new task
def createSubTask():
    projectID = request.args.get('id', None)
    parentTaskID = request.args.get('parentTaskID', None)
    if 'userID' not in session:  # if not logged in, or no parent projectID is given
        print("NO USERID")
        return render_template('login.html')
    if request.method == "GET" and (projectID is None or parentTaskID is None):  # if the projectID is not specified in the url for GET request
        print("No projectID / parentTaskID")

        return redirect(url_for('home'))
    elif request.method == "POST":
        projectID = request.form['projectID']  # otherwise, the projectID is send in the request form
        parentTaskID = request.form['parentTaskID']
    # get the project details
    try:
        con = mysql.connect()  # set up database connection
        cur = con.cursor()
        cur.execute("SELECT * FROM project WHERE projectID=%s", (projectID))
        data = cur.fetchone()
    except:
        con.rollback()
    finally:
        con.commit()
        con.close()

    date = datetime.date(datetime.today())  # the current date (for deadline picker)
    projectDeadline = data[2]  # the deadline of the project (for deadline picker)

    if request.method == 'POST':
        name = request.form['name']
        deadline = request.form['deadline']
        description = request.form['description']
        if name == "" or deadline == "":
            return render_template('create_task.html', date=date, deadline=projectDeadline, projectID=projectID,
                                   error="Please enter a name and a deadline for the task")
        try:
            con = mysql.connect()  # set up database connection
            cur = con.cursor()
            cur.execute('INSERT INTO task (name, deadline, description, projectID, parentTask)'
                        'VALUES( %s, %s, %s, %s, %s)',
                        (name, deadline, description, projectID, parentTaskID))
            idOfTaskCreated = cur.lastrowid  # get the id of the last created object in cur
            cur.execute('INSERT INTO children_tasks (parentTaskID, taskID)'
                        'VALUES( %s, %s)',
                        (parentTaskID, idOfTaskCreated))
            con.commit()
        except:
            con.rollback()
            return redirect(url_for('project', id=projectID, error="Error creating task"))
        finally:
            con.close()
        return redirect(url_for('project', id=projectID))
    return render_template('create_sub_task.html', date=date, deadline=projectDeadline, projectID=projectID,
                           parentTaskID=parentTaskID)


@app.route("/taskDetails", methods=['GET']) #gets a tasks details page
def taskDetails():
    taskID = request.args.get('taskID', None)
    projectID = request.args.get('projectID', None)
    error = request.args.get('error', None)
    if 'userID' not in session: #if not logged in
        return render_template('login.html')
    if taskID is None or projectID is None:
        return home()

    role = session['role']
    try:
        con = mysql.connect()  # set up database connection
        cur = con.cursor()
        cur.execute("SELECT * FROM task WHERE taskID=%s", taskID) # get the task
        taskSQL = cur.fetchone()
        cur.execute("SELECT * FROM task WHERE parentTask=%s", taskID) # get its children
        childrenSQL = cur.fetchall()
    except:
        con.rollback()
    finally:
        con.commit()
        con.close()

    task = Task() # create task object
    task.set_taskID(taskSQL[0])
    task.set_name(taskSQL[1])
    task.set_effort(taskSQL[2])
    task.set_status(taskSQL[3])
    task.set_deadline(taskSQL[4])
    task.set_description(taskSQL[5])
    task.set_assigned_user(taskSQL[8])
    for child in childrenSQL: # append its child objects after creating them also
        childTask = Task()
        childTask.set_taskID(child[0])
        childTask.set_name(child[1])
        childTask.set_effort(child[2])
        childTask.set_status(child[3])
        childTask.set_deadline(child[4])
        childTask.set_description(child[5])
        childTask.set_assigned_user(child[8])
        task.add_child_task(childTask) # add the child task to the task object

    return render_template("task.html", task=task, projectID=projectID, role=role, error=error, userID=session['userID'])

@app.route("/project", methods=['GET'])  #gets a projects details page
def project():
    projectID = request.args.get('id', None)
    if 'userID' not in session: #if not logged in
        return render_template('login.html')
    if projectID is None:
        print("No projectID")
        return redirect(url_for('home'))
        # get the project details
    try:
        con = mysql.connect()  # set up database connection
        cur = con.cursor()
        cur.execute("SELECT * FROM task WHERE projectID=%s AND parentTask is NULL ORDER BY deadline", projectID)
        data = cur.fetchall() #gets all the parent tasks in the task hierarchy
        print(data)
    except:
        con.rollback()
    finally:
        con.commit()
        con.close()

    role = session['role']
    projectTasks = sortTasks(data) # sorts the data into the relevant, class hierarchy

    #projectTasks no contains a list of each core task

    return render_template("project.html", project=projectTasks, projectID=projectID, role=role)

def sortTasks(data): #data parameter - the sql returned from collecting all of the parent tasks for the projects.
    project = []#list of tasks
    for task in data:
        taskInstance = Task() # create the task instance
        taskInstance.set_taskID(task[0])
        taskInstance.set_name(task[1])
        taskInstance.set_effort(task[2])
        taskInstance.set_status(task[3])
        taskInstance.set_deadline(task[4])
        taskInstance.set_description(task[5])
        taskInstance.set_assigned_user(task[8])
        for childToAdd in getChildren(taskInstance.get_taskID()):
            taskInstance.add_child_task(childToAdd) # composite pattern
        # call the recursive function to populate the task hierarchy
        project.append(taskInstance)
    return project # sorts the data into the

def getChildren(id): # returns a task from its id
    theTasks=[]
    try:
        con = mysql.connect()  # set up database connection
        cur = con.cursor()
        cur.execute(("SELECT * FROM task WHERE taskID IN"
                     " (SELECT taskID FROM children_tasks WHERE parentTaskID=%s)"),id)
        data = cur.fetchall()
    except:
        con.rollback()
    finally:
        con.commit()
        con.close()
    for task in data:
        taskInstance = Task()  # create the task instance
        taskInstance.set_taskID(task[0])
        taskInstance.set_name(task[1])
        taskInstance.set_effort(task[2])
        taskInstance.set_deadline(task[3])
        taskInstance.set_description(task[4])
        taskInstance.set_assigned_user(task[8])
        taskInstance.add_child_task(getChildren(taskInstance.get_taskID()))
        theTasks.append(taskInstance)
        # call the recursive function to populate the task hierarchy
    return theTasks # return the task to be appended in the hierarchy

@app.route("/", methods=['GET']) #gets the home page
def home():
    if 'userID' not in session: #if not logged in
        return render_template('login.html')

    rows=[]

    if session['role'] == "worker":
        try:
            con = mysql.connect()  # set up database connection
            cur = con.cursor()
            userID = session['userID']
            cur.execute("SELECT * FROM project WHERE projectID IN (SELECT projectID FROM task WHERE assignedUserID=%s)", userID)
            rows = cur.fetchall()
            print(rows)
        except:
            con.rollback()
        finally:

            con.commit()
            con.close()
        return render_template('worker_home.html', data=rows)


    if session['role'] == "manager":
        try:
            con = mysql.connect()  # set up database connection
            cur = con.cursor()
            userID = session['userID']
            print(userID)
            cur.execute("SELECT * FROM project WHERE projectLeader=%s ORDER BY project.deadline", (userID))
            rows = cur.fetchall()
            print(rows)
        except:
            con.rollback()
        finally:

            con.commit()
            con.close()

        return render_template('manager_home.html', data=rows)
    return render_template('login.html')


@app.route('/assignUser', methods=['POST'])
def assignUser(): #post request for managers to assign users to a project
    if 'userID' not in session:  # if not logged in
        return render_template('login.html')
    if session['role'] == "worker":
        return render_template('worker_home.html')

    projectID = request.form['projectID']
    taskID = request.form['taskID']
    userID = request.form['userID']
    try:
        con = mysql.connect()  # set up database connection
        cur = con.cursor()
        cur.execute("UPDATE task SET assignedUserID=%s WHERE taskID=%s", (userID, taskID))
        cur.execute("UPDATE task SET status='assigned' WHERE taskID=%s", taskID)
        sendEmail(userID, "A new task has been assigned to you, please log in to see the information.", "A new task has been assigned to you")
    except:
        print("Error in assigning a user")
        return redirect(url_for('taskDetails', projectID=projectID, taskID=taskID, error="No user with id: " + str(userID)))
        con.rollback()

    finally:
        con.commit()
        con.close()
    return redirect(url_for('taskDetails', projectID=projectID, taskID=taskID ))  # route to task details page


@app.route('/removeUser', methods=['POST','PATCH'])
def removeUser(): #PATCH request for managers to remove users from a project
    if session['role'] == "worker":
        return render_template('worker_home.html')

    projectID = request.form['projectID']
    taskID = request.form['taskID']
    try:
        con = mysql.connect()  # set up database connection
        cur = con.cursor()
        cur.execute("SELECT assignedUserID, name FROM task WHERE taskID=%s", taskID)
        result = cur.fetchone()
        userID = result[0]
        taskName = result[1]
        cur.execute("UPDATE task SET assignedUserID=NULL, status='new' WHERE taskID=%s", taskID)
        sendEmail(userID, "You have been un-assigned to the task: " + taskName, taskName)
    except:
        print("Error in removing user")
        return redirect(url_for('taskDetails', projectID=projectID, taskID=taskID))
        con.rollback()

    finally:
        con.commit()
        con.close()
    return redirect(url_for('taskDetails', projectID=projectID, taskID=taskID ))  # route to task details page


@app.route('/deleteTask', methods=['POST','DELETE'])
def deleteTask(): #DELETE request for managers to remove a task from a project
    projectID = request.form['projectID']
    taskID = request.form['taskID']
    if 'userID' not in session:  # if not logged in
        return render_template('login.html')
    if session['role'] == "worker":
        return render_template('worker_home.html')

    try:
        con = mysql.connect()  # set up database connection
        cur = con.cursor()
        cur.execute('DELETE FROM children_tasks WHERE parentTaskID=%s OR taskID=%s', (taskID, taskID))
        cur.execute('DELETE FROM task WHERE taskID=%s', taskID)
    except:
        con.rollback()

    finally:
        con.commit()
        con.close()


    return redirect(url_for('project', id=projectID ))  # route to project page

@app.route('/deleteProject', methods=['POST','DELETE'])
def deleteProject(): #DELETE request for managers to remove a task from a project
    projectID = request.form['projectID']
    if 'userID' not in session:  # if not logged in
        return render_template('login.html')
    if session['role'] == "worker":
        return render_template('worker_home.html')
    try:
        con = mysql.connect()  # set up database connection
        cur = con.cursor()
        cur.execute(
            "DELETE children_tasks, task FROM task INNER JOIN children_tasks ON task.projectID = children_tasks.projectID WHERE task.projectID=%s",
            projectID)
        cur.execute("DELETE FROM project WHERE projectID=%s", projectID)
    except:
        con.rollback()

    finally:
        con.commit()
        con.close()

    return redirect(url_for('home'))  # route to task details page

@app.route('/updateStatus', methods=['POST', 'PATCH'])
def updateStatus(): #patch request for users to update the status of a task
    status = request.form['status']
    projectID = request.form['projectID']
    taskID = request.form['taskID']
    if 'userID' not in session:  # if not logged in
        return render_template('login.html')

    userID = session['userID']
    role = session['role']

    # Here is the logic: do this in the state Go4 pattern areas
    # if new:
    #   - A Manager can assign a user. The status is changed to "assigned" (email worker?)
    #   - A worker can assign themselves. The status is changed to "assigned"
    # if assigned:
    #   - A Manager can un-assign a user. Making the status "new" (email worker?)
    #   - A Worker can select "complete". Making the status "reviewing" (email manager?)
    # if reviewing:
    #   - A Manager can select accept. Making the status "completed"
    #   - A Manager can select reject. Making the status "assigned" (email worker?)
    #   - A Worker can select cancel. Making the status "assigned"
    # if completed:
    #   - Do nothing

    try:
        con = mysql.connect()  # set up database connection
        cur = con.cursor()
        cur.execute("SELECT * FROM task WHERE taskID=%s", taskID) # get the task
        taskSQL = cur.fetchone()
    except:
        con.rollback()
        return redirect(url_for('taskDetails', projectID=projectID, taskID=taskID,
                                error="Error updating status"))

    finally:
        con.commit()
        con.close()


    task = Task()  # create task object
    task.set_taskID(taskSQL[0])
    task.set_name(taskSQL[1])
    task.set_effort(taskSQL[2])
    task.set_deadline(taskSQL[4])
    task.set_description(taskSQL[5])
    task.set_assigned_user(taskSQL[8])

    task.set_status(taskSQL[3])

    #status is updated in the State Go4 pattern
    # #(after some validation to ensure the status change is legal to the functionality requirements)


    taskName = task.get_name()

    if status == "assigned":
        #send email as the reviewing task is rejected
        reciever = task.get_assigned_user()
        message = "The reviewing task '" + taskName + "', has been rejected."
        progress_state = AssignedState()  # set the state function
        updatedStatus = progress_state.validate_status(task, userID, role)
        # set the status by sending to validation
    elif status == "reviewing":
        try:
            con = mysql.connect()  # set up database connection
            cur = con.cursor()
            cur.execute("SELECT projectLeader FROM project WHERE projectID=%s", projectID)
            reciever = cur.fetchone() #get the reciever
        except:
            reciever = 0
            con.rollback()
        finally:
            con.commit()
            con.close()
        message = "The task: '" + taskName +"' has been set to completed. Log in to accept / reject the task."
        progress_state = ReviewingState()
        updatedStatus = progress_state.validate_status(task, userID, role)
    elif status == "completed":
        progress_state = CompletedState()
        updatedStatus = progress_state.validate_status(task, userID, role)
    else:
        #send unassigned email
        reciever = task.get_assigned_user()
        message = "You are no longer assigned to the task: '" + task.get_name()
        progress_state = NewState()
        updatedStatus = progress_state.validate_status(task, userID, role)



    if updatedStatus != status:
        # if the updatedStatus is not the same as status sent, return the taskDetails page with the error
        return redirect(url_for('taskDetails', projectID=projectID, taskID=taskID, error=updatedStatus))
        # updatedStatus is set to an error message if not the status

    if(status != "completed"):
        sendEmail(reciever, message, taskName) # call the email sending function


    try:
        con = mysql.connect()  # set up database connection
        cur = con.cursor()
        cur.execute("UPDATE task SET status=%s WHERE taskID=%s", (updatedStatus, taskID))
    except:
        con.rollback()
        cur.execute("UPDATE task SET status=%s WHERE taskID=%s", (updatedStatus, taskID))
        return redirect(url_for('taskDetails', projectID=projectID, taskID=taskID,
                                error="Error updating status"))
    finally:
        con.commit()
        con.close()


    return redirect(url_for('taskDetails', projectID=projectID, taskID=taskID))  # route to task details page


@app.route('/updateEffort', methods=['POST', 'PATCH'])
def updateEffort(): #patch request for managers to update the relative effort of a task
    effort = request.form['effort']
    projectID = request.form['projectID']
    taskID = request.form['taskID']


    if 'userID' not in session:  # if not logged in
        return render_template('login.html')
    if session['role'] == "worker":
        return render_template('worker_home.html')
    try:
        con = mysql.connect()  # set up database connection
        cur = con.cursor()
        cur.execute("UPDATE task SET effort=%s WHERE taskID=%s", (effort, taskID))
    except:
        con.rollback()
    finally:
        con.commit()
        con.close()

    return redirect(url_for('taskDetails', projectID=projectID, taskID=taskID ))  # route to task details page


def sendEmail(reciever, message, taskName):
    try:
        con = mysql.connect()  # set up database connection
        cur = con.cursor()
        cur.execute("SELECT email FROM user WHERE userID=%s", reciever)
        #print("Email with user ID: " + str(reciever) + ". Has SQL results of: " + str(cur.fetchone()))
        for row in cur.fetchone():
            emailAddress = row
        print(emailAddress)
    except:
        emailAddress = "josephmcgeever23@gmail.com" # all fail emails go here
        con.rollback()
    finally:
        con.commit()
        con.close()
    message = Mail(
        from_email='josephmcgeever@hotmail.co.uk',
        to_emails=emailAddress,
        subject='Updated: ' + taskName,
        html_content=message)
    try:
        sg = SendGridAPIClient(os.environ.get('sendgrid_api_key'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.body)


if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.run()
