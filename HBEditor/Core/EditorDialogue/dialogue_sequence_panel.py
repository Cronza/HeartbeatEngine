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
from PyQt5 import QtWidgets, QtGui, QtCore
from HBEditor.Core.Logger.logger import Logger
from HBEditor.Core.ActionMenu.action_menu import ActionMenu
from HBEditor.Core.EditorCommon.DetailsPanel.base_source_entry import SourceEntry
from HBEditor.Core.EditorUtilities import action_data as ad


class DialogueSequencePanel(QtWidgets.QWidget):
    """
    The core U.I class for the dialogue sequence panel. This contains all logic for generating, moving and removing
    any and all child widgets pertaining to the panel.

    This class is not meant for any destructive data changes, merely U.I actions
    """
    def __init__(self, ed_core):
        super().__init__()

        self.ed_core = ed_core

        # Create an action menu to be used later on for adding entries to the sequence
        self.action_menu = ActionMenu(self.AddEntry, self.ed_core.file_type)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Create the View title
        self.title = QtWidgets.QLabel(self)
        self.title.setText("Dialogue Sequence")
        self.title.setObjectName("h1")

        # Create the toolbar
        self.main_toolbar = QtWidgets.QToolBar()

        # Add Entry Button (Popup Menu)
        self.add_entry_button = QtWidgets.QToolButton(self.main_toolbar)
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/Icons/Plus.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        self.add_entry_button.setIcon(icon)
        self.add_entry_button.setMenu(self.action_menu)
        self.add_entry_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.main_toolbar.addWidget(self.add_entry_button)

        # Remove Entry Button
        self.main_toolbar.addAction(
            QtGui.QIcon(QtGui.QPixmap(":/Icons/Minus.png")),
            "Remove Entry",
            self.RemoveEntry
        )

        # Copy Entry Button
        self.main_toolbar.addAction(
            QtGui.QIcon(QtGui.QPixmap(":/Icons/Copy.png")),
            "Copy Entry",
            self.CopyEntry
        )

        # Move Entry Up Button
        self.main_toolbar.addAction(
            QtGui.QIcon(QtGui.QPixmap(":/Icons/Up.png")),
            "Move Entry Up",
            self.MoveEntryUp
        )

        # Move Entry Down Button
        self.main_toolbar.addAction(
            QtGui.QIcon(QtGui.QPixmap(":/Icons/Down.png")),
            "Move Entry Up",
            self.MoveEntryDown
        )

        # Build the Action Sequence
        self.dialogue_table = QtWidgets.QTableWidget(self)
        self.dialogue_table.verticalHeader().setObjectName("vertical")
        self.dialogue_table.setColumnCount(1)
        self.dialogue_table.setShowGrid(False)
        self.dialogue_table.horizontalHeader().hide()
        self.dialogue_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.dialogue_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)  # Disable editing
        self.dialogue_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)  # Disable multi-selection
        self.dialogue_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)  # Disables cell selection
        self.dialogue_table.verticalHeader().setDefaultAlignment(QtCore.Qt.AlignCenter)
        self.dialogue_table.itemSelectionChanged.connect(self.ed_core.UpdateActiveEntry)

        # 'outline: none;' doesn't work for table widgets seemingly, so I can't use CSS to disable the
        # focus border. Thus, we do it the slightly more tragic way
        self.dialogue_table.setFocusPolicy(QtCore.Qt.NoFocus)

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

    def AddEntry(self, action_data: dict, specific_row: int = None, skip_select: bool = False):
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
        else:
            self.ed_core.UpdateActiveEntry()

    def CopyEntry(self):
        """ If an entry is selected, clone it and add it to the sequence """
        selection = self.GetSelectedEntry()

        if selection:
            self.AddEntry(selection.action_data)

    def MoveEntryUp(self):
        """ If an entry is selected, move it up one row """
        row_count = self.dialogue_table.rowCount()
        if row_count:
            selection_index = self.GetSelectedRow()

            # Only allow moving up if we're not already at the top of the sequence
            if selection_index < 0:
                Logger.getInstance().Log("No entry selected", 3)
            elif selection_index == 0:
                Logger.getInstance().Log("Can't move entry up as we're at the top of the sequence", 3)
            else:
                # 'cellWidget' returns a pointer which becomes invalid once we override it's row. Given this, instead
                # of gently moving the row, we recreate it by transferring it's data to a newly created entry
                taken_entry = self.dialogue_table.cellWidget(selection_index, 0)

                # Delete the origin row
                self.dialogue_table.removeRow(selection_index)

                # Add a new entry two rows above the initial row
                new_row_num = selection_index - 1
                new_entry = self.AddEntry(taken_entry.action_data, new_row_num)

                # Transfer the data from the original entry to the new one, before refreshing the details
                new_entry.action_data = taken_entry.action_data
                self.ed_core.UpdateActiveEntry()

    def MoveEntryDown(self):
        """ If an entry is selected, move it down one row """
        row_count = self.dialogue_table.rowCount()
        if self.dialogue_table.rowCount():
            selection_index = self.GetSelectedRow()

            # Only allow moving down if we're not already at the bottom of the sequence
            if selection_index < 0:
                Logger.getInstance().Log("No entry selected", 3)
            elif selection_index + 1 >= self.dialogue_table.rowCount():
                Logger.getInstance().Log("Can't move entry down as we're at the bottom of the sequence", 3)
            else:
                # 'cellWidget' returns a pointer which becomes invalid once we override it's row. Given this, instead
                # of gently moving the row, we recreate it by transferring it's data to a newly created entry
                taken_entry = self.dialogue_table.cellWidget(selection_index, 0)

                # Delete the origin row
                self.dialogue_table.removeRow(selection_index)

                # Add a new entry two rows above the initial row
                new_row_num = selection_index + 1
                new_entry = self.AddEntry(taken_entry.action_data, new_row_num)

                # Transfer the data from the original entry to the new one, before refreshing the details
                new_entry.action_data = taken_entry.action_data
                self.ed_core.UpdateActiveEntry()

    def GetSelectedEntry(self):
        """ Returns the currently selected dialogue entry. If there isn't one, returns None """
        selected_entry = self.dialogue_table.selectedIndexes()

        if selected_entry:
            selected_row = selected_entry[0].row()
            return self.dialogue_table.cellWidget(selected_row, 0)
        else:
            return None

    def GetSelectedRow(self) -> int:
        """ Returns the currently selected row. If there isn't one, returns -1 """
        selected_row = self.dialogue_table.selectedIndexes()

        if selected_row:
            return selected_row[0].row()
        else:
            return -1


