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
        for req in editor_req_data[search_term]:
            # Prevent exporting requirements that are not in use by this editor type
            if excluded_properties:
                if req["name"] in excluded_properties:
                    continue
            if "children" not in req and "value" in req:
                if "global" in req:
                    # Exclude requirements that are pointing to a global setting. The engine will take care of
                    # this at runtime since any global value stored in a file will become outdated as soon as the
                    # global setting is changed
                    if not req["global"]["active"]:
                        conv_data[req["name"]] = req["value"]
                else:
                    conv_data[req["name"]] = req["value"]
            elif "template" in req:
                # Templates are used for dynamic child creation, where each child is an instance of the template.
                # To allow this without causing key stomping issues, use a list of dicts
                template_instances = []
                for index in range(0, len(req["children"])):
                    child_data = req["children"][index]
                    template_instances.append(
                        {child_data["name"]: ConvertActionRequirementsToEngineFormat(child_data, "children")}
                    )

                conv_data[req["name"]] = template_instances
            else:
                conv_data[req["name"]] = ConvertActionRequirementsToEngineFormat(req, "children")

        return conv_data
    return None


def ConvertActionRequirementsToEditorFormat(editor_req, engine_req, search_term="requirements",
                                            excluded_properties: list = None):
    """
    Given an action_data dict for a single action, convert its structure into one usable by the HBEditor,
    then return it

    If excluded_properties is provided, any properties in that list will not be converted, and will not appear in the
    returned data
    """
    if search_term in editor_req:
        for index in range(0, len(editor_req[search_term])):
            req = editor_req[search_term][index]
            # Prevent importing requirements that are not in used by this editor type (They would
            # have been removed during exporting, so they wouldn't appear when importing)
            if excluded_properties:
                if req["name"] in excluded_properties:
                    continue
            if "children" not in req and "value" in req:
                if req["name"] in engine_req:
                    # If the requirement is present, but it does have a global option, then it's an override
                    if "global" in req:
                        req["global"]["active"] = False

                    req["value"] = engine_req[req["name"]]
                else:
                    if "global" in req:
                        req["global"]["active"] = True

            elif "template" in req:
                # We need to duplicate the template a number of times equal to the number of instances found
                # in the eng data, then update each copy using the eng data
                req["children"] = []
                eng_target = engine_req[req["name"]]
                for i in range(0, len(eng_target)):
                    template_copy = copy.deepcopy(req["template"])
                    ConvertActionRequirementsToEditorFormat(template_copy, eng_target[i][template_copy["name"]], "children")
                    req["children"].append(template_copy)

            elif "children" in req:
                ConvertActionRequirementsToEditorFormat(req, engine_req[req["name"]], "children")