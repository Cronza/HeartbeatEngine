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
from PyQt5 import QtWidgets, QtGui
from HBEditor.Core.settings import Settings


class LoggerUI(QtWidgets.QWidget):
    def __init__(self, l_core):
        super().__init__()

        self.l_core = l_core

        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)

        # Main Layout
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.main_layout.setSpacing(0)

        # Toolbar
        self.logger_toolbar = QtWidgets.QToolBar(self)

        # Generic Button Settings
        icon = QtGui.QIcon()

        # Clear Log Button
        self.logger_toolbar.addAction(
            QtGui.QIcon(
                QtGui.QPixmap(
                    Settings.getInstance().ConvertPartialToAbsolutePath("Content/Icons/Trash.png"),
                )
            ),
            "Clear Log",
            self.l_core.ClearLog
        )

        # Logger data list
        self.log_list = QtWidgets.QListWidget(self)
        self.log_list.setAutoScroll(True)

        # Add everything to the main container
        self.main_layout.addWidget(self.logger_toolbar)
        self.main_layout.addWidget(self.log_list)
