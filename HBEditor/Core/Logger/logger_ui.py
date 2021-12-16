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
from PyQt5 import QtWidgets, QtGui, QtCore
from HBEditor.Core.settings import Settings


class LoggerUI(QtWidgets.QWidget):

    def __init__(self, l_core):
        super().__init__()

        self.l_core = l_core

        self.setObjectName("logger")

        # Main Layout
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Toolbar
        self.logger_toolbar = QtWidgets.QToolBar(self)
        self.logger_toolbar.setObjectName("logger")

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
        self.log_list.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.log_list.setEditTriggers(QtWidgets.QAbstractItemView.SelectedClicked)
        self.log_list.setAutoScroll(True)

        # Add everything to the main container
        self.main_layout.addWidget(self.logger_toolbar)
        self.main_layout.addWidget(self.log_list)

    def AddEntry(self, text, style):
        new_entry = QtWidgets.QListWidgetItem()
        entry_text = QtWidgets.QLabel(text)  # Use a QLabel so we can apply css styling per-entry
        entry_text.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        entry_text.setProperty("model-entry", style)  # Apply the match css rule in the active .qss file

        self.log_list.addItem(new_entry)
        self.log_list.setItemWidget(new_entry, entry_text)

        # Since Qt only refreshes widgets when it regains control of the main thread, force the update here
        # as long updates are high priority in terms of visibility
        self.log_list.repaint()
        self.repaint()
