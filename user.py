""" This is the entity, User"""


class User:

    def __init__(self):  # a method to create objects
        self.__username = ""
        self.__email = ""
        self.__start_year = ""
        self.__role = ""
        # self.__profile = Profile()
        # self.__contract = Contract()

    def get_user_name(self):  # get method
        return self.__username

    def set_user_name(self, name):  # set method
        self.__username = name


# if __name__ == "__main__":
#     user = User()
#     user.set_start_year("2011")  # 01/01/2011
#     result = user.get_work_years()
#     print("result: " + str(result))
