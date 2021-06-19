import inspect

from Engine.Actions import actions
from Engine.Actions import transitions
from Engine.BaseClasses.transition import Transition

class ActionManager:
    def __init__(self, scene, settings):

        self.scene = scene
        self.active_actions = {}
        self.scene.settings = settings

    def Update(self):
        pending_completion = []
        if self.active_actions:
            # We can't edit the dict size while iterating, so if any actions are complete, store them and delete them
            # afterwards
            for action in self.active_actions:
                if action.complete is True:
                    pending_completion.append(action)
                else:
                    action.Update()
            if pending_completion:
                for action in pending_completion:
                    # Use the complete delegate if its available
                    if action.complete_delegate:
                        action.complete_delegate()
                    del self.active_actions[action]

    def PerformAction(self, action_data, action_name, complete_delegate = None):
        """
        Given an action_data YAML block and an action name, create and run the associated action
        """

        # Fetch the action function corresponding to the next action index
        action = self.GetAction(action_name)
        new_action = action(self.scene, action_data, self)

        # If the calling function wishes to be informed when the action is completed, opt in here
        if complete_delegate:
            new_action.complete_delegate = complete_delegate

        self.active_actions[new_action] = None

        # Actions can opt in to return data. Return whatever is returned from the underlying action
        return new_action.Start()

    def GetAction(self, action_name):
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

    def GetTransition(self, transition_data):
        """
        Returns the object associated with the provided transition text
        """
        if 'type' in transition_data:
            transition = None

            available_transitions = inspect.getmembers(transitions, inspect.isclass)
            for transition, t_object in available_transitions:
                if transition_data['type'] == transition:
                    transition = t_object
                    break

            # The given transition name was not found, thus not populating 'transition' properly
            if transition is None:
                print("The provided transition name is invalid. Please review the available transitions, or add a new action "
                      "object for the one provided")
                return None

            return transition

            #if 'speed' in transition_data:
            #    #return transition(self, self.scene, renderable, transition_data['speed'])
            #else:
            #    print("Transition Speed not specified - Resorting to default")
            #    return transition(self, self.scene, renderable)
        else:
            print('No transition type specified - Unable to process transition')

    def CreateTransition(self, transition_data, renderable):
        transition = self.GetTransition(transition_data)

        if 'speed' in transition_data:
            return transition(self.scene, self, renderable, transition_data['speed'])
        else:
            return transition(self.scene, self, renderable)
