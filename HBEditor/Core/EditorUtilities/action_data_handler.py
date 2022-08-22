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


def ConvertActionRequirementsToEngineFormat(editor_req_data: dict, search_term="requirements",
                                            excluded_properties: list = None):
    """
    Given an action_data dict for a single action, convert its structure into one usable by the HBEngine,
    then return it

    If excluded_properties is provided, any properties in that list will not be converted, and will not appear in the
    returned data
    """
    conv_data = {}
    if search_term in editor_req_data:
        for req_name, req_data in editor_req_data[search_term].items():
            # Prevent exporting requirements that are not in use by this editor type
            if excluded_properties:
                if req_name in excluded_properties:
                    continue
            if "children" not in req_data:
                # New data or data that hasn't been edited by the user won't have the 'value' key. In these cases,
                # generate the key using the value of the 'default' key
                if "value" not in req_data:
                    req_data["value"] = req_data["default"]
                if "global_active" in req_data:
                    # Exclude requirements that are pointing to a global setting. The engine will take care of
                    # this at runtime since any global value stored in a file will become outdated as soon as the
                    # global setting is changed
                    if not req_data["global_active"]:
                        conv_data[req_name] = req_data["value"]
                else:
                    conv_data[req_name] = req_data["value"]
            elif "template" in req_data:
                # Templates are used for dynamic child creation, where each child is an instance of the template.
                # To allow this without causing key stomping issues, use a list of dicts
                template_instances = []
                for child_req_name, child_req_data in req_data["children"]:
                    template_instances.append(
                        {child_req_name: ConvertActionRequirementsToEngineFormat(child_req_data, "children")}
                    )

                conv_data[req_name] = template_instances
            else:
                conv_data[req_name] = ConvertActionRequirementsToEngineFormat(req_data, "children")

        return conv_data
    return None


def ConvertActionRequirementsToEditorFormat(metadata_entry: dict, engine_entry: dict, search_term: str = "requirements",
                                            excluded_properties: list = None):
    """
    Given an action_data dict for a single action, convert its structure into one usable by the HBEditor,
    then return it

    If excluded_properties is provided, any properties in that list will not be converted, and will not appear in the
    returned data
    """
    for req_name, req_data in metadata_entry[search_term].items():
        # Prevent importing requirements that are not in used by this editor type (They would
        # have been removed during exporting, so they wouldn't appear when importing)
        if excluded_properties:
            if req_name in excluded_properties:
                continue
        if "children" not in req_data:
            # If the req entry isn't found in the engine action data, then it was likely omitted due to a global
            # setting being enabled
            if req_name in engine_entry:
                if "global" in req_data:
                    req_data["global_active"] = False
                req_data["value"] = engine_entry[req_name]
            else:
                if "global" in req_data:
                    req_data["global_active"] = True

        elif "template" in req_data:
            #@TODO: Review when the new action data structure has an example of this
            pass
            """
            # We need to duplicate the template a number of times equal to the number of instances found
            # in the engine data, then update each copy using the engine data
            req_data["children"] = []
            eng_target = engine_req[req_name]
            for i in range(0, len(eng_target)):
                template_copy = copy.deepcopy(req_data["template"])
                ConvertActionRequirementsToEditorFormat(template_copy, eng_target[template_copy["name"]], "children")
                req["children"].append(template_copy)
            """

        elif "children" in req_data:

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
