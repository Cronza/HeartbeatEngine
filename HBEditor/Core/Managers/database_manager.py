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
from HBEditor.Core.settings import Settings
from HBEditor.Core.DataTypes.parameter_types import ParameterType


class DBManager:
    """ A manager dedicated to actions that interface with the ActionDatabase """

    def ConvertDialogueFileToEngineFormat(self, action_data: dict):
        """
        Given a full dict of dialogue file data in editor format (branches and all), convert it to the engine format
        Return the converted dict
        """
        new_dialogue_data = {}
        for branch_name, branch_data in action_data.items():
            converted_branch = {
                "description": branch_data["description"]
            }

            converted_entries = []
            for editor_action in branch_data["entries"]:
                # Get the action name
                converted_action = {"action": editor_action["action_name"]}

                # Collect a converted dict of all requirements for this action (If any are present)
                converted_requirements = self.ConvertActionRequirementsToEngineFormat(editor_action)
                if converted_requirements:
                    converted_action.update(converted_requirements)

                # Add the newly converted action
                converted_entries.append(converted_action)

            # Complete the converted branch, and add it to the new dialogue data
            converted_branch["entries"] = converted_entries
            new_dialogue_data[branch_name] = converted_branch

        return new_dialogue_data

    def ConvertActionRequirementsToEngineFormat(self, editor_req_data, search_term="requirements"):
        conv_data = {}

        if search_term in editor_req_data:
            for req in editor_req_data[search_term]:
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
                            {child_data["name"]: self.ConvertActionRequirementsToEngineFormat(child_data, "children")}
                        )

                    conv_data[req["name"]] = template_instances
                else:
                    conv_data[req["name"]] = self.ConvertActionRequirementsToEngineFormat(req, "children")

            return conv_data
        return None

    def ConvertDialogueFileToEditorFormat(self, action_data):
        """
        Given a full dict of dialogue file data in engine format (branches and all), convert it to the editor format by
        rebuilding the structure based on lookups in the ActionDatabase
        """
        #@TODO: Investigate how to speed this up. The volume of O(n) searching is worrying
        new_dialogue_data = {}

        for branch_name, branch_data in action_data.items():
            converted_entries = []
            for action in branch_data["entries"]:
                action_name = action["action"]

                # Using the name of the action, look it up in the ActionDatabase. From there, we can build the new
                # structure
                database_entry = None
                for cat_name, cat_data in Settings.getInstance().action_database.items():
                    for option in cat_data["options"]:
                        if action_name == option['action_name']:
                            database_entry = copy.deepcopy(option)
                            break

                    if database_entry:
                        break
                # Pass the entry by ref, and let the convert func edit it directly
                self.ConvertActionRequirementsToEditorFormat(database_entry, action)
                converted_entries.append(database_entry)

            branch_data["entries"] = converted_entries
            new_dialogue_data[branch_name] = branch_data

        return new_dialogue_data

    def ConvertActionRequirementsToEditorFormat(self, editor_req, engine_req, search_term="requirements"):
        if search_term in editor_req:
            for index in range(0, len(editor_req[search_term])):
                req = editor_req[search_term][index]

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
                        self.ConvertActionRequirementsToEditorFormat(template_copy, eng_target[i][template_copy["name"]], "children")
                        req["children"].append(template_copy)

                elif "children" in req:
                    self.ConvertActionRequirementsToEditorFormat(req, engine_req[req["name"]], "children")
