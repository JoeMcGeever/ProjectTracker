""" This is the entity, User"""

class User:

    def __init__(self):  # a method to create objects
        self.__username = ""
        self.__email = ""
        self.__password = ""
        self.__role = ""

    def get_username(self):  # get method
        return self.__username

    def set_username(self, name):  # set method
        self.__username = name

    def get_email(self):  # get method
        return self.__email

    def set_email(self, email):  # set method
        self.__email = email

    def get_password(self):  # get method
        return self.__password

    def set_password(self, password):  # set method
        #encrypt here
        self.__password = password

    def get_role(self):  # get method
        return self.__role

    def set_role(self, role):  # set method
        self.__role = role