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
from HBEditor.Core.settings import Settings
from HBEditor.Core.BaseClasses.base_editor import EditorBase
from HBEditor.Core.DataTypes.file_types import FileType
from HBEditor.Core.EditorPointAndClick.editor_pointandclick_ui import EditorPointAndClickUI


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
