"""
    The Heartbeat Engine is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    The Heartbeat Engine is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with the Heartbeat Engine. If not, see <https://www.gnu.org/licenses/>.
"""
import inspect
from HBEngine.Core.Actions import actions, transitions


class ActionManager:
    def __init__(self, scene):

        self.scene = scene
        self.active_actions = {}

    def Update(self, events):
        pending_completion = []
        if self.active_actions:
            # We can't edit the dict size while iterating, so if any actions are complete, store them and delete them
            # afterwards
            for action, null_val in self.active_actions.items():
                if action.complete is True:
                    pending_completion.append(action)
                else:
                    action.Update(events)
            if pending_completion:
                for action in pending_completion:
                    # We defer using completion delegates to here since, if actions could execute them, it might
                    # cause them to close prematurely. It's also difficult to have oversight on what actions might
                    # do, and what completion delegates may do. To avoid any confusion, always run the delegates just
                    # as the action is closing
                    if action.complete_delegate:
                        action.complete_delegate()
                    del self.active_actions[action]

    def PerformAction(self, action_data, action_name, complete_delegate=None):
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

        print(f"The provided action name is invalid: '{action_name}'. Please review the available actions, or "
              "add a new action function for the one provided")
        return None

    def GetTransition(self, transition_data):
        """
        Returns the object associated with the provided transition text
        """
        if 'type' in transition_data:
            transition = None

            # No transition specified
            if transition_data['type'] == 'None':
                return None

            available_transitions = inspect.getmembers(transitions, inspect.isclass)
            for transition, t_object in available_transitions:
                if transition_data['type'] == transition:
                    transition = t_object
                    break

            if transition is None:
                raise ValueError("The provided transition name is invalid. Please review the available transitions, "
                                 "or add a new action object for the one provided")
                return None

            return transition
        else:
            raise ValueError("No transition type specified - Unable to process transition")

    def CreateTransition(self, transition_data, renderable):
        transition = self.GetTransition(transition_data)

        if 'speed' in transition_data:
            return transition(self.scene, self, renderable, transition_data['speed'])
        else:
            return transition(self.scene, self, renderable)
