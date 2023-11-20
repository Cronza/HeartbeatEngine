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
from PyQt5 import QtWidgets, QtCore, QtGui
from HBEditor.Core.base_editor_ui import EditorBaseUI
from HBEditor.Core.EditorCommon.DetailsPanel.details_panel import DetailsPanel
from HBEditor.Core.EditorCommon.SceneViewer.scene_viewer import SceneViewer
from HBEditor.Core.EditorCommon.scene_settings import SceneSettings
from HBEditor.Core.EditorCommon.GroupsPanel.groups_panel import GroupsPanel
from HBEditor.Core.Primitives import input_entry_handler as ieh
from HBEditor.Core.DataTypes.file_types import FileType


class EditorInterfaceUI(EditorBaseUI):
    def __init__(self, core_ref):
        super().__init__(core_ref)

        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.central_grid_layout = QtWidgets.QGridLayout(self)
        self.central_grid_layout.setContentsMargins(0, 0, 0, 0)
        self.central_grid_layout.setSpacing(0)

        self.pages_panel = GroupsPanel(title="Pages", enable_togglable_entries=True)
        self.pages_panel.SIG_USER_UPDATE.connect(self.SIG_USER_UPDATE.emit)
        self.pages_panel.SIG_USER_GROUP_CHANGE.connect(self.core.EnablePageItems)
        self.pages_panel.SIG_USER_GROUP_TOGGLE.connect(self.core.ShowPageItems)

        self.scene_viewer = SceneViewer(self.core.file_type)
        self.scene_viewer.SIG_USER_ADDED_ITEM.connect(self.core.RegisterItemToPage)
        self.scene_viewer.SIG_USER_DELETED_ITEMS.connect(self.SIG_USER_UPDATE.emit)
        self.scene_viewer.SIG_USER_MOVED_ITEMS.connect(self.OnItemMove)
        self.scene_viewer.SIG_SELECTION_CHANGED.connect(self.core.UpdateActiveSceneItem)

        self.details = DetailsPanel()
        self.details.SIG_USER_UPDATE.connect(self.SIG_USER_UPDATE.emit)
        self.interface_settings = InterfaceSettings()
        self.interface_settings.Populate()

        # Allow the user to resize each column
        self.main_resize_container = QtWidgets.QSplitter(self)

        # Add a sub tab widget for details, settings, etc
        self.sub_tab_widget = QtWidgets.QTabWidget(self)
        self.sub_tab_widget.setElideMode(0)
        self.sub_tab_widget.addTab(self.details, "Details")
        self.sub_tab_widget.addTab(self.interface_settings, "Settings")

        # Assign everything to the main widget
        self.main_layout.addWidget(self.main_resize_container)
        self.main_resize_container.addWidget(self.pages_panel)
        self.main_resize_container.addWidget(self.scene_viewer)
        self.main_resize_container.addWidget(self.sub_tab_widget)

        # Adjust the main view so it's consuming as much space as possible
        self.main_resize_container.setStretchFactor(1, 10)

    def OnItemMove(self, selected_items: list = None):
        self.SIG_USER_UPDATE.emit()
        self.core.UpdateActiveSceneItem(selected_items)


class InterfaceSettings(SceneSettings):
    def __init__(self):
        super().__init__()

    def Populate(self, data: dict = None):
        self.settings_tree.clear()

        entries = {
            "key": {
                "type": "String",
                "default": "!&INTERFACE&!",
                "value": "!&INTERFACE&!",
                "flags": ["editable"]
            },

            "description": {
                "type": "Paragraph",
                "default": "",
                "value": "",
                "flags": ["editable"]
            }
        }

        if data:
            if "key" in data:
                entries["key"]["value"] = data["key"]
            if "description" in data:
                entries["description"]["value"] = data["description"]

        for name, data in entries.items():
            ieh.Add(
                owner=self,
                view=self.settings_tree,
                name=name,
                data=data,
                parent=None
            )
