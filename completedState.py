"""GoF state pattern"""
from state import State


class CompletedState(State):

    def validate_status(self, context, userID, role):
        ### validation on status change ###
        oldStatus = context.get_status()
        if role != "manager":
            return "Only managers can set a task as 'completed'"
        if oldStatus != "reviewing":
            return "Only tasks that are set to be reviewed can be marked as completed"
        ### validation over ###

        context.set_status("completed")
        return "completed"
