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
from HBEditor.Core.EditorInterface.editor_interface_ui import EditorInterfaceUI
from HBEditor.Core.EditorCommon.SceneViewer.scene_items import RootItem
from HBEditor.Core.EditorCommon.GroupsPanel.groups_panel import GroupEntry
from Tools.HBYaml.hb_yaml import Reader, Writer


class EditorInterface(EditorBase):
    def __init__(self, file_path, interface_type: FileType = FileType.Interface):
        super().__init__(file_path)

        # Where as many scenes have unique editors, interface types share the same editor. As such, we need
        # to know which type this editor is working on to properly adjust functionality
        self.file_type = interface_type

        self.editor_ui = EditorInterfaceUI(self)
        self.editor_ui.pages_panel.CreateEntry(
            "Persistent",
            "This is the default, main view",
            True
        )
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

    def RegisterItemToPage(self, item: RootItem, page: GroupEntry = None):
        """
        Sets the owner ID of the provided item to the active page ID. If 'page' is provided, make it the owner instead
        """
        if not page:
            page = self.editor_ui.pages_panel.active_entry
        item.owner_id = page.Get()[0]

    def ShowPageItems(self, make_visible: bool, page_name: str):
        """
        Sets the 'Visible' state for all items owned by the provided page based on the given bool
        """
        for item in self.editor_ui.scene_viewer.GetSceneItems():
            if item.owner_id == page_name:
                item.setVisible(make_visible)

    def EnablePageItems(self, cur_page: GroupEntry, new_page: GroupEntry):
        """
        Sets the 'Enabled' state for all items owned by 'new_page', and the 'Disabled' state for all items owned by the
        'cur_page'. This disables interactivity
        """
        if not cur_page:
            # No previously selected page. Only set state for the new page
            new_group_name = new_page.Get()[0]
            for item in self.editor_ui.scene_viewer.GetSceneItems():
                if item.owner_id == new_group_name:
                    item.setEnabled(True)
        elif cur_page == new_page:
            pass
        else:
            # Prior page available. Disable its items, and enable the new page's items
            cur_group_name = cur_page.Get()[0]
            new_group_name = new_page.Get()[0]
            for item in self.editor_ui.scene_viewer.GetSceneItems():
                if item.owner_id == cur_group_name:
                    item.setEnabled(False)
                elif item.owner_id == new_group_name:
                    item.setEnabled(True)

    def Export(self):
        super().Export()
        Logger.getInstance().Log(f"Exporting Interface data for: {self.file_path}")

        # Store any active changes in the details panel
        self.editor_ui.details.StoreData()

        # Collect the scene settings
        conv_scene_data = ad.ConvertParamDataToEngineFormat(self.editor_ui.interface_settings.GetData())

        # Merge the collected data
        data_to_export = {
            "type": self.file_type.name,
            "settings": conv_scene_data,
            "pages": self.ConvertInterfaceItemsToEngineFormat(self.editor_ui.scene_viewer.GetSceneItems())
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
        Logger.getInstance().Log(f"Importing Interface data for: {self.file_path}")

        file_data = Reader.ReadAll(self.file_path)

        # Skip importing if the file has no data to load
        if file_data:
            # Populate the interface settings
            self.editor_ui.interface_settings.Populate(file_data["settings"])

            for page_name, page_data in file_data["pages"].items():
                # Create the page entry (The persistent page is created on editor init, so skip that)
                if page_name.lower() != "persistent":
                    self.editor_ui.pages_panel.CreateEntry(page_name, page_data["description"])

                # Populate the page entry
                conv_page_items = self.ConvertInterfaceItemsToEditorFormat(page_data["items"])
                for item in conv_page_items:
                    action_name, action_data = next(iter(item.items()))
                    new_item = self.editor_ui.scene_viewer.AddRenderable(action_name, action_data, True)

                    # Apply any imported editor-specific properties
                    if "editor_properties" in item[ad.GetActionName(item)]:
                        editor_properties = item[ad.GetActionName(item)]["editor_properties"]
                        if "locked" in editor_properties:
                            new_item.SetLocked(editor_properties["locked"])

                    # Hide non-persistent page items by default, as pages themselves are inactive by default
                    if page_name.lower() != "persistent":
                        new_item.setVisible(False)

        # Select the persistent layer
        self.editor_ui.pages_panel.ChangeEntry(0)

    def ConvertInterfaceItemsToEngineFormat(self, scene_items: dict) -> dict:
        """ Build and return a dict of data from all active view items converted to engine format, organized by page """
        conv_pages = {}

        # Prepare each page grouping
        for index in range(0, self.editor_ui.pages_panel.GetCount()):
            page = self.editor_ui.pages_panel.GetEntryItemWidget(index)
            page_name, page_desc = page.Get()
            conv_pages[page_name] = {"description": page_desc, "items": []}

        for scene_item in scene_items:
            conv_ad = ad.ConvertParamDataToEngineFormat(scene_item.action_data)

            # Preserve any notable editor-specific parameters so that they're available when importing
            # Note: This is subject to change when additional examples are available
            if scene_item.GetLocked():
                conv_ad["editor_properties"] = {"locked": scene_item.GetLocked()}

            # Add the newly converted action to the associated page
            conv_pages[scene_item.owner_id]["items"].append({scene_item.action_name: conv_ad})

        return conv_pages

    def ConvertInterfaceItemsToEditorFormat(self, action_data):
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
                action_data=action_data
            )

            # Import the editor-specific properties in order to preserve editing state for items
            if "editor_properties" in item:
                base_ad_clone["editor_properties"] = item["editor_properties"]

            conv_items.append({action_name: base_ad_clone})

        return conv_items
