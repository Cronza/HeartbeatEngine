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
from HBEditor.Core.EditorDialogue.dialogue_sequence_panel import DialogueSequencePanel
from HBEditor.Core.EditorCommon.GroupsPanel.groups_panel import GroupsPanel
from HBEditor.Core.EditorCommon.DetailsPanel.base_source_entry import SourceEntry


class EditorDialogueUI(EditorBaseUI):
    def __init__(self, core_ref):
        super().__init__(core_ref)

        # Build the core editor layout object
        self.central_grid_layout = QtWidgets.QGridLayout(self)
        self.central_grid_layout.setContentsMargins(0, 0, 0, 0)
        self.central_grid_layout.setSpacing(0)

        self.branches_panel = GroupsPanel(title="Branches")
        self.branches_panel.SIG_USER_UPDATE.connect(self.SIG_USER_UPDATE.emit)
        self.branches_panel.SIG_USER_GROUP_CHANGE.connect(self.core.SwitchBranches)
        self.dialogue_sequence = DialogueSequencePanel(self.core)
        self.dialogue_sequence.SIG_USER_UPDATE.connect(self.SIG_USER_UPDATE.emit)
        self.details = DetailsPanel()
        self.details.SIG_USER_UPDATE.connect(self.SIG_USER_UPDATE.emit)

        self.dialogue_settings = DetailsPanel(use_connections=False)
        self.dialogue_settings_src_obj = DialogueSettings()
        self.dialogue_settings.SIG_USER_UPDATE.connect(self.SIG_USER_UPDATE.emit)
        self.dialogue_settings.Populate(self.dialogue_settings_src_obj)

        # The dialogue editor makes use of the "Choice" input widget, which requires a reference
        # to the branches list
        self.details.branch_list = self.branches_panel.entry_list

        # Allow the user to resize each column
        self.main_resize_container = QtWidgets.QSplitter(self)

        # Add a sub tab widget for details, settings, etc
        self.sub_tab_widget = QtWidgets.QTabWidget(self)
        self.sub_tab_widget.setElideMode(QtCore.Qt.TextElideMode.ElideLeft)
        self.sub_tab_widget.addTab(self.details, "Details")
        self.sub_tab_widget.addTab(self.dialogue_settings, "Dialogue Settings")

        # Add everything to the editor interface
        self.central_grid_layout.addWidget(self.main_resize_container, 0, 0)
        self.main_resize_container.addWidget(self.branches_panel)
        self.main_resize_container.addWidget(self.dialogue_sequence)
        self.main_resize_container.addWidget(self.sub_tab_widget)

    def AdjustSize(self):
        # Adjust the main view so it's consuming as much space as possible
        self.main_resize_container.setSizes([round(self.width() / 5), round((self.width() / 2) + self.width() / 5), round(self.width() / 4)])
        self.details.AdjustSize()


class DialogueSettings(QtCore.QObject, SourceEntry):
    SIG_USER_UPDATE = QtCore.pyqtSignal()
    ACTION_DATA = {
        "interface": {
            "type": "Interface",
            "value": "",
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
