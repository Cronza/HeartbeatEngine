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
from HBEditor.Interface.BaseClasses.base_editor import EditorBaseUI
from HBEditor.Interface.DetailsPanel.details_panel import DetailsPanel
from HBEditor.Interface.Menus.ActionMenu.action_menu import ActionMenu
from HBEditor.Interface.EditorPointAndClick.scene_viewer import SceneViewer
from HBEditor.Interface.Primitives.input_entry_text import InputEntryText
from HBEditor.Interface.Primitives.input_entry_paragraph import InputEntryParagraph
from HBEditor.Interface.Primitives.input_entry_bool import InputEntryBool
from HBEditor.Interface.Primitives.input_entry_color import InputEntryColor
from HBEditor.Interface.Primitives.input_entry_vector2 import InputEntryTuple
from HBEditor.Interface.Primitives.input_entry_int import InputEntryInt
from HBEditor.Interface.Primitives.input_entry_file_selector import InputEntryFileSelector
from HBEditor.Interface.Primitives.input_entry_dropdown import InputEntryDropdown
from HBEditor.Interface.EditorProjectSettings.input_entry_resolution import InputEntryResolution
from HBEditor.Utilities.DataTypes.parameter_types import ParameterType


class EditorPointAndClickUI(EditorBaseUI):
    def __init__(self, core_ref):
        super().__init__(core_ref)

        # Build the core editor layout object
        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Build the core editor layout object
        self.central_grid_layout = QtWidgets.QGridLayout(self)
        self.central_grid_layout.setContentsMargins(0, 0, 0, 0)
        self.central_grid_layout.setSpacing(0)

        self.CreateSceneViewer()
        self.CreateDetailsPanel()

        # Allow the user to resize each column
        self.main_resize_container = QtWidgets.QSplitter(self)

        # Assign everything to the main widget
        self.main_layout.addWidget(self.main_resize_container)
        self.main_resize_container.addWidget(self.scene_viewer)
        self.main_resize_container.addWidget(self.details)

        # Adjust the space allocation to favor the settings section
        self.main_resize_container.setStretchFactor(1, 0)
        self.main_resize_container.setStretchFactor(0, 1)

    def CreateDetailsPanel(self):
        """
        Create the details panel using the generic details object. Since this panel is generic,
        it functions independently of whether it has a reference to the editor core
        """
        self.details = DetailsPanel(self.core.settings, self.core.logger)

    def CreateSceneViewer(self):
        """ Create the scene viewer """
        self.scene_viewer = SceneViewer(self.core.settings, self.core)
