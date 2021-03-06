# apply composite pattern here - where tasks can have mini tasks beneath it (related tasks)
from state import State

""" This is the entity, Task"""


class Task:

    _taskID=""
    _name=""
    _effort=""
    _status=""
    _description = ""
    _deadine =""
    _assignedUser = 0
    _miniTasks =[]



    def __init__(self):
        super().__init__()
        self._taskID = None
        self._name = ""
        self._effort = 0
        self._status= "new"
        self._description = ""
        self._deadline = None
        self._assignedUser = None
        self._miniTasks = []  # composite pattern

    # composite pattern##

    def get_child_tasks(self):
        return self._miniTasks

    def add_child_task(self, child):
        if child is not None:
            self._miniTasks.append(child)

    def get_sub_taskIDs(self):
        taskIDs =[]
        for task in self._miniTasks:
            taskIDs.append(task.get_taskID())
        return taskIDs

    ####################

    def set_taskID(self, taskID):
        self._taskID = taskID

    def get_taskID(self):
        return self._taskID

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def get_effort(self):
        return self._effort

    def set_effort(self, effort):
        self._effort = effort

    def get_status(self):
        return self._status

    def set_status(self, status):
        self._status = status

    def get_description(self):
        return self._description

    def set_description(self, description):
        self._description = description

    def get_deadline(self):
        return self._deadline

    def set_deadline(self, deadline):
        self._deadline = deadline

    def get_assigned_user(self):
        return self._assignedUser

    def set_assigned_user(self, assignedUser):
        self._assignedUser = assignedUser