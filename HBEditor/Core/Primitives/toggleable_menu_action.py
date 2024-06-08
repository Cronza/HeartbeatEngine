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
from PyQt6 import QtWidgets, QtGui


class ToggleableAction(QtWidgets.QToolButton):
    def __init__(self, text: str, not_toggled_icon: QtGui.QIcon, toggled_icon: QtGui.QIcon = None):
        super().__init__()

        self.not_toggled_icon = not_toggled_icon
        self.toggled_icon = toggled_icon
        if not self.toggled_icon:
            self.toggled_icon = self.not_toggled_icon

        self.setText(text)
        self.setIcon(self.not_toggled_icon)

        self.setObjectName("toggleable-action")

    def Toggle(self, toggle: bool):
        if toggle:
            self.setIcon(self.toggled_icon)
            self.setProperty("toggleable-action", "toggled")  # Apply the match css rule in the active .qss file
            self.setStyle(self.style())

        else:
            self.setIcon(self.not_toggled_icon)
            self.setProperty("toggleable-action", "")  # Clear the property, reverting the CSS back to normal
            self.setStyle(self.style())
