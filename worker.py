""" This is the entity, Worker"""
from user import User


class Worker(User):

    def __init__(self):
        super().__init__()
        self._numberOfProjects = []


    def set_number_of_projects(self, list):
        self._numberOfProjects = list






