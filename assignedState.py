"""GoF state pattern"""
from state import State


class AssignedState(State):

    def validate_status(self, context, userID, role):
        ### validation on status change ###
        oldStatus = context.get_status()
        if oldStatus == "new" and role == "worker":
            context.set_assigned_user(userID) # the worker themselves has assigned the task to them
        elif oldStatus == "reviewing" and role == "worker":
            return "Only Managers can reject a task in the 'reviewing' state"
        elif oldStatus!="new" and oldStatus!="reviewing":
            return "Task must be in the 'new' or 'reviewing' state to be assigned"
        ### validation over ###

        context.set_status("assigned")

        return "assigned"
