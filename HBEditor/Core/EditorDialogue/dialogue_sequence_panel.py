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
from HBEditor.Core.Logger.logger import Logger
from HBEditor.Core.settings import Settings
from HBEditor.Core.Menus.ActionMenu.action_menu import ActionMenu


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
        self.action_menu = ActionMenu(self.AddEntry, Settings.getInstance().action_database)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Create the View title
        self.title = QtWidgets.QLabel(self)
        self.title.setFont(Settings.getInstance().header_1_font)
        self.title.setStyleSheet(Settings.getInstance().header_1_color)
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
            f"background-color: rgb({Settings.getInstance().toolbar_button_background_color});\n"
        )

        # Add Entry Button (Popup Menu)
        self.add_entry_button = QtWidgets.QToolButton(self.main_toolbar)
        self.add_entry_button.setStyleSheet(button_style)
        icon.addPixmap(
            QtGui.QPixmap(Settings.getInstance().ConvertPartialToAbsolutePath("Content/Icons/Plus.png")),
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
            QtGui.QPixmap(Settings.getInstance().ConvertPartialToAbsolutePath("Content/Icons/Minus.png")),
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
            QtGui.QPixmap(Settings.getInstance().ConvertPartialToAbsolutePath("Content/Icons/Copy.png")),
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
            QtGui.QPixmap(Settings.getInstance().ConvertPartialToAbsolutePath("Content/Icons/Up.png")),
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
            QtGui.QPixmap(Settings.getInstance().ConvertPartialToAbsolutePath("Content/Icons/Down.png")),
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
        self.dialogue_table.verticalHeader().setStyleSheet(Settings.getInstance().selection_color)
        self.dialogue_table.setStyleSheet(Settings.getInstance().selection_color)
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
            if not selection:
                Logger.getInstance().Log("No entry selected", 3)
            elif selection == 0:
                Logger.getInstance().Log("Can't move entry up as we're at the top of the sequence", 3)
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
            if not selection:
                Logger.getInstance().Log("No entry selected", 3)
            elif selection + 1 >= self.dialogue_table.rowCount():
                Logger.getInstance().Log("Can't move entry down as we're at the bottom of the sequence", 3)
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

    def GetSelectedEntry(self):
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


class DialogueEntry(QtWidgets.QWidget):
    def __init__(self, action_data, select_func, size_refresh_func):
        super().__init__()

        # Store a func object that is used when this entry is selected
        self.select_func = select_func

        # Store a func object that is used when the row containing this object should be resized based on the
        # subtext data in this object
        self.size_refresh_func = size_refresh_func

        # Store this entries action data
        self.action_data = action_data

        # ****** DISPLAY WIDGETS ******
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Name
        self.name_widget = QtWidgets.QLabel()
        self.name_widget.setFont(Settings.getInstance().header_2_font)
        self.name_widget.setStyleSheet(Settings.getInstance().header_2_color)
        self.name_widget.setText(self.action_data["display_name"])

        # Details
        self.subtext_widget = QtWidgets.QLabel()
        self.subtext_widget.setFont(Settings.getInstance().subtext_font)
        self.subtext_widget.setStyleSheet(Settings.getInstance().subtext_color)

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
        if "requirements" in self.action_data:
            self.subtext_widget.setText(self.CompileSubtextString(self.action_data["requirements"]))

    def CompileSubtextString(self, data):
        """ Given a list of requirements from the ActionsDatabase file, compile them into a user-friendly string """
        #@TODO: Resolve issue for actions that don't have any requirements (IE. Stop Music)
        cur_string = ""
        for param in data:
            if param["preview"]:

                param_name = param["name"]
                param_data = None

                if param["type"] == "container":
                    # Recurse, searching the children as well
                    cur_string += f"{param_name}: ["
                    cur_string += self.CompileSubtextString(param['children'])
                    cur_string += "], "

                else:
                    param_data = param["value"]
                    cur_string += f"{param_name}: {param_data}, "

        # Due to how the comma formatting is, strip it from the end of the string
        return cur_string.strip(', ')

    def Refresh(self):
        """
        Refresh is the common function used by elements that need refreshing when an important U.I change is made
        """
        self.UpdateSubtext()
        self.size_refresh_func()
