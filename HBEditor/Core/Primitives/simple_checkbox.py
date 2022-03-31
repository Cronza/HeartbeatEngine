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
from PyQt5 import QtWidgets, QtCore


class SimpleCheckbox(QtWidgets.QWidget):
    """
    A custom wrapper for the QCheckbox class when provides a textless, centered checkbox
    """
    SIG_USER_UPDATE = QtCore.pyqtSignal(object, bool)

    def __init__(self):
        super().__init__()
        self.owner = None

        # For some unholy reason, the QCheckbox widget does not support center alignment natively. To make matters
        # worse, the text is considered in the size when used in layouts regardless if text is actually specified

        # This can be bypassed by surrounding the QCheckbox in spacers that force it to the center of the layout
        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.left_spacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding)
        self.right_spacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding)

        self.checkbox = QtWidgets.QCheckBox(self)
        self.checkbox.setText("")

        self.main_layout.addItem(self.left_spacer)
        self.main_layout.addWidget(self.checkbox)
        self.main_layout.addItem(self.right_spacer)

    def Get(self) -> bool:
        """ Returns whether the checkbox is checked """
        return self.checkbox.isChecked()

    def Set(self, value) -> None:
        self.checkbox.setChecked(value)

    def Connect(self):
        self.checkbox.stateChanged.connect(lambda update: self.SIG_USER_UPDATE.emit(self.owner, self.Get()))

    def Disconnect(self):
        self.checkbox.disconnect()
