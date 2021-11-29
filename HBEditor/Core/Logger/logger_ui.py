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
        self.main_layout.setContentsMargins(4, 2, 4, 2)
        self.main_layout.setSpacing(0)

        # Toolbar
        self.logger_toolbar = QtWidgets.QFrame(self)
        self.logger_toolbar.setAutoFillBackground(False)
        self.logger_toolbar.setStyleSheet(
            "QFrame, QLabel, QToolTip {\n"
            "    border-radius: 4px;\n"
            f"   background-color: rgb({Settings.getInstance().toolbar_background_color});\n"
            "}")
        self.logger_toolbar.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.logger_toolbar.setFrameShadow(QtWidgets.QFrame.Raised)
        self.logger_toolbar_layout = QtWidgets.QHBoxLayout(self.logger_toolbar)
        self.logger_toolbar_layout.setContentsMargins(2, 2, 2, 2)
        self.logger_toolbar_layout.setSpacing(0)

        # Generic Button Settings
        icon = QtGui.QIcon()
        button_style = (
            f"background-color: rgb({Settings.getInstance().toolbar_button_background_color});\n"
        )

        # Clear Log Button
        self.clear_log_button = QtWidgets.QToolButton(self.logger_toolbar)
        self.clear_log_button.setStyleSheet(button_style)
        icon.addPixmap(
            QtGui.QPixmap(Settings.getInstance().ConvertPartialToAbsolutePath("Content/Icons/Trash.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        self.clear_log_button.setIcon(icon)
        self.clear_log_button.clicked.connect(self.l_core.ClearLog)

        # Add buttons to toolbar
        self.logger_toolbar_layout.addWidget(self.clear_log_button)
        toolbar_spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.logger_toolbar_layout.addItem(toolbar_spacer)

        # Logger data list
        self.log_list = QtWidgets.QListWidget(self)
        self.log_list.setFont(Settings.getInstance().paragraph_font)
        self.log_list.setStyleSheet(Settings.getInstance().paragraph_color)
        self.log_list.setAutoScroll(True)

        # Add everything to the main container
        self.main_layout.addWidget(self.logger_toolbar)
        self.main_layout.addWidget(self.log_list)
