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
import copy
from Editor.Interface.EditorDialogue.editor_dialogue import EditorDialogueUI
from Editor.Interface.EditorDialogue.dialogue_entry import DialogueEntry
from PyQt5 import QtWidgets

class EditorDialogue():
    def __init__(self, settings, logger):
        self.settings = settings
        self.logger = logger

        self.logger.Log("Initializing Dialogue Editor...")

        # Build the Dialogue Editor UI
        self.ed_ui = EditorDialogueUI(self)

    def MakeActiveEntry(self, entry):
        """ Makes the given entry the active one, refreshing the details panel"""
        print("Changing active entry")

        self.ed_ui.dialogue_sequence.selectRow(entry.row())

    def AddEntry(self, action_data: dict):
        """ Given a block of action data from the action database, create a new entry in the dialogue sequence """
        print("Adding new dialogue entry")
        print(action_data)
        # Create a new row
        self.ed_ui.dialogue_sequence.insertRow(self.ed_ui.dialogue_sequence.rowCount())

        # Create a new dialogue entry object, and add it to the sequence widget
        new_entry = DialogueEntry(action_data, self.settings, self.MakeActiveEntry)
        self.ed_ui.dialogue_sequence.setItem(self.ed_ui.dialogue_sequence.rowCount() - 1, 0, new_entry)

        # Make this entry the active one, updating the U.I to shows it's information
        self.MakeActiveEntry(new_entry)

        self.logger.Log(f"Adding new dialogue sequence entry")

    # ****** TOOLBAR BUTTON FUNCTIONS ******

    def RemoveEntry(self):
        """ If an entry is selected, delete it from the table """
        selected_entry = self.ed_ui.dialogue_sequence.selectedIndexes()
        if selected_entry:
            self.ed_ui.dialogue_sequence.removeRow(selected_entry[0].row())

    def CopyEntry(self):
        """ If an entry is selected, clone it and add it to the sequence """
        selected_entry = self.ed_ui.dialogue_sequence.selectedItems()
        if selected_entry:
            self.AddEntry(selected_entry[0].action_data)

    def MoveEntryUp(self):
        """ If an entry is selected, move it up one row """
        selected_entry = self.ed_ui.dialogue_sequence.selectedItems()
        if selected_entry:
            selected_entry = selected_entry[0]

            # Only allow moving up if we're not already at the top of the sequence
            initial_row_num = selected_entry.row()
            if initial_row_num is 0:
                self.logger.Log("Warning: Can't move entry up as we're at the top of the sequence")
            else:
                # Remove the entry without deleting it
                taken_entry = self.ed_ui.dialogue_sequence.takeItem(initial_row_num, 0)

                # Delete the origin row
                self.ed_ui.dialogue_sequence.removeRow(initial_row_num)

                # Add the entry two row above its initial row
                new_row_num = initial_row_num - 1
                self.ed_ui.dialogue_sequence.insertRow(new_row_num)
                self.ed_ui.dialogue_sequence.setItem(new_row_num, 0, taken_entry)

                # Select the newly moved row
                self.MakeActiveEntry(taken_entry)

    def MoveEntryDown(self):
        """ If an entry is selected, move it down one row """
        selected_entry = self.ed_ui.dialogue_sequence.selectedItems()
        if selected_entry:
            selected_entry = selected_entry[0]

            # Only allow moving down if we're not already at the bottom of the sequence
            initial_row_num = selected_entry.row()
            print(self.ed_ui.dialogue_sequence.rowCount())
            if initial_row_num + 1 >= self.ed_ui.dialogue_sequence.rowCount():
                self.logger.Log("Warning: Can't move entry down as we're at the bottom of the sequence")
            else:
                # Remove the entry without deleting it
                taken_entry = self.ed_ui.dialogue_sequence.takeItem(initial_row_num, 0)

                # Delete the origin row
                self.ed_ui.dialogue_sequence.removeRow(initial_row_num)

                # Add the entry two row below its initial row
                new_row_num = initial_row_num + 1
                self.ed_ui.dialogue_sequence.insertRow(new_row_num)
                self.ed_ui.dialogue_sequence.setItem(new_row_num, 0, taken_entry)

                # Select the newly moved row
                self.MakeActiveEntry(taken_entry)







