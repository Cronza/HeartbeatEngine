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


def ConvertActionRequirementsToEngineFormat(editor_req_data: dict, search_term="requirements",
                                            excluded_properties: list = None):
    """
    Given an action_data dict for a single action, convert its structure into one usable by the HBEngine,
    then return it. If 'excluded_properties' is provided, any properties in that list will not be converted, and will
    not appear in the returned data. If any items are missing the 'flags' key, they will also not be returned
    """
    conv_data = {}
    if search_term in editor_req_data:
        for req_name, req_data in editor_req_data[search_term].items():
            if excluded_properties:
                if "flags" in req_data:
                    # Prevent exporting requirements that are not in use by this editor type unless exempted
                    if req_name in excluded_properties and "no_exclusion" not in req_data["flags"]:
                        continue

            if "global" in req_data:
                if "flags" in req_data:
                    # Exclude requirements that are pointing to a global setting. The engine will take care of
                    # this at runtime since any global value stored in a file will become outdated as soon as the
                    # global setting is changed
                    if "global_active" not in req_data["flags"]:
                        conv_data[req_name] = req_data["value"]

            elif "value" in req_data:
                if "flags" in req_data:
                    # Exclude parameters that don't have any flags. These are, by default, not editable
                    # Containers don't have the 'value' key
                    conv_data[req_name] = req_data["value"]

            if "children" in req_data:
                conv_data[req_name] = ConvertActionRequirementsToEngineFormat(req_data, "children")

        return conv_data
    return None


def ConvertActionRequirementsToEditorFormat(metadata_entry: dict, engine_entry: dict, search_term: str = "requirements",
                                            excluded_properties: list = None):
    """
    Given a clone of a metadata entry (IE. 'create_text'), update it using the provided engine data making it usable by
    the HBEditor.

    If excluded_properties is provided, any properties in that list will not be converted, and will not appear in the
    returned data
    """
    # Some actions may save without any requirement data
    if engine_entry:
        for req_name, req_data in metadata_entry[search_term].items():
            # Prevent importing requirements that are not in used by this editor type (They would
            # have been removed during exporting, so they wouldn't appear when importing)
            if excluded_properties:
                if req_name in excluded_properties:
                    continue

            if req_data["type"] == "Event":
                # Event types have a unique data structure in that they have generated children based on another
                # action's metadata. Since this data comes from outside the scope of this action, we have to perform
                # a second cloning
                #
                # The first child key in the imported block is the 'action' key, which is specially created to
                # house the value of the input_widget (IE. 'load_scene' -> {'action': 'load_scene'}). Using this action
                # key, clone the corresponding metadata and update it
                #
                # If the action block is missing, it's assumed the user selected the null option, or "None". Since this
                # represents "do nothing", we don't load it in this case
                if engine_entry[req_name]:
                    event_target_metadata = copy.deepcopy(settings.action_metadata[engine_entry[req_name]["action"]])
                    req_data["children"] = {
                        "action": {
                            "type": "String",
                            "value": engine_entry[req_name]["action"],
                            "flags": ["no_exclusion"]
                        }
                    }
                    # Merge in the target req metadata
                    req_data["children"].update(event_target_metadata["requirements"])

                    # By default, 'value' will be the entire child dict (IE. {'action': ..., 'scene_file': ...})
                    # Since events use an input_widget, we need to change 'value' to something more appropriate
                    req_data["value"] = engine_entry[req_name]["action"]

            if "template" in req_data:
                # We need to duplicate the template a number of times equal to the number of instances found
                # in the engine data, then update each copy using the engine data
                req_data["children"] = {}

                for eng_inst_name, eng_inst_data in engine_entry[req_name].items():
                    template_copy = copy.deepcopy(req_data["template"])
                    template_copy_name = GetActionName(req_data["template"])
                    template_copy_data = template_copy[template_copy_name]

                    ConvertActionRequirementsToEditorFormat(template_copy_data, eng_inst_data, "children")  # @todo: This is only touching one entry

                    # Since actions that use the 'template' key generate their children, the top level key names are
                    # likely unique, where-as the name used in the metadata is generic (IE. 'choice' vs 'choice_01').
                    # We need to update the template copy to use the unique key names from the eng data
                    req_data["children"][eng_inst_name] = template_copy_data

            elif "children" not in req_data:
                if req_name in engine_entry:
                    if "global" in req_data:
                        RemoveFlag("global_active", req_data)
                    req_data["value"] = engine_entry[req_name]
                else:
                    if "global" in req_data:
                        # If the req entry isn't found in the engine action data, then it was likely omitted due to a
                        # global setting being enabled
                        AddFlag("global_active", req_data)

            if "children" in req_data:
                ConvertActionRequirementsToEditorFormat(req_data, engine_entry[req_name], "children")


def GetActionName(action_data: dict) -> str:
    """
    Retrieve the action name used as the top level key for the provided action_data

    This function is meant to be used by classes that cloned a piece of metadata from the actions_metadata.yaml file
    """
    return next(iter(action_data))


def GetActionDisplayName(action_data: dict) -> str:
    """
    Retrieve the display name value nested within the provided action_data

    This function is meant to be used by classes that cloned a piece of metadata from the actions_metadata.yaml file
    """
    return action_data[GetActionName(action_data)]["display_name"]


def GetActionRequirements(action_data: dict) -> dict:
    """
    Retrieve the requirements dict nested within the provided action_data

    This function is meant to be used by classes that cloned a piece of metadata from the actions_metadata.yaml file
    """
    return action_data[GetActionName(action_data)]["requirements"]


def AddFlag(name: str, req_data: dict):
    """ Adds the provided string to the provided requirements dict if it doesn't already exist """
    if name not in req_data["flags"]:
        req_data["flags"].append(name)

def RemoveFlag(name: str, req_data: dict):
    """ Removes the provided string from the provided requirements dict if it exists """
    if name in req_data["flags"]:
        req_data["flags"].remove(name)
