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
import inspect, operator
from typing import Type
from HBEngine.Core.Actions import actions, transitions
from HBEngine.Core import settings


active_actions = {}


def Update(events):
    global active_actions
    pending_completion = []
    if active_actions:
        # We can't edit the dict size while iterating, so if any actions are complete, store them and delete them
        # afterwards
        for action, null_val in active_actions.items():
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
                if action.completion_callback:
                    action.completion_callback()

                # Do one final confirmation that the action still exists in case the completion callback lead to the
                # deletion of the action in question (Commonly happens during scene changes)
                if action in active_actions:
                    del active_actions[action]


def Clear():
    """ Clears the list of all active actions, stopping any further updates """
    global active_actions
    active_actions.clear()


def PerformAction(action_data: dict, action_name: str, parent: object = None, completion_callback: callable = None, no_draw: bool = False) -> any:
    """
    Given an action_data YAML block and an action name, create and run the associated action. Return anything
    that the action opts to return
    """
    # Check conditions prior to loading the action
    if "conditions" in action_data:
        if action_data["conditions"]:
            print(action_data["conditions"])
            if not CheckCondition(action_data["conditions"]):
                # Condition not met - Do not execute this action
                return None



    # Fetch the action function corresponding to the next action index
    action = GetAction(action_name)
    new_action = action(
        simplified_ad=action_data,
        parent=parent,
        no_draw=no_draw
    )

    # If the calling function wishes to be informed when the action is completed, opt in here
    if completion_callback:
        new_action.completion_callback = completion_callback

    active_actions[new_action] = None

    # Actions can opt in to return data. Return whatever is returned from the underlying action
    return new_action.Start()


def GetAction(action_name: str) -> callable:
    """
    Returns the action class with a matching name to the provided name. Returns 'None' if the action isn't found
    """
    # Get a list of the action objects in the form of a list of tuples (object_name, object),
    # and use the given action text as a lookup for an action in the list. If found, return it, otherwise
    # return None
    available_actions = inspect.getmembers(actions, inspect.isclass)

    #@TODO: Review how to speed this up, as it seems inefficient
    for action, object_ref in available_actions:
        if action_name == action:
            return object_ref

    print(f"The provided action name is invalid: '{action_name}'. Please review the available actions, or "
          "add a new action function for the one provided")

    return None


def GetTransition(transition_data: dict) -> callable:
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


def CreateTransition(transition_data: dict, renderable):
    transition = GetTransition(transition_data)

    if 'speed' in transition_data:
        return transition(renderable, transition_data['speed'])
    else:
        return transition(renderable)


def CheckCondition(conditional_data: dict) -> bool:
    """ Given a dict of conditions, check each one. If all conditions are met, return True. Otherwise return False """
    operators = {
        'equal': operator.eq,
        'not_equal': operator.ne,
        'less': operator.lt,
        'less-or-equal': operator.le,
        'greater': operator.gt,
        'greater-or-equal': operator.ge,
    }

    # Loop through each condition and confirm whether it resolves to True or False. Every condition *must*
    # resolve to True in order for the overall condition to be considered met
    condition_met = True
    for con_name, con_data in conditional_data.items():
        cur_value_data = settings.GetVariable(con_data['variable'])

        # Equality operators support any data type, while numerical comparisons require that the value and goal
        # be numerical (Float or Int). If performing a numerical comparison, perform type enforcement
        if con_data['operator'] != 'equal' and con_data['operator'] != 'not_equal':

            if not con_data['goal'].isnumeric():
                raise ValueError(
                    f"Condition uses a numeric operator '{con_data['operator']}' but targets a non-numeric value: '{con_data['variable']}'")
            elif not cur_value_data.isnumeric():
                raise ValueError(
                    f"Condition uses a numeric operator '{con_data['operator']}' but targets a non-numeric goal: '{con_data['goal']}")

            # Cast the value and goal to float so the comparison applies properly
            if not operators[con_data['operator']](float(cur_value_data), float(con_data['goal'])):
                condition_met = False
                break

        if not operators[con_data['operator']](cur_value_data, con_data['goal']):
            condition_met = False
            break

    return condition_met

