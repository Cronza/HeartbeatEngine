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

class DBManager:
    """ A manager dedicated to actions that interface with the ActionDatabase """

    def ConvertDialogueFileToEngineFormat(self, action_data: dict):
        """
        Given a full dict of dialogue file data in editor format (branches and all), convert it to the engine format
        Return the converted dict
        """
        converted_dict = {}
        for branch in action_data.items():
            branch_name = branch[0]
            action_list = []
            for editor_action in branch[1]:
                # Get the action name
                converted_action = {'action': editor_action['action_name']}

                # Collect a converted dict of all requirements for this action (If any are present)
                converted_data = self.ConvertActionRequirementsToEngineFormat(editor_action)
                if converted_data:
                    converted_action.update(converted_data)

                # Add it to the final list of actions
                action_list.append(converted_action)

            # Add the list of actions under the target branch
            converted_dict[branch_name] = action_list

        return converted_dict

    def ConvertActionRequirementsToEngineFormat(self, editor_action_data, has_parent=None):
        """ Given an editor action requirements / children data dict, convert it to a format usable by the engine"""
        converted_action = {}

        term = "requirements"
        if has_parent:
            term = "children"

        if term in editor_action_data:
            for requirement in editor_action_data[term]:
                if requirement["type"] != "container":

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

    def ConvertDialogueFileToEditorFormat(self, action_data, settings):
        """
        Given a full dict of dialogue file data in engine format (branches and all), convert it to the editor format by
        rebuilding the structure based on lookups in the ActionDatabase
        """
        #@TODO: Investigate how to speed this up. The volume of O(n) searching is worrying
        converted_dict = {}

        for branch in action_data.items():
            branch_name = branch[0]

            action_list = []
            for action in branch[1]:
                action_name = action["action"]

                # Using the name of the action, look it up in the ActionDatabase. From there, we can build the new
                # structure
                database_entry = None
                for cat_name, cat_data in settings.action_database.items():
                    for option in cat_data["options"]:
                        if action_name == option['action_name']:
                            database_entry = copy.deepcopy(option)
                            break

                    if database_entry:
                        break
                # Pass the entry by ref, and let the convert func edit it directly
                self.ConvertActionRequirementsToEditorFormat(database_entry, action)
                action_list.append(database_entry)

            converted_dict[branch_name] = action_list

        return converted_dict

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
                if requirement["type"] != "container":

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
