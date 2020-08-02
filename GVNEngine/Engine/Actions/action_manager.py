import inspect

from Engine.Actions import actions


class ActionManager:
    def __init__(self, scene, settings):

        # Allow actions to disable user input
        self.canProceed = False

        # The currently active scene
        self.scene = scene

        self.settings = settings

    def PerformAction(self, action_data):
        """ Loads the next action in the dialogue sequence, then increments the dialogue index"""

        # Fetch the action function corresponding to the next action index
        action = self.GetActionFunction(action_data['action'])
        action(self.scene, action_data)


    def GetActionFunction(self, action_name):
        """ Returns the function object associated with the provided action text
        """
        # Get a list of the action functions in the form of a list of tuples (function_name, function),
        # and use the given action text as a lookup for an action in the list. If found, return it, otherwise
        # return None
        available_actions = inspect.getmembers(actions, inspect.isfunction)

        for action, function in available_actions:
            if action_name == action:
                return function

        print("The provided action name is invalid. Please review the available actions, or add a new action function"
              "for the one provided")
        return None