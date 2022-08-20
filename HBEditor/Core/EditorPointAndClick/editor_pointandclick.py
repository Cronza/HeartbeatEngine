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
from HBEditor.Core.Logger.logger import Logger
from HBEditor.Core import settings
from HBEditor.Core.BaseClasses.base_editor import EditorBase
from HBEditor.Core.DataTypes.file_types import FileType
from HBEditor.Core.EditorUtilities import action_data_handler as adh
from HBEditor.Core.EditorPointAndClick.editor_pointandclick_ui import EditorPointAndClickUI
from Tools.HBYaml.hb_yaml import Reader, Writer


class EditorPointAndClick(EditorBase):
    def __init__(self, file_path):
        super().__init__(file_path)

        self.file_type = FileType.Scene_Point_And_Click

        # Like the actions themselves, there are some properties that are explicitly not used by this editor
        self.excluded_properties = ["transition", "post_wait"]

        self.editor_ui = EditorPointAndClickUI(self)
        Logger.getInstance().Log("Editor initialized")

    def UpdateActiveSceneItem(self):
        """
        Makes the selected scene item the active one, refreshing the details panel. Hides the details information
        if more than one item is selected
        """
        # NOTE: This occurs twice when switching selections, first by deselecting the active entry,
        # and then selecting the second while there is no selection
        #@TODO: Investigate double details refresh when switching scene item selections
        selected_items = self.editor_ui.scene_viewer.GetSelectedItems()

        if selected_items:
            # Only allow editing of details when a single item is selected
            if len(selected_items) == 1:
                self.UpdateDetails(selected_items[0])
                return

        self.UpdateDetails(None)

    def UpdateDetails(self, selected_item):
        """
        Refreshes the details panel with the details from the selected item. Clears all details if None is provided
        """
        if selected_item:
            self.editor_ui.details.Populate(selected_item)

        # No entries left to select. Wipe remaining details
        else:
            self.editor_ui.details.Clear()

    def Export(self):
        super().Export()
        Logger.getInstance().Log(f"Exporting Dialogue data for: {self.file_path}")

        # Get an engine-formatted list of scene items
        conv_scene_items = self.ConvertSceneItemsToEngineFormat(self.editor_ui.scene_viewer.GetSceneItems())

        data_to_export = {
            "type": FileType.Scene_Point_And_Click.name,
            "scene_items": conv_scene_items
        }
        Logger.getInstance().Log("Writing data to file...")
        try:
            Writer.WriteFile(
                data=data_to_export,
                file_path=self.file_path,
                metadata=f"# Type: {FileType.Scene_Point_And_Click.name}\n" +
                f"# {settings.editor_data['EditorSettings']['version_string']}"
            )
            Logger.getInstance().Log("File Exported!", 2)
        except Exception as exc:
            Logger.getInstance().Log(f"Failed to Export: {exc}", 4)

    def Import(self):
        super().Import()
        Logger.getInstance().Log(f"Importing Point & Click data for: {self.file_path}")

        file_data = Reader.ReadAll(self.file_path)

        # Skip importing if the file has no data to load
        if file_data:
            conv_scene_items = self.ConvertSceneItemsToEditorFormat(file_data["scene_items"])
            for item in conv_scene_items:
                self.editor_ui.scene_viewer.AddRenderable(item)

    def ConvertSceneItemsToEngineFormat(self, scene_items: list):
        """ Build and return a list of the data from all active scene items converted to engine format """
        converted_entries = []
        for scene_item in scene_items:
            scene_item_data = scene_item.action_data

            # Get the action name
            converted_action = {"action": scene_item_data["action_name"]}

            # Collect a converted dict of all requirements for this action (If any are present)
            converted_requirements = adh.ConvertActionRequirementsToEngineFormat(
                editor_req_data=scene_item_data,
                excluded_properties=self.excluded_properties
            )
            if converted_requirements:
                converted_action.update(converted_requirements)

            # Add the newly converted action
            converted_entries.append(converted_action)

        return converted_entries

    def ConvertSceneItemsToEditorFormat(self, action_data):
        """
            Given a full dict of scene item data in engine format, convert it to the editor format by
            rebuilding the structure based on lookups in the ActionDatabase
        """
        conv_items = []
        for item in action_data:
            action_name = item["action"]

            # Using the name of the action, look it up in the ActionDatabase. If found, clone it
            database_entry = None
            for cat_name, cat_data in settings.action_database.items():
                for option in cat_data["options"]:
                    if action_name == option['action_name']:
                        database_entry = copy.deepcopy(option)
                        break
                if database_entry:
                    break

            # Pass the entry by ref, and let the convert func edit it directly
            adh.ConvertActionRequirementsToEditorFormat(
                editor_req=database_entry,
                engine_req=item,
                excluded_properties=self.excluded_properties
            )
            conv_items.append(database_entry)

        return conv_items
