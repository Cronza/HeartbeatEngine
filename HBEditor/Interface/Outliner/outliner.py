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
from HBEditor.Interface.Outliner.file_system_tree import FileSystemTree


class OutlinerUI(QtWidgets.QWidget):
    def __init__(self, core, settings):
        super().__init__()

        self.core = core
        self.settings = settings

        # Main Layout
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(4, 2, 4, 2)
        self.main_layout.setSpacing(0)

        # Directory view
        self.fs_tree = FileSystemTree(
            self,
            self.settings,
            self.core.hb_core.OpenFile,
            self.core.CreateFile,
            self.core.CreateFolder,
            self.core.DeleteFile,
            self.core.DeleteFolder
        )

        # Add everything to the main container
        self.main_layout.addWidget(self.fs_tree)
