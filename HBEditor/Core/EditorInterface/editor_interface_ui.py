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
from PyQt6 import QtWidgets, QtCore
from HBEditor.Core.base_editor_ui import EditorBaseUI
from HBEditor.Core.EditorCommon.DetailsPanel.details_panel import DetailsPanel
from HBEditor.Core.EditorCommon.SceneViewer.scene_viewer import SceneViewer
from HBEditor.Core.EditorCommon.GroupsPanel.groups_panel import GroupsPanel
from HBEditor.Core.DataTypes.file_types import FileType
from HBEditor.Core.EditorCommon.DetailsPanel.base_source_entry import SourceEntry


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

        self.scene_viewer = SceneViewer(FileType.Interface)
        self.scene_viewer.SIG_USER_ADDED_ITEM.connect(self.core.RegisterItemToPage)
        self.scene_viewer.SIG_USER_DELETED_ITEMS.connect(self.SIG_USER_UPDATE.emit)
        self.scene_viewer.SIG_USER_MOVED_ITEMS.connect(self.OnItemMove)
        self.scene_viewer.SIG_SELECTION_CHANGED.connect(self.core.UpdateActiveSceneItem)

        self.details = DetailsPanel()
        self.details.SIG_USER_UPDATE.connect(self.SIG_USER_UPDATE.emit)

        self.interface_settings = DetailsPanel(use_connections=False)
        self.interface_settings_src_obj = InterfaceSettings()
        self.interface_settings.SIG_USER_UPDATE.connect(self.SIG_USER_UPDATE.emit)
        self.interface_settings.Populate(self.interface_settings_src_obj)

        # Allow the user to resize each column
        self.main_resize_container = QtWidgets.QSplitter(self)

        # Add a sub tab widget for details, settings, etc
        self.sub_tab_widget = QtWidgets.QTabWidget(self)
        self.sub_tab_widget.setElideMode(QtCore.Qt.TextElideMode.ElideLeft)
        self.sub_tab_widget.addTab(self.details, "Details")
        self.sub_tab_widget.addTab(self.interface_settings, "Settings")

        # Assign everything to the main widget
        self.main_layout.addWidget(self.main_resize_container)
        self.main_resize_container.addWidget(self.pages_panel)
        self.main_resize_container.addWidget(self.scene_viewer)
        self.main_resize_container.addWidget(self.sub_tab_widget)

        # Adjust the main view so it's consuming as much space as possible
        self.main_resize_container.setStretchFactor(0, 6)
        self.main_resize_container.setStretchFactor(1, 8)
        self.main_resize_container.setStretchFactor(2, 8)  # Increase details panel size to accomodate connection column

    def OnItemMove(self, selected_items: list = None):
        self.SIG_USER_UPDATE.emit()
        self.core.UpdateActiveSceneItem(selected_items)

    def FreezeSignals(self):
        """ Block signals for all connected child widgets """
        self.pages_panel.blockSignals(True)
        self.scene_viewer.blockSignals(True)
        self.details.blockSignals(True)

    def UnfreezeSignals(self):
        """ Unblock signals for all connected child widgets """
        self.pages_panel.blockSignals(False)
        self.scene_viewer.blockSignals(False)
        self.details.blockSignals(False)

class InterfaceSettings(QtCore.QObject, SourceEntry):
    SIG_USER_UPDATE = QtCore.pyqtSignal()
    ACTION_DATA = {
        "key": {
            "type": "String",
            "value": "!&INTERFACE&!",
            "flags": ["editable"]
        },
        "description": {
            "type": "Paragraph",
            "value": "",
            "flags": ["editable"]
        }
    }

    def __init__(self):
        super().__init__()
        self.action_data = copy.deepcopy(self.ACTION_DATA)

    def Refresh(self, change_tree: list = None):
        self.SIG_USER_UPDATE.emit()
