"""GoF state pattern"""
from state import State



class ReviewingState(State):

    def validate_status(self, context, userID, role):
        ### validation on status change ###
        oldStatus = context.get_status()
        if oldStatus != "assigned":
            return "Nobody has been assigned the work for it to be reviewed"
        elif userID != context.get_assigned_user():
            return "This user is not the assigned user"
        ### validation over ###

        context.set_status("reviewing")



        return "reviewing"
