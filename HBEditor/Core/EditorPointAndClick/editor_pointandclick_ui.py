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
from HBEditor.Core.EditorCommon.SceneViewer.scene_viewer import SceneViewer
from HBEditor.Core.EditorCommon.scene_settings import SceneSettings


class EditorPointAndClickUI(EditorBaseUI):
    def __init__(self, core_ref):
        super().__init__(core_ref)

        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.central_grid_layout = QtWidgets.QGridLayout(self)
        self.central_grid_layout.setContentsMargins(0, 0, 0, 0)
        self.central_grid_layout.setSpacing(0)

        self.scene_viewer = SceneViewer(self.core, self.core.UpdateActiveSceneItem)
        self.details = DetailsPanel(self.core.excluded_properties)
        self.scene_settings = SceneSettings()
        self.scene_settings.Populate()

        # Allow the user to resize each column
        self.main_resize_container = QtWidgets.QSplitter(self)

        # Add a sub tab widget for details, settings, etc
        self.sub_tab_widget = QtWidgets.QTabWidget(self)
        self.sub_tab_widget.setElideMode(0)
        self.sub_tab_widget.addTab(self.details, "Details")
        self.sub_tab_widget.addTab(self.scene_settings, "Scene Settings")

        # Assign everything to the main widget
        self.main_layout.addWidget(self.main_resize_container)
        self.main_resize_container.addWidget(self.scene_viewer)
        self.main_resize_container.addWidget(self.sub_tab_widget)

        # Adjust the space allocation to favor the settings section
        self.main_resize_container.setStretchFactor(1, 0)
        self.main_resize_container.setStretchFactor(0, 1)
