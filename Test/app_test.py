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
        cur.execute('ALTER TABLE task AUTO_INCREMENT=1')
        cur.execute('ALTER TABLE project AUTO_INCREMENT=1')
        cur.execute('ALTER TABLE user AUTO_INCREMENT=1')
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


    def test_post_create_task(self):
        self.register('testUser', 'testEmail@email.com', 'testPassword', "manager")
        self.createProject('test project','2021-05-03', 'a test project')
        response = self.createTask('test task', '2021-05-03','a test task')
        print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Create a task' in response.data)




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
        with tester.session_transaction() as lSess:
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


if __name__ == '__main__':
    unittest.main()
