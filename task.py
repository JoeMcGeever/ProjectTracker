# apply composite pattern here - where tasks can have mini tasks beneath it (related tasks)

""" This is the entity, Task"""


class Task:

    def __init__(self):
        super().__init__()
        self._name = ""
        self._effort = ""
        self._description = ""
        self._deadline = None
        self._assignedUser = ""
        self._miniTasks = []  # composite pattern

    # composite pattern##
    def get_child_tasks(self):
        return self._miniTasks

    def add_child_task(self, child):
        self._miniTasks.append(child)

    ####################

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def get_effort(self):
        return self._effort

    def set_effort(self, effort):
        self._effort = effort

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