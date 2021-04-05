"""GoF state pattern"""
from state import State


class NewState(State):

    def validate_status(self, context, userID, role):
        ### validation on status change ###
        if role != "manager":
            return "Must be a manager to do this operation"
        oldStatus = context.get_status()
        if(oldStatus!="assigned"):
            return "A task's status can only be updated to 'new' when an assigned user is set to be unassigned"
        ### validation over ###

        context.set_status("new") # set the status in the object
        return "new" # return 'new'


