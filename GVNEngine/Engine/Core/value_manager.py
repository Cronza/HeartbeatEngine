import inspect

from Engine.Actions import actions
from Engine.Actions import transitions
from Engine.BaseClasses.transition import Transition

class ValueManager:
    def __init__(self, scene, settings):

        self.scene = scene

        self.scene.settings = settings


    def Request
















    def GetValue(self, action_name):
        """
        Returns the object associated with the provided action text
        """
        # Get a list of the action objects in the form of a list of tuples (object_name, object),
        # and use the given action text as a lookup for an action in the list. If found, return it, otherwise
        # return None
        available_actions = inspect.getmembers(actions, inspect.isclass)

        for action, object_ref in available_actions:
            if action_name == action:
                return object_ref

        print("The provided action name is invalid. Please review the available actions, or add a new action function "
              "for the one provided")
        return None

