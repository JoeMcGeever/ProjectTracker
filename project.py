""" This is the entity, Project"""
from task import Task

class Project:

    def __init__(self):
        super().__init__()
        self._tasks = []
        self._name = ""
        self._deadline = None
        self._projectLeader = ""
        self._description = ""

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def get_deadline(self):
        return self._deadline

    def set_deadline(self, deadline):
        self._deadline = deadline

    def get_tasks(self):
        return self._tasks
    

    def add_task(self, task):
        taskToAdd = Task()
        print(taskToAdd.set_taskID())
        self._tasks.append(task)

    def get_project_leader(self):
        return self._projectLeader()

    def set_project_leader(self, leader):
        self._projectLeader = leader

    def get_description(self):
        return self.description()

    def set_description(self, description):
        self._description = description