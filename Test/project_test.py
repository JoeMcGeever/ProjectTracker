import unittest
from project import Project
from task import Task


class TestProject(unittest.TestCase):

    def setUp(self):
        print("setUp")
        self.__project = Project()

    def tearDown(self):
        print("tearDown")
        del self.__project


if __name__ == '__main__':
    unittest.main()
