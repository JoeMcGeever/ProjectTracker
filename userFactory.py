#apply factory pattern here:

""" UserFactory"""
from manager import Manager
from worker import Worker


class UserFactory:

    def __init__(self):  # a method to create objects
        self.user = None

    def get_user(self, the_type):  # GoF factory method pattern
        if the_type is not None:
            if the_type.lower() == "manager":
                self.user = Manager()
            elif the_type.lower() == "worker":
                self.user = Worker()
            else:
                self.user = None

        return self.user





