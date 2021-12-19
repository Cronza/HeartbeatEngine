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
from PyQt5 import QtWidgets, QtGui, QtCore
from HBEditor.Core.settings import Settings


class BranchesPanel(QtWidgets.QWidget):
    def __init__(self, ed_core):
        super().__init__()

        self.ed_core = ed_core

        # Keep track of the active branch as we're switching between entries so we know where
        # to store dialogue entry data
        self.active_branch = None

        self.branches_layout = QtWidgets.QVBoxLayout(self)
        self.branches_layout.setContentsMargins(0, 0, 0, 0)
        self.branches_layout.setSpacing(0)

        # Create title
        self.branches_title = QtWidgets.QLabel(self)
        self.branches_title.setObjectName("h1")
        self.branches_title.setText("Branches")

        # Create the toolbar
        self.branches_toolbar = QtWidgets.QToolBar(self)

        # Add Branch Button
        self.branches_toolbar.addAction(
            QtGui.QIcon(QtGui.QPixmap(":/Icons/Plus.png")),
            "Add Branch",
            self.AddBranch
        )

        # Remove Branch Button
        self.branches_toolbar.addAction(
            QtGui.QIcon(QtGui.QPixmap(":/Icons/Minus.png")),
            "Remove Branch",
            self.RemoveBranch
        )

        # Create search filter
        #self.branches_filter = QtWidgets.QLineEdit(self.branches_toolbar)
        #self.branches_filter.setPlaceholderText("filter...")
        #self.branches_toolbar_layout.addWidget(self.branches_filter)

        # Create Details List
        self.branches_list = QtWidgets.QListWidget(self)
        self.branches_list.setObjectName("dialogue-branch-panel")
        self.branches_list.itemDoubleClicked.connect(self.EditBranch)
        self.branches_list.itemSelectionChanged.connect(self.ChangeBranch)

        # 'outline: none;' doesn't work for list widgets seemingly, so I can't use CSS to disable the
        # focus border. Thus, we do it the slightly more tragic way
        self.branches_list.setFocusPolicy(QtCore.Qt.NoFocus)

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
        new_entry = BranchesEntry(None)
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
            if all(new_data):
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
        # User cancelled
        return None, None

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


class BranchesEntry(QtWidgets.QWidget):
    def __init__(self, select_func):
        super().__init__()

        # Store a func object that is used when this entry is selected
        self.select_func = select_func

        # Store all dialogue entries associated with this branch
        self.branch_data = []

        # ****** DISPLAY WIDGETS ******
        # Due to some size shenanigans with the widgets when they have a certain amount of text, force them to use
        # the minimum where possible
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                           QtWidgets.QSizePolicy.Minimum)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(4, 0, 0, 0)

        #@TODO: Investigate why QLabel size hint includes newlines needed for wordwrap
        # Name
        self.name_widget = QtWidgets.QLabel()
        self.name_widget.setObjectName("h2")
        self.name_widget.setWordWrap(True)
        self.name_widget.setText("Test Name")
        self.name_widget.setSizePolicy(size_policy)
        self.name_widget.heightForWidth(0)

        # Details
        self.subtext_widget = QtWidgets.QLabel()
        self.subtext_widget.setObjectName("text-soft-italic")
        self.subtext_widget.setText('Test Description')
        self.subtext_widget.setAlignment(QtCore.Qt.AlignTop)
        self.subtext_widget.setSizePolicy(size_policy)

        # Add everything to the layout
        self.main_layout.addWidget(self.name_widget)
        self.main_layout.addWidget(self.subtext_widget)

    def Get(self):
        """ Returns a tuple of 'branch name', 'branch description' """
        return self.name_widget.text(), self.subtext_widget.text()

    def Set(self, data):
        """ Given a tuple of 'branch name' and 'branch description', update the relevant widgets """
        self.name_widget.setText(data[0])
        self.subtext_widget.setText(data[1])

    def GetData(self) -> list:
        """ Returns a list of dialogue entry data stored in this branch entry """
        return self.branch_data

    def Refresh(self):
        """
        Refresh is the common function used by elements that need refreshing when an important U.I change is made
        """

        pass


class EditBranchPrompt(QtWidgets.QDialog):
    def __init__(self, branch_name, branch_description, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Branch Configuration")

        # Create layout and add widgets
        self.main_layout = QtWidgets.QVBoxLayout()

        # Branch name
        self.branch_name_header = QtWidgets.QLabel("Branch Name:")
        self.branch_name_input = QtWidgets.QLineEdit(branch_name)

        # Branch description
        self.branch_description_header = QtWidgets.QLabel("Branch Description:")
        self.branch_description_input = QtWidgets.QPlainTextEdit(branch_description)

        # Cancel & Accept
        self.button_layout = QtWidgets.QHBoxLayout()
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.accept_button = QtWidgets.QPushButton("Accept")
        self.button_layout.addWidget(self.accept_button)
        self.button_layout.addWidget(self.cancel_button)

        # Add everything together
        self.main_layout.addWidget(self.branch_name_header)
        self.main_layout.addWidget(self.branch_name_input)
        self.main_layout.addWidget(self.branch_description_header)
        self.main_layout.addWidget(self.branch_description_input)
        self.main_layout.addLayout(self.button_layout)
        # Set dialog layout
        self.setLayout(self.main_layout)

        # Connect buttons
        self.accept_button.clicked.connect(self.Accept)
        self.cancel_button.clicked.connect(self.Cancel)


    def Cancel(self):
        self.reject()

    def Accept(self):
        if self.branch_name_input.text() == "":
            print("No branch name provided - Cancelling prompt")
            self.reject()
        else:
            self.accept()

    def Get(self):
        """ Returns the branch name and description as a tuple """
        return self.branch_name_input.text(), self.branch_description_input.toPlainText()
