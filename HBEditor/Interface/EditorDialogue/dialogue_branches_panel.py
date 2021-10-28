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
from HBEditor.Interface.EditorDialogue.dialogue_branches_entry import BranchesEntry
from HBEditor.Interface.EditorDialogue.dialogue_branches_edit_prompt import EditBranchPrompt

class BranchesPanel(QtWidgets.QWidget):
    def __init__(self, settings, ed_core):
        super().__init__()

        self.ed_core = ed_core
        self.settings = settings

        # Keep track of the active branch as we're switching between entries so we know where
        # to store dialogue entry data
        self.active_branch = None

        self.branches_layout = QtWidgets.QVBoxLayout(self)
        self.branches_layout.setContentsMargins(0, 0, 0, 0)
        self.branches_layout.setSpacing(0)

        # Create title
        self.branches_title = QtWidgets.QLabel(self)
        self.branches_title.setFont(self.settings.header_1_font)
        self.branches_title.setStyleSheet(self.settings.header_1_color)
        self.branches_title.setText("Branches")

        # Create the toolbar
        self.branches_toolbar = QtWidgets.QFrame(self)
        self.branches_toolbar.setAutoFillBackground(False)
        self.branches_toolbar.setStyleSheet(
            "QFrame, QLabel, QToolTip {\n"
            "    border-radius: 4px;\n"
            f"   background-color: rgb({self.settings.toolbar_background_color});\n"
            "}"
        )
        self.branches_toolbar.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.branches_toolbar.setFrameShadow(QtWidgets.QFrame.Raised)
        self.branches_toolbar_layout = QtWidgets.QHBoxLayout(self.branches_toolbar)
        self.branches_toolbar_layout.setContentsMargins(2, 2, 2, 2)
        self.branches_toolbar_layout.setSpacing(0)

        # Generic button settings
        icon = QtGui.QIcon()
        button_style = (
            f"background-color: rgb({self.settings.toolbar_button_background_color});\n"
        )

        # Add Branch Button
        self.add_entry_button = QtWidgets.QToolButton(self.branches_toolbar)
        self.add_entry_button.setStyleSheet(button_style)
        icon.addPixmap(
            QtGui.QPixmap(self.settings.ConvertPartialToAbsolutePath("Content/Icons/Plus.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        self.add_entry_button.setIcon(icon)
        self.add_entry_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.add_entry_button.clicked.connect(self.AddBranch)
        self.branches_toolbar_layout.addWidget(self.add_entry_button)

        # Remove Branch Button
        self.remove_entry_button = QtWidgets.QToolButton(self.branches_toolbar)
        self.remove_entry_button.setStyleSheet(button_style)
        icon.addPixmap(
            QtGui.QPixmap(self.settings.ConvertPartialToAbsolutePath("Content/Icons/Minus.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        self.remove_entry_button.setIcon(icon)
        self.remove_entry_button.clicked.connect(self.RemoveBranch)
        self.branches_toolbar_layout.addWidget(self.remove_entry_button)

        # Create search filter
        #self.branches_filter = QtWidgets.QLineEdit(self.branches_toolbar)
        #self.branches_filter.setPlaceholderText("filter...")
        #self.branches_toolbar_layout.addWidget(self.branches_filter)

        # Create Empty Space Spacer
        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.branches_toolbar_layout.addItem(spacer)

        # Create Details List
        self.branches_list = QtWidgets.QListWidget(self)
        self.branches_list.itemDoubleClicked.connect(self.EditBranch)
        self.branches_list.itemSelectionChanged.connect(self.ChangeBranch)

        # ********** Add All Major Pieces to details layout **********
        self.branches_layout.addWidget(self.branches_title)
        self.branches_layout.addWidget(self.branches_toolbar)
        self.branches_layout.addWidget(self.branches_list)

    def CreateBranch(self, branch_name, branch_description):
        """ Adds a new branch entry to the branch list, and set it's name and description using the given data """
        # Create the list item container
        list_item = QtWidgets.QListWidgetItem()
        self.branches_list.addItem(list_item)

        # Create the core part of the entry
        new_entry = BranchesEntry(self.settings, None)
        self.branches_list.setItemWidget(list_item, new_entry)
        new_entry.Set((branch_name, branch_description))

        # Adjust the size hint of the item container to match the contents
        list_item.setSizeHint(new_entry.sizeHint())

        # Select the new entry
        self.branches_list.setCurrentItem(list_item)

    def AddBranch(self):
        """ Prompts the user for branch information, and creates a branch with that information """
        # Create the prompt object, using the defaults for the params
        branch_name, branch_description = self.ConfigurePrompt()

        # If the data has been validated, then create the new branch
        if branch_name:
            self.CreateBranch(branch_name, branch_description)

    def RemoveBranch(self):
        """ Deletes the selected branch if it is not the main branch """
        # Don't allow the user to delete the main branch
        if self.branches_list.currentRow() != 0:

            selected_row = self.branches_list.currentRow()
            self.branches_list.takeItem(selected_row)

    def EditBranch(self):
        selection = self.branches_list.selectedItems()[0]
        branch_entry = self.branches_list.itemWidget(selection)

        # Only allow editing for all entries other than the initial (main) entry
        if self.branches_list.currentRow() != 0:
            selected_branch = self.branches_list.itemWidget(selection)

            # Retrieves the tuple data of 'branch name' and 'branch description'
            data = selected_branch.Get()

            # Create the prompt object, providing the selected branch's data. Provide
            # the branch we're editing to so we bypass having to choose a new name
            new_data = self.ConfigurePrompt(data[0], data[1], selected_branch)

            # If the user has changed anything, then update the entry. Otherwise, do nothing
            if new_data:
                # Set the data before resizing the entry to fit the new data
                branch_entry.Set(new_data)
                self.ResizeListEntry(selection, branch_entry)

    def ConfigurePrompt(self, branch_name="New Name", branch_description="New Description", source_branch=None) -> tuple:
        """ Prompts the user with a branch configuration window. Returns the new data if provided, or None if not """
        # Create the prompt object
        prompt = EditBranchPrompt(branch_name, branch_description)

        # Use a loop here to allow the user to continually try again until they choose to cancel the process
        # This is particularly useful in case they wrote a description they really don't want to lose
        # 0 = dialog was cancelled, 1 = dialogue was accepted
        while prompt.exec() == 1:
            new_data = prompt.Get()

            # Validate the branch name before we try creating the branch
            if self.ValidateBranchName(new_data[0], source_branch):

                # Name validated. Return the new data
                return new_data

            # The chosen name already exists. Inform the user
            else:
                QtWidgets.QMessageBox.about(
                    self, "Branch Name in Use!",
                    "The chosen branch name is already in use!\nPlease choose a new name"
                )

    def ValidateBranchName(self, name, source_branch) -> bool:
        """
        Check if the provided branch name already exists. If a source branch is provided, then exempt it from
        being considered
        """
        for entry_index in range(0, self.branches_list.count()):
            entry = self.branches_list.itemWidget(self.branches_list.item(entry_index))

            print(source_branch)
            if source_branch:
                if entry == source_branch:
                    continue

            if entry.Get()[0] == name:
                # Match found
                return False

        # No match found
        return True

    def ResizeListEntry(self, list_item_container, list_item_object):
        """ Resize the provided list entry to match the size of it's contents """
        list_item_container.setSizeHint(list_item_object.sizeHint())

    def ChangeBranch(self, new_branch_index: int = -1):
        """ A wrapper for the real SwitchBranch function. This acquires and provides the right entry references """
        if new_branch_index > -1:
            self.branches_list.setCurrentRow(new_branch_index)

        selection = self.branches_list.itemWidget(self.branches_list.currentItem())

        self.ed_core.SwitchBranches(
            self.active_branch,
            selection
        )

        # Update the active branch to point to the newly selected branch
        self.active_branch = selection
