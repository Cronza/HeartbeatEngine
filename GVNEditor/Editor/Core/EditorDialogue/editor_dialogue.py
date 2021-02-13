"""
    This file is part of GVNEditor.

    GVNEditor is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    GVNEditor is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with GVNEditor.  If not, see <https://www.gnu.org/licenses/>.
"""

from Editor.Interface.EditorDialogue.editor_dialogue import EditorDialogueUI
from PyQt5 import QtWidgets

class EditorDialogue():
    def __init__(self, e_ui):

        self.e_ui = e_ui
        self.logger = self.e_ui.logger
        self.logger.Log("Initializing Dialogue Editor...")

        # Build the Dialogue Editor UI
        self.ed_ui = EditorDialogueUI(self)

    def AddAction(self):
        print("TESTING")
        test = QtWidgets.QListWidgetItem()
        test.setText("This is a test")
        self.ed_ui.dialogue_sequence.addItem(test)
