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

    def ConvertActionRequirementsToEngineFormat(self, editor_action_data, has_parent=None):
        """ Given an editor action requirements / children data dict, convert it to a format usable by the engine"""
        converted_action = {}

        term = "requirements"
        if has_parent:
            term = "children"

        if term in editor_action_data:
            for requirement in editor_action_data[term]:
                if ParameterType[requirement["type"]] != ParameterType.Container:

                    # Exclude requirements that are pointing to a global setting. The engine will take care of this at
                    # runtime since any global value stored in a file will become outdated as soon as the global setting
                    # is changed
                    if "global" in requirement:
                        if "active" in requirement["global"]:
                            if not requirement["global"]["active"]:
                                converted_action[requirement["name"]] = requirement["value"]
                    else:
                        converted_action[requirement["name"]] = requirement["value"]
                else:
                    converted_action[requirement["name"]] = self.ConvertActionRequirementsToEngineFormat(requirement, True)

            return converted_action
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

    def ConvertActionRequirementsToEditorFormat(self, editor_action_data, engine_action_data, has_parent=None):
        """
        Given engine & editor action requirements / children data dict, convert it to a format usable
        by the editor
        """
        term = "requirements"
        if has_parent:
            term = "children"

        # Compare the parameters that are in the file, and those that aren't. Any that aren't are assumed to be
        # using global params, and any that are will be using custom values. Account for this difference in the
        # settings
        if term in editor_action_data:
            for requirement in editor_action_data[term]:
                if ParameterType[requirement["type"]] != ParameterType.Container:

                    # If the requirement is present, and it does have a global option, then it's an override
                    if requirement["name"] in engine_action_data:
                        if "global" in requirement:
                            requirement["global"]["active"] = False

                        requirement["value"] = engine_action_data[requirement["name"]]
                    else:
                        if "global" in requirement:
                            requirement["global"]["active"] = True
                else:
                    self.ConvertActionRequirementsToEditorFormat(requirement, engine_action_data[requirement["name"]], True)

            return editor_action_data
        return None
