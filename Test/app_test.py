import unittest
from app import app
from flaskext.mysql import MySQL
from flask import session


class TestCaseExamples(unittest.TestCase):

    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False

        app.config['MYSQL_DATABASE_USER'] = 'root'
        app.config['MYSQL_DATABASE_PASSWORD'] = ''
        app.config['MYSQL_DATABASE_DB'] = 'project_tracker_test'
        app.config['MYSQL_DATABASE_HOST'] = 'localhost'
        app.secret_key = 'super secret key' #needed for session storage usage
        self.app = app.test_client()

    # executed after each test
    def tearDown(self):
        mysql = MySQL()
        mysql.init_app(app)
        mysql.connect()
        con = mysql.connect()
        cur = con.cursor()
        cur.execute('DELETE FROM task')
        cur.execute('DELETE FROM project')
        cur.execute('DELETE FROM user')
        cur.execute('DELETE FROM children_tasks')
        cur.execute('ALTER TABLE task AUTO_INCREMENT=1')
        cur.execute('ALTER TABLE project AUTO_INCREMENT=1')
        cur.execute('ALTER TABLE user AUTO_INCREMENT=1')
        cur.execute('ALTER TABLE children_tasks AUTO_INCREMENT=1')
        con.commit()
        pass


    def test_reroute_to_login(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        print(response.data)
        self.assertTrue(b'Login' in response.data)

    def test_valid_worker_registration(self):
        response = self.register('testUser', 'testEmail@email.com', 'testPassword', "worker")
        self.assertEqual(response.status_code, 200)
        response = self.login('testUser', 'testPassword')
        self.assertTrue(b'Worker Home' in response.data)

    def test_valid_manager_registration(self):
        response = self.register('testUser', 'testEmail@email.com', 'testPassword', "manager")
        self.assertEqual(response.status_code, 200)
        response = self.login('testUser', 'testPassword')
        self.assertTrue(b'Manager Home' in response.data)

    def test_register_same_username_fails(self):
        response = self.register('testUser', 'testEmail@email.com', 'testPassword', "manager")
        self.assertEqual(response.status_code, 200)
        response = self.register('testUser', 'testEmail2@email.com', 'testPassword', "manager")
        print(response.data)
        self.assertTrue(b'username already in use' in response.data)

    def test_register_same_email_fails(self):
        response = self.register('testUser', 'testEmail@email.com', 'testPassword', "manager")
        self.assertEqual(response.status_code, 200)
        response = self.register('testUser2', 'testEmail@email.com', 'testPassword', "manager")
        self.assertTrue(b'email already in use' in response.data)

    def test_login_fail(self):
        response = self.login('testUser', 'testPassword')
        self.assertTrue(b'Invalid login details' in response.data)


    def test_post_create_project(self):
        self.register('testUser', 'testEmail@email.com', 'testPassword', "manager")
        response = self.createProject('test project','2021-05-03', 'a test project')
        self.assertTrue(b'Manager Home' in response.data) # test the user is at the home page (redirect)
        self.assertTrue(b'test project' in response.data) # test the project is now being displayed in the home page



    def test_post_create_task(self):
        self.register('testUser', 'testEmail@email.com', 'testPassword', "manager")
        self.createProject('test project', '2021-05-03', 'a test project')
        response = self.createTask('test task', '2021-05-03', 'a test task')
        print(response.data)
        self.assertTrue(b'Project Details' in response.data) # test the page redirects to the Project Details page
        self.assertTrue(b'test task' in response.data) # test the page also dispays the newly created task

    def test_post_sub_task(self):
        self.register('testUser', 'testEmail@email.com', 'testPassword', "manager")
        self.createProject('test project', '2021-05-03', 'a test project')
        self.createTask('test task', '2021-05-03', 'a test task')
        response = self.createSubTask('test sub task', '2021-04-02', 'sub task of "test task"', 1)
        self.assertTrue(b'Project Details' in response.data)  # test the page redirects to the Project Details page
        self.assertTrue(b'test sub task' in response.data)  # test that the sub task is viewable in the project page
        response = self.taskDetails(1, 1, 1) #get the task details of the projectID=1, taskID=1... This represents the parent task, while id=2 is the child
        self.assertTrue(b'Task Details' in response.data)  # test the page redirects to the Task Details page
        self.assertTrue(b'test sub task' in response.data)  # test that the sub task is viewable in the task page

    def test_post_assignAndUnassign_user(self):
        self.register('testUser', 'testEmail@email.com', 'testPassword', "manager")
        self.register('testWorker', 'testWorker@email.com', 'testWorkerPassword', "worker")
        self.createProject('test project', '2021-05-03', 'a test project')
        self.createTask('test task', '2021-05-03', 'a test task')
        response = self.taskDetails(1, 1, 1)
        print(response.data)
        self.assertTrue(b'Assigned:\n' in response.data)  # ensure the assigned user field is empty
        self.assertFalse(b'Assigned: 2' in response.data) # ensure the assigned user is not id 2
        response = self.assignUser(1, 1, 2) # assign userID = 2 (testWorker) to be the assigned user for task 1 in project 1
        self.assertTrue(b'Assigned: 2' in response.data)  # ensure the assigned user is not id 2
        response = self.removeUser(1, 1) # unassign the user in task id 1
        self.assertTrue(b'Assigned:\n' in response.data)  # ensure the assigned user field is empty
        self.assertFalse(b'Assigned: 2' in response.data)  # ensure the assigned user is not id 2
        self.assertFalse(b'Status: new' in response.data)  # ensure the status is set to "new" again



    def test_post_delete_task(self):
        self.register('testUser', 'testEmail@email.com', 'testPassword', "manager")
        self.createProject('test project', '2021-05-03', 'a test project')
        response = self.createTask('test task', '2021-05-03', 'a test task')
        self.assertTrue(b'Project Details' in response.data)  # test the page redirects to the Project Details page
        self.assertTrue(b'test task' in response.data)  # test that the task is viewable in the project page
        response = self.deleteTask(1, 1) # delete the task
        self.assertTrue(b'Project Details' in response.data)  # test the page redirects to the Project Details page
        self.assertFalse(b'test task' in response.data)  # test that the task is not viewable in the project page


    def test_post_delete_project(self):
        self.register('testUser', 'testEmail@email.com', 'testPassword', "manager")
        response = self.createProject('test project', '2021-05-03', 'a test project')
        self.assertTrue(b'Manager Home' in response.data)  # test the page redirects to the Home page
        self.assertTrue(b'test project' in response.data)  # test that the project is viewable in the home page
        response = self.deleteProject(1)
        self.assertTrue(b'Manager Home' in response.data)  # test the page redirects to the home page
        self.assertFalse(b'test project' in response.data)  # test that the project is no longer there

    def test_update_effort(self):
        self.register('testUser', 'testEmail@email.com', 'testPassword', "manager")
        self.createProject('test project', '2021-05-03', 'a test project')
        self.createTask('test task', '2021-05-03', 'a test task')
        response = self.taskDetails(1, 1, 1) # get newly created task
        self.assertTrue(b'<input name="effort" value="0" />' in response.data) # check to see if effort is 0
        response = self.updateEffort(1, 1, 8) #update the task with id 1 in project id 1, to have an effort of 8
        self.assertTrue(b'<input name="effort" value="8" />' in response.data) # check to see if effort is 8


    def test_update_status_newToAssigned_manager(self):
        self.register('testUser', 'testEmail@email.com', 'testPassword', "manager") # will have userID = 1
        self.register('testWorker', 'testWorker@email.com', 'testPassword', "worker") # will have userID = 2
        self.register('testWorker2', 'testWorker2@email.com', 'testPassword', "worker")  # will have userID = 3
        self.createProject('test project', '2021-05-03', 'a test project')
        self.createTask('test task', '2021-05-03', 'a test task')
        response = self.taskDetails(1, 1, 1) # view task1 in project1 as user1
        self.assertTrue(b'Status: new' in response.data) # test the status is currently new
        response = self.assignUser(1, 1, 2) # assign user with id 2 to task 1 project 1
        self.assertTrue(b'Status: assigned' in response.data)  # test the status is currently new
        # test to see if assigned user can see the task
        response = self.taskDetails(1, 1, 2) # view task1 in project1 as user 2 (worker who is now assigned)
        self.assertTrue(b'Status: assigned' in response.data)  # test the status is currently new
        self.assertTrue(b'Completed?' in response.data) # test to see if the user has an option to set the task as completed
        # test to see if unassigned user can complete the task
        response = self.taskDetails(1, 1, 3)  # view task1 in project1 as user 2 (worker who is now assigned)
        self.assertTrue(b'Status: assigned' in response.data)  # test the status is currently assigned
        self.assertFalse(b'Completed?' in response.data)  # test to see if the user has the option to complete the task

    def test_update_status_newToAssigned_worker(self):
        self.register('testUser', 'testEmail@email.com', 'testPassword', "manager")  # will have userID = 1
        self.register('testWorker', 'testWorker@email.com', 'testPassword', "worker")  # will have userID = 2
        self.createProject('test project', '2021-05-03', 'a test project')
        self.createTask('test task', '2021-05-03', 'a test task') # taskID = 1
        self.createTask('test task2', '2021-05-03', 'a test task2') # taskID = 2
        self.assignUser(1, 1, 2) # assign the user to a task so they can view the project
        response = self.login('testWorker', 'testPassword')
        self.assertTrue(b'test project' in response.data) #check to see if the user can see the project now
        response = self.taskDetails(1, 2, 2)
        self.assertTrue(b'Assign to me' in response.data) #test if user has the chance to assign a different task to themlselves
        response = self.updateStatus("assigned", 2, 2, 'worker') # assign userID 2, to task2 on project 1 as a worker
        self.assertTrue(b'Status: assigned' in response.data)  # test the status is currently assigned
        self.assertFalse(b'Completed?' in response.data)  # test to see if the user has the option to complete it







    def test_update_status_assignedToReviewing_worker(self):
        self.register('testUser', 'testEmail@email.com', 'testPassword', "manager")  # will have userID = 1
        self.register('testWorker', 'testWorker@email.com', 'testPassword', "worker")  # will have userID = 2
        self.createProject('test project', '2021-05-03', 'a test project')
        self.createTask('test task', '2021-05-03', 'a test task')  # taskID = 1
        self.assignUser(1, 1, 2)  # assign the user to a task so they can view the project
        self.updateStatus("reviewing", 1, 1, 'worker') # set the status of the event as 'reviewing'
        response = self.taskDetails(1, 1, 2) # view the task as the worker
        self.assertTrue(
            b'reviewing' in response.data)  # test if the task is set to "reviewing"

    def test_update_status_rejectReviewing_manager(self):
        self.register('testUser', 'testEmail@email.com', 'testPassword', "manager")  # will have userID = 1
        self.register('testWorker', 'testWorker@email.com', 'testPassword', "worker")  # will have userID = 2
        self.createProject('test project', '2021-05-03', 'a test project')
        self.createTask('test task', '2021-05-03', 'a test task')  # taskID = 1
        self.assignUser(1, 1, 2)  # assign the user to a task so they can view the project
        self.updateStatus("reviewing", 1, 1, 'worker')  # set the status of the event as 'reviewing'
        response = self.taskDetails(1, 1, 1)  # view the task as the manager
        self.assertTrue(b'<input type = "submit" value = "Accept" />' in response.data)  # test if the manager can accept the reviewing task
        self.assertTrue(
            b'<input type = "submit" value = "Reject" />' in response.data)  # test if the manager can reject the reviewing task
        response = self.updateStatus("assigned", 1, 1, 'manager')
        print(response.data)
        self.assertTrue(b'Status: assigned' in response.data)

    def test_update_status_acceptReviewing_manager(self):
        self.register('testUser', 'testEmail@email.com', 'testPassword', "manager")  # will have userID = 1
        self.register('testWorker', 'testWorker@email.com', 'testPassword', "worker")  # will have userID = 2
        self.createProject('test project', '2021-05-03', 'a test project')
        self.createTask('test task', '2021-05-03', 'a test task')  # taskID = 1
        self.assignUser(1, 1, 2)  # assign the user to a task so they can view the project
        self.updateStatus("reviewing", 1, 1, 'worker')  # set the status of the event as 'reviewing'
        response = self.updateStatus("completed", 1, 1, 'manager') #manager accepts the changes
        self.assertTrue(b'Status: completed' in response.data) # check to see if status is now completed









        # helper methods
    def register(self, username, email, password, role):
        tester = app.test_client(self)
        return tester.post(
            '/register',
            data=dict(username=username, email=email, password=password, role=role),
            follow_redirects=True
        )

    def login(self, username, password):
        tester = app.test_client(self)
        return tester.post(
            '/login',
            data=dict(username=username, password=password),
            follow_redirects=True
        )

    def logout(self):
        tester = app.test_client(self)
        return tester.get(
            '/logout',
            follow_redirects=True
        )

    def createProject(self, name, deadline, description):
        tester = app.test_client(self)
        with tester.session_transaction() as lSess: #set session variables
                lSess['userID'] = 1
                lSess['role'] = 'manager'
        return tester.post(
            '/createProject',
            data=dict(name=name, deadline=deadline, description=description),
            follow_redirects=True
        )

    def createTask(self, name, deadline, description):
        tester = app.test_client(self)
        with tester.session_transaction() as lSess:
            lSess['userID'] = 1
            lSess['role'] = 'manager'
        return tester.post(
            '/createTask',
            data=dict(name=name, deadline=deadline, description=description, projectID=1),
            follow_redirects=True
        )

    def createSubTask(self, name, deadline, description, parentTaskID):
        tester = app.test_client(self)
        with tester.session_transaction() as lSess:
            lSess['userID'] = 1
            lSess['role'] = 'manager'
        return tester.post(
            '/createSubTask',
            data=dict(parentTaskID=parentTaskID, name=name, deadline=deadline, description=description, projectID=1),
            follow_redirects=True
        )

    def taskDetails(self, projectID, taskID, userID):
        tester = app.test_client(self)
        if(userID==1):
            role = 'manager'
        else:
            role = 'worker'
        with tester.session_transaction() as lSess:
            lSess['userID'] = userID
            lSess['role'] = role
        return tester.get('/taskDetails?projectID=' + str(projectID) + '&taskID=' + str(taskID))

    def projectDetails(self, projectID):
        tester = app.test_client(self)
        with tester.session_transaction() as lSess:
            lSess['userID'] = 1
            lSess['role'] = 'manager'
        return tester.get('/project?projectID=' + str(projectID))

    def assignUser(self, projectID, taskID, userID):
        tester = app.test_client(self)
        with tester.session_transaction() as lSess:
            lSess['userID'] = 1
            lSess['role'] = 'manager'
        return tester.post(
            '/assignUser',
            data=dict(userID=userID, taskID=taskID, projectID=projectID),
            follow_redirects=True
        )

    def updateEffort(self, projectID, taskID, effort):
        tester = app.test_client(self)
        with tester.session_transaction() as lSess:
            lSess['userID'] = 1
            lSess['role'] = 'manager'
        return tester.post(
            '/updateEffort',
            data=dict(effort=effort, taskID=taskID, projectID=projectID),
            follow_redirects=True
        )


    def removeUser(self, projectID, taskID):
        tester = app.test_client(self)
        with tester.session_transaction() as lSess:
            lSess['userID'] = 1
            lSess['role'] = 'manager'
        return tester.post(
            '/removeUser',
            data=dict(taskID=taskID, projectID=projectID),
            follow_redirects=True
        )

    def deleteTask(self, projectID, taskID):
        tester = app.test_client(self)
        with tester.session_transaction() as lSess:
            lSess['userID'] = 1
            lSess['role'] = 'manager'
        return tester.post(
            '/deleteTask',
            data=dict(taskID=taskID, projectID=projectID),
            follow_redirects=True
        )

    def deleteProject(self, projectID):
        tester = app.test_client(self)
        with tester.session_transaction() as lSess:
            lSess['userID'] = 1
            lSess['role'] = 'manager'
        return tester.post(
            '/deleteProject',
            data=dict(projectID=projectID),
            follow_redirects=True
        )


    def updateStatus(self, status, projectID, taskID, role):
        tester = app.test_client(self)
        if(role=="worker"):
            userID = 2
        else:
            userID = 1
        with tester.session_transaction() as lSess:
            lSess['userID'] = userID
            lSess['role'] = role
        return tester.post(
            '/updateStatus',
            data=dict(projectID=projectID, taskID=taskID, status=status),
            follow_redirects=True
        )



if __name__ == '__main__':
    unittest.main()