class DialogueEntry(QtWidgets.QWidget, SourceEntry):
    def __init__(self, action_data, select_func, size_refresh_func):
        super().__init__()

        # Store a func object that is used when this entry is selected
        self.select_func = select_func

        # Store a func object that is used when the row containing this object should be resized based on the
        # subtext data in this object
        #@TODO: Replace with a Qt signal / slot
        self.size_refresh_func = size_refresh_func

        # Store this entry's action data
        self.action_data = action_data

        # ****** DISPLAY WIDGETS ******
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(4, 4, 0, 4)
        self.main_layout.setSpacing(0)

        self.name_widget = QtWidgets.QLabel()
        self.name_widget.setObjectName("h2")

        self.name_widget.setText(ad.GetActionDisplayName(self.action_data))
        self.subtext_widget = QtWidgets.QLabel()
        self.subtext_widget.setObjectName("text-soft-italic")

        # Refresh the subtext
        self.UpdateSubtext()

        # Add everything to the layout
        self.main_layout.addWidget(self.name_widget)
        self.main_layout.addWidget(self.subtext_widget)

    def Get(self) -> dict:
        """ Returns the action data stored in this object """
        return self.action_data

    def UpdateSubtext(self):
        """ Updates the subtext displaying entry parameters """
        self.subtext_widget.setText(self.CompileSubtextString(ad.GetActionRequirements(self.action_data)))

    def CompileSubtextString(self, req_data):
        """ Given a list of requirements from the actions_metadata file, compile them into a user-friendly string """
        cur_string = ""
        for name, data in req_data.items():
            if "flags" in data:
                if "preview" in data["flags"]:
                    if "children" in data:
                        cur_string += f"{name}: ["
                        cur_string += self.CompileSubtextString(data['children'])
                        cur_string += "], "

                    elif "value" in data:
                        req_value = data["value"]
                        cur_string += f"{name}: {req_value}, "

        # Due to how the comma formatting is, strip it from the end of the string
        return cur_string.strip(', ')

    def Refresh(self, change_tree: list = None):
        self.size_refresh_func()
        self.UpdateSubtext()

