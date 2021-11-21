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
import copy
from PyQt5 import QtWidgets, QtGui
from HBEditor.Interface.Menus.ActionMenu.action_menu import ActionMenu
from HBEditor.Interface.EditorDialogue.dialogue_sequence_entry import DialogueEntry

"""
The core U.I class for the dialogue sequence panel. This contains all logic for generating, moving and removing
any and all child widgets pertaining to the panel.

This class is not meant for any destructive data changes, merely U.I actions
"""
class DialogueSequencePanel(QtWidgets.QWidget):
    def __init__(self, settings, ed_core):
        super().__init__()

        self.ed_core = ed_core
        self.settings = settings

        # Create an action menu to be used later on for adding entries to the sequence
        self.action_menu = ActionMenu(self.settings, self.AddEntry, settings.action_database)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Create the View title
        self.title = QtWidgets.QLabel(self)
        self.title.setFont(self.settings.header_1_font)
        self.title.setStyleSheet(self.settings.header_1_color)
        self.title.setText("Dialogue Sequence")

        # Create the toolbar
        self.main_toolbar = QtWidgets.QFrame()
        self.main_toolbar.setStyleSheet(
            "QFrame, QLabel, QToolTip {\n"
            "    border-radius: 4px;\n"
            "    background-color: rgb(44,53,57);\n"
            "}"
        )
        self.main_toolbar.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.main_toolbar.setFrameShadow(QtWidgets.QFrame.Raised)
        self.main_toolbar_layout = QtWidgets.QHBoxLayout(self.main_toolbar)
        self.main_toolbar_layout.setContentsMargins(2, 2, 2, 2)
        self.main_toolbar_layout.setSpacing(0)

        # Generic button settings
        icon = QtGui.QIcon()
        button_style = (
            f"background-color: rgb({self.settings.toolbar_button_background_color});\n"
        )

        # Add Entry Button (Popup Menu)
        self.add_entry_button = QtWidgets.QToolButton(self.main_toolbar)
        self.add_entry_button.setStyleSheet(button_style)
        icon.addPixmap(
            QtGui.QPixmap(self.settings.ConvertPartialToAbsolutePath("Content/Icons/Plus.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        self.add_entry_button.setIcon(icon)
        self.add_entry_button.setMenu(self.action_menu)
        self.add_entry_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.main_toolbar_layout.addWidget(self.add_entry_button)

        # Remove Entry Button
        self.remove_entry_button = QtWidgets.QToolButton(self.main_toolbar)
        self.remove_entry_button.setStyleSheet(button_style)
        icon.addPixmap(
            QtGui.QPixmap(self.settings.ConvertPartialToAbsolutePath("Content/Icons/Minus.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        self.remove_entry_button.setIcon(icon)
        self.remove_entry_button.clicked.connect(self.RemoveEntry)
        self.main_toolbar_layout.addWidget(self.remove_entry_button)

        # Copy Entry Button
        self.copy_entry_button = QtWidgets.QToolButton(self.main_toolbar)
        self.copy_entry_button.setStyleSheet(button_style)
        icon.addPixmap(
            QtGui.QPixmap(self.settings.ConvertPartialToAbsolutePath("Content/Icons/Copy.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        self.copy_entry_button.setIcon(icon)
        self.copy_entry_button.clicked.connect(self.CopyEntry)
        self.main_toolbar_layout.addWidget(self.copy_entry_button)

        # Move Entry Up Button
        self.move_entry_up_button = QtWidgets.QToolButton(self.main_toolbar)
        self.move_entry_up_button.setStyleSheet(button_style)
        icon.addPixmap(
            QtGui.QPixmap(self.settings.ConvertPartialToAbsolutePath("Content/Icons/Up.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        self.move_entry_up_button.setIcon(icon)
        self.move_entry_up_button.clicked.connect(self.MoveEntryUp)
        self.main_toolbar_layout.addWidget(self.move_entry_up_button)

        # Move Entry Down Button
        self.move_entry_down_button = QtWidgets.QToolButton(self.main_toolbar)
        self.move_entry_down_button.setStyleSheet(button_style)
        icon.addPixmap(
            QtGui.QPixmap(self.settings.ConvertPartialToAbsolutePath("Content/Icons/Down.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        self.move_entry_down_button.setIcon(icon)
        self.move_entry_down_button.clicked.connect(self.MoveEntryDown)
        self.main_toolbar_layout.addWidget(self.move_entry_down_button)

        # Empty Space Spacer
        spacer = QtWidgets.QSpacerItem(534, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.main_toolbar_layout.addItem(spacer)

        # Build the Action Sequence
        self.dialogue_table = QtWidgets.QTableWidget(self)
        self.dialogue_table.setColumnCount(1)
        self.dialogue_table.horizontalHeader().hide()
        self.dialogue_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.dialogue_table.verticalHeader().setStyleSheet(self.settings.selection_color)
        self.dialogue_table.setStyleSheet(self.settings.selection_color)
        self.dialogue_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)  # Disable editing
        self.dialogue_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)  # Disable multi-selection
        self.dialogue_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)  # Disables cell selection
        self.dialogue_table.itemSelectionChanged.connect(self.ed_core.UpdateActiveEntry)

        # ********** Add All Major Pieces to main view layout **********
        self.main_layout.addWidget(self.title)
        self.main_layout.addWidget(self.main_toolbar)
        self.main_layout.addWidget(self.dialogue_table)

    def RefreshCurrentRowSize(self):
        """ Resize the currently selected row based on the size of it's contents """
        self.dialogue_table.resizeRowToContents(self.dialogue_table.currentIndex().row())
        
    def Clear(self):
        """ Deletes all data in the dialogue table """
        for row in range(self.dialogue_table.rowCount(), 0, -1):
            self.dialogue_table.removeRow(row - 1)

    def AddEntry(self, action_data: dict, specific_row: int = None, skip_select: bool = False) -> DialogueEntry:
        """ Given a block of action data from the action database, create a new entry in the dialogue sequence """
        # Create a new, empty row. Allow optional row position specification, but default to the end of the sequence
        new_entry_row = self.dialogue_table.rowCount()
        if specific_row is not None:
            new_entry_row = specific_row
            self.dialogue_table.insertRow(new_entry_row)
        else:
            self.dialogue_table.insertRow(new_entry_row)

        # Create a new dialogue entry object, and add it to the sequence widget
        new_entry = DialogueEntry(
            copy.deepcopy(action_data),
            self.settings,
            self.ed_core.UpdateActiveEntry,
            self.RefreshCurrentRowSize
        )

        # Assign the entry widget to the row
        self.dialogue_table.setCellWidget(new_entry_row, 0, new_entry)

        # Since selecting the new row will cause the details panel to refresh, allow opting out in case
        # batch creation is happening
        if not skip_select:
            self.dialogue_table.selectRow(new_entry_row)

        # Resize the row to fit any contents it has
        self.dialogue_table.resizeRowToContents(new_entry_row)

        return new_entry

    def RemoveEntry(self):
        """ If an entry is selected, delete it from the table """
        selection = self.GetSelectedRow()

        if selection is not None:
            self.dialogue_table.removeRow(self.GetSelectedRow())

    def CopyEntry(self):
        """ If an entry is selected, clone it and add it to the sequence """
        selection = self.GetSelectedEntry()

        if selection:
            self.AddEntry(selection.action_data)

    def MoveEntryUp(self):
        """ If an entry is selected, move it up one row """
        if self.dialogue_table.rowCount():
            selection = self.GetSelectedRow()

            # Only allow moving up if we're not already at the top of the sequence
            if selection == 0:
                self.ed_core.logger.Log("Can't move entry up as we're at the top of the sequence", 3)
            else:
                # 'cellWidget' returns a pointer which becomes invalid once we override it's row. Given this, instead
                # of gently moving the row, we recreate it by transferring it's data to a newly created entry
                taken_entry = self.dialogue_table.cellWidget(selection, 0)

                # Delete the origin row
                self.dialogue_table.removeRow(selection)

                # Add a new entry two rows above the initial row
                new_row_num = selection - 1
                new_entry = self.AddEntry(taken_entry.action_data, new_row_num)

                # Transfer the data from the original entry to the new one, before refreshing the details
                new_entry.action_data = taken_entry.action_data
                self.ed_core.UpdateActiveEntry()

    def MoveEntryDown(self):
        """ If an entry is selected, move it down one row """
        if self.dialogue_table.rowCount():
            selection = self.GetSelectedRow()

            # Only allow moving down if we're not already at the bottom of the sequence
            if selection + 1 >= self.dialogue_table.rowCount():
                self.ed_core.logger.Log("Can't move entry down as we're at the bottom of the sequence", 3)
            else:
                # 'cellWidget' returns a pointer which becomes invalid once we override it's row. Given this, instead
                # of gently moving the row, we recreate it by transferring it's data to a newly created entry
                taken_entry = self.dialogue_table.cellWidget(selection, 0)

                # Delete the origin row
                self.dialogue_table.removeRow(selection)

                # Add a new entry two rows above the initial row
                new_row_num = selection + 1
                new_entry = self.AddEntry(taken_entry.action_data, new_row_num)

                # Transfer the data from the original entry to the new one, before refreshing the details
                new_entry.action_data = taken_entry.action_data
                self.ed_core.UpdateActiveEntry()

    def GetSelectedEntry(self) -> DialogueEntry:
        """ Returns the currently selected dialogue entry. If there isn't one, returns None """
        selected_entry = self.dialogue_table.selectedIndexes()

        if selected_entry:
            selected_row = selected_entry[0].row()
            return self.dialogue_table.cellWidget(selected_row, 0)
        else:
            return None

    def GetSelectedRow(self) -> int:
        """ Returns the currently selected row. If there isn't one, returns None """
        selected_row = self.dialogue_table.selectedIndexes()

        if selected_row:
            return selected_row[0].row()
        else:
            return None
