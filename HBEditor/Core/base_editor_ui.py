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
from PyQt6 import QtWidgets, QtCore


class EditorBaseUI(QtWidgets.QWidget):
    SIG_USER_UPDATE = QtCore.pyqtSignal()  # Emitted whenever any editor child widget is modified by the user
    SIG_USER_SAVE = QtCore.pyqtSignal()  # Emitted whenever the user saves this editor

    def __init__(self, core_ref):
        super().__init__()

        self.core = core_ref
        self.pending_changes = False

    def AdjustSize(self):
        """
        Adjust the size of child widgets. This is typically only called when the window has changed in a meaningful way
        """
        pass
