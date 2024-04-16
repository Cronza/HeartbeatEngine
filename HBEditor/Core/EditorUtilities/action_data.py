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
import copy
from HBEditor.Core import settings


def ConvertParamDataToEngineFormat(editor_param_data: dict, excluded_properties: list = None, force_when_no_change: bool = False):
    """
    Given a dict of parameter data (typically for an action), convert its structure into one usable by the HBEngine,
    then return it.

    - If 'excluded_properties' is provided, any parameters in that list will not be converted, and will
    not appear in the returned data. If any items are missing the 'flags' key, they will also not be returned. If any
    items have a 'value' that matches 'default', they will also not be returned.

    - If 'force_when_no_change' is provided, items with 'value' that match 'default' are returned
    """
    conv_data = {}

    for param_name, param_data in editor_param_data.items():
        if excluded_properties:
            if "flags" in param_data:
                # Prevent exporting parameters that are not in use by this editor type (unless using 'no_exclusion')
                if param_name in excluded_properties and "no_exclusion" not in param_data["flags"]:
                    continue

        if "global" in param_data:
            if "flags" in param_data:
                # Exclude parameters that are pointing to a global setting. The engine will take care of
                # this at runtime since any global value stored in a file will become outdated as soon as the
                # global setting is changed
                if "global_active" not in param_data["flags"]:
                    conv_data[param_name] = param_data["value"]

        elif "value" in param_data:
            # Exclude parameters that don't have any flags. These are, by default, not editable
            # Containers don't have the 'value' key
            if "flags" in param_data:
                if force_when_no_change or 'default' not in param_data:
                    conv_data[param_name] = param_data["value"]
                elif 'default' in param_data:
                    if param_data["value"] != param_data["default"]:
                        conv_data[param_name] = param_data["value"]

        if "children" in param_data:
            conv_data[param_name] = ConvertParamDataToEngineFormat(param_data["children"])

    return conv_data


def ConvertActionDataToEditorFormat(action_data: dict, base_action_data: dict, excluded_properties: list = None):
    """
    Given a clone of an action's base ACTION_DATA, update it using the provided action data making it usable by
    the HBEditor.

    If excluded_parameters is provided, any properties in that list will not be converted, and will not appear in the
    returned data
    """
    # Some actions may save without any requirement data
    if action_data:
        for base_param_name, base_param_data in base_action_data.items():

            # Prevent importing parameters that are not in used by this editor type (They would
            # have been removed during exporting, so they wouldn't appear when importing)
            if excluded_properties:
                if base_param_name in excluded_properties:
                    continue

            if base_param_data["type"] == "Event":
                # Event types have a unique data structure in that they have generated children based on another
                # action's ACTION_DATA. Since this data comes from outside the scope of this action, we have to perform
                # a second cloning
                #
                # The first child key in the imported block is the 'action' key, which is specially created to
                # house the value of the input_widget (IE. 'load_scene' -> {'action': 'load_scene'}). Using this action
                # key, clone the corresponding metadata and update it
                #
                # If the action block is missing, it's assumed the user selected the null option, or "None". Since this
                # represents "do nothing", we don't load it in this case
                if action_data[base_param_name]:
                    base_param_data["children"] = {
                        "action": {
                            "type": "String",
                            "value": action_data[base_param_name]["action"],
                            "flags": ["no_exclusion"]
                        }
                    }
                    # Merge in the target parameters
                    event_target_base_ad = copy.deepcopy(settings.GetActionData(action_data[base_param_name]["action"]))
                    base_param_data["children"].update(event_target_base_ad)

                    # By default, 'value' will be the entire child dict (IE. {'action': ..., 'scene_file': ...})
                    # Since events use an input_widget, we need to change 'value' to something more appropriate
                    base_param_data["value"] = action_data[base_param_name]["action"]

            if "template" in base_param_data:
                # We need to duplicate the template a number of times equal to the number of instances found
                # in the engine data, then update each copy using the engine data
                base_param_data["children"] = {}

                for inst_name, inst_data in action_data[base_param_name].items():
                    template_copy = copy.deepcopy(base_param_data["template"])
                    template_copy_name = GetActionName(base_param_data["template"])
                    template_copy_data = template_copy[template_copy_name]

                    ConvertActionDataToEditorFormat(
                        base_action_data=template_copy_data["children"],
                        action_data=inst_data
                    )

                    # Since actions that use the 'template' key generate their children, the top level key names are
                    # likely unique, where-as the name used in the metadata is generic (IE. 'choice' vs 'choice_01').
                    # We need to update the template copy to use the unique key names from the eng data
                    base_param_data["children"][inst_name] = template_copy_data

            elif "children" not in base_param_data:
                if base_param_name in action_data:
                    if "default" in base_param_data and "value" not in base_param_data:
                        base_param_data["value"] = settings.user_project_data[base_param_data['default'][0]][base_param_data['default'][1]]['value']
                    else:
                        base_param_data["value"] = action_data[base_param_name]
                else:
                    if "global" in base_param_data:
                        # If the req entry isn't found in the engine action data, then it was likely omitted due to a
                        # global setting being enabled
                        AddFlag("global_active", base_param_data)

            if "children" in base_param_data:
                # Ensure the param in the base AD exists in the supplied AD
                if base_param_name in action_data:
                    ConvertActionDataToEditorFormat(
                        base_action_data=base_param_data["children"],
                        action_data=action_data[base_param_name]
                    )


def GetActionName(action_data: dict) -> str:
    """
    Retrieve the action name used as the top level key for the provided action_data
    """
    return next(iter(action_data))


def AddFlag(name: str, req_data: dict):
    """ Adds the provided string to the provided requirements dict if it doesn't already exist """
    if name not in req_data["flags"]:
        req_data["flags"].append(name)

def RemoveFlag(name: str, req_data: dict):
    """ Removes the provided string from the provided requirements dict if it exists """
    if name in req_data["flags"]:
        req_data["flags"].remove(name)
