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
from HBEditor.Core.base_editor import EditorBase
from HBEditor.Core.DataTypes.file_types import FileType
from HBEditor.Core.EditorUtilities import action_data as ad
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

    def UpdateActiveSceneItem(self, selected_items):
        """
        Makes the selected scene item the active one, refreshing the details panel. Hides the details information
        if more than one item is selected
        """

        # Only allow editing of details when a single item is selected
        if selected_items:
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

        else:
            # No entries left to select. Wipe remaining details
            self.editor_ui.details.ClearActiveItem()

    def Export(self):
        super().Export()
        Logger.getInstance().Log(f"Exporting Point & Click data for: {self.file_path}")

        # Store any active changes in the details panel
        self.editor_ui.details.StoreData()

        # Collect the scene settings
        conv_scene_data = ad.ConvertParamDataToEngineFormat(self.editor_ui.scene_settings.GetData())

        # Merge the collected data
        data_to_export = {
            "type": FileType.Scene_Point_And_Click.name,
            "settings": conv_scene_data,
            "scene_items": self.ConvertSceneItemsToEngineFormat(self.editor_ui.scene_viewer.GetSceneItems())
        }

        Logger.getInstance().Log("Writing data to file...")
        try:
            Writer.WriteFile(
                data=data_to_export,
                file_path=self.file_path,
                metadata=f"# Type: {self.file_type.name}\n" +
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

            # Populate the scene settings
            self.editor_ui.scene_settings.Populate(file_data["settings"])

            for item in conv_scene_items:
                action_name, action_data = next(iter(item.items()))
                new_item = self.editor_ui.scene_viewer.AddRenderable(action_name, action_data, True)

                # Apply any imported editor-specific properties
                if "editor_properties" in action_data:
                    editor_properties = action_data["editor_properties"]
                    if "locked" in editor_properties:
                        new_item.SetLocked(editor_properties["locked"])

    def ConvertSceneItemsToEngineFormat(self, scene_items: list):
        """ Build and return a list of the data from all active scene items converted to engine format """
        conv_entries = []
        for scene_item in scene_items:
            conv_ad = ad.ConvertParamDataToEngineFormat(scene_item.action_data)

            # Preserve any notable editor-specific parameters so that they're available when importing
            # Note: This is subject to change when additional examples are available
            if scene_item.GetLocked():
                conv_ad["editor_properties"] = {"locked": scene_item.GetLocked()}

            conv_entries.append({scene_item.action_name: conv_ad})

        return conv_entries

    def ConvertSceneItemsToEditorFormat(self, action_data):
        """
        Given a full dict of scene item data in engine format, convert it to the editor format by
        rebuilding the structure based on lookups in the actions_metadata
        """
        conv_items = []
        for item in action_data:
            # Entries are dicts with only one top level key, which is the name of the action. Use it to look up
            # the matching ACTION_DATA and clone it
            action_name, action_data = next(iter(item.items()))
            base_ad_clone = copy.deepcopy(settings.GetActionData(action_name))

            # Pass the entry by ref, and let the convert func edit it directly
            ad.ConvertActionDataToEditorFormat(
                base_action_data=base_ad_clone,
                action_data=action_data,
                excluded_properties=self.excluded_properties
            )

            # Import the editor-specific properties in order to preserve editing state for items
            if "editor_properties" in item:
                base_ad_clone["editor_properties"] = item["editor_properties"]

            conv_items.append({action_name: base_ad_clone})

        return conv_items
