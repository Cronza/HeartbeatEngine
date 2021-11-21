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
from HBEditor.Core.BaseClasses.base_editor import EditorBase
from HBEditor.Utilities.DataTypes.file_types import FileType
from HBEditor.Interface.EditorPointAndClick.editor_pointandclick import EditorPointAndClickUI


class EditorPointAndClick(EditorBase):
    def __init__(self, settings, logger, file_path):
        super().__init__(settings, logger, file_path)

        self.file_type = FileType.Scene_Point_And_Click

        # Since the Point & Click editor doesn't make use of all actions, but only those that can be rendered
        # (interactables, sprites, text, etc), we need to compile a custom action_data dict with only the options
        # we'll allow
        possible_actions = {
            "Renderables": ["Create Sprite", "Create Text", "Create Background"],
        }
        self.action_data = self.BuildActionDataDict(possible_actions)

        # Initialize the editor U.I
        self.editor_ui = EditorPointAndClickUI(self)
        self.logger.Log("Editor initialized")

    def BuildActionDataDict(self, possible_actions: dict) -> dict:
        """
        Compiles a dict clone of the ActionDatabase, limited to a specific subset of categories and actions defined
        in 'possible_actions'
        """
        # Build our action data dict
        compiled_dict = {}
        for category_name, action_list in possible_actions.items():
            # Clone the entire category structure so we don't try and piecemeal it, potentially creating issues
            # in the future if we change the structure
            category_data = copy.deepcopy(self.settings.action_database[category_name])

            # Wipe the available options, as we're going to rebuild the list with only those we can use
            category_data["options"] = []

            # For every action we want, find the matching entry in the database and clone it

            for action_name in action_list:
                for db_action in self.settings.action_database[category_name]["options"]:
                    if action_name == db_action["display_name"]:
                        category_data["options"].append(copy.deepcopy(db_action))
                        break

            # Add the completed clone to the main dict
            compiled_dict[category_name] = category_data

        return compiled_dict

    def UpdateActiveSceneItem(self):
        """
        Makes the selected scene item the active one, refreshing the details panel. Hides the details information
        if more than one item is selected
        """
        selected_items = self.editor_ui.scene_viewer.GetSelectedItems()

        if selected_items:
            # Only allow editing of details when a single item is selected
            if len(selected_items) == 1:
                self.UpdateDetails(selected_items[0])
                return None

        self.UpdateDetails(None)

    def UpdateDetails(self, selected_item):
        """
        Refreshes the details panel with the details from the selected item. Clears all details if None is provided
        """
        if selected_item:
            self.editor_ui.details.PopulateDetails(selected_item)

        # No entries left to select. Wipe remaining details
        else:
            self.editor_ui.details.Clear()
