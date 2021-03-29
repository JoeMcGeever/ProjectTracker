""" This is the entity, Manager"""
from user import User


class Manager(User):

    def __init__(self):
        super().__init__()
        self._projects = []

    def get_projects(self):
        return self._projects

    def set_projects(self, list):
        self._projects = list

