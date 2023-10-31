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
from PyQt5 import QtWidgets
from HBEditor.Core.base_editor_ui import EditorBaseUI
from HBEditor.Core.EditorCommon.DetailsPanel.details_panel import DetailsPanel
from HBEditor.Core.EditorDialogue.dialogue_sequence_panel import DialogueSequencePanel
from HBEditor.Core.EditorCommon.GroupsPanel.groups_panel import GroupsPanel
from HBEditor.Core.EditorCommon.scene_settings import SceneSettings


class EditorDialogueUI(EditorBaseUI):
    def __init__(self, core_ref):
        super().__init__(core_ref)

        # Build the core editor layout object
        self.central_grid_layout = QtWidgets.QGridLayout(self)
        self.central_grid_layout.setContentsMargins(0, 0, 0, 0)
        self.central_grid_layout.setSpacing(0)

        self.branches_panel = GroupsPanel(self.core.SwitchBranches, title="Branches")
        self.dialogue_sequence = DialogueSequencePanel(self.core)
        self.details = DetailsPanel()
        self.scene_settings = SceneSettings()
        self.scene_settings.Populate()

        # The dialogue editor makes use of the "Choice" input widget, which requires a reference
        # to the branches list
        self.details.branch_list = self.branches_panel.entry_list

        # Allow the user to resize each column
        self.main_resize_container = QtWidgets.QSplitter(self)

        # Add a sub tab widget for details, settings, etc
        self.sub_tab_widget = QtWidgets.QTabWidget(self)
        self.sub_tab_widget.setElideMode(0)
        self.sub_tab_widget.addTab(self.details, "Details")
        self.sub_tab_widget.addTab(self.scene_settings, "Scene Settings")

        # Add everything to the editor interface
        self.central_grid_layout.addWidget(self.main_resize_container, 0, 0)
        self.main_resize_container.addWidget(self.branches_panel)
        self.main_resize_container.addWidget(self.dialogue_sequence)
        self.main_resize_container.addWidget(self.sub_tab_widget)

        # Adjust the main view so it's consuming as much space as possible
        self.main_resize_container.setStretchFactor(1, 10)
