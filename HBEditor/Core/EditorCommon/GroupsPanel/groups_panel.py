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
from HBEditor.Core import settings
from HBEditor.Core.Primitives.simple_checkbox import SimpleCheckbox
from HBEditor.Core.Logger.logger import Logger


class GroupsPanel(QtWidgets.QWidget):
    def __init__(self,
                 change_func: callable = None,
                 title: str = "Groups",
                 enable_togglable_entries: bool = False,
                 toggle_func: callable = None):
        super().__init__()

        # Simplify the reference to the active group
        self.active_entry = None

        # Callbacks
        self.change_func = change_func

        # Configurable properties
        self.enable_togglable_entries = enable_togglable_entries
        self.toggle_func = toggle_func

        ### U.I ###

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Create title
        self.title = QtWidgets.QLabel(self)
        self.title.setObjectName("h1")
        self.title.setText(title)

        # Create the toolbar
        self.toolbar = QtWidgets.QToolBar(self)

        # Add Group Button
        self.toolbar.addAction(
            QtGui.QIcon(QtGui.QPixmap(":/Icons/Plus.png")),
            "Add Entry",
            self.AddEntry
        )

        # Remove Entry Button
        self.toolbar.addAction(
            QtGui.QIcon(QtGui.QPixmap(":/Icons/Minus.png")),
            "Remove Entry",
            self.RemoveEntry
        )

        # Create search filter
        #self.groups_filter = QtWidgets.QLineEdit(self.toolbar)
        #self.groups_filter.setPlaceholderText("filter...")
        #self.toolbar_layout.addWidget(self.groups_filter)

        # Create entry List
        self.entry_list = QtWidgets.QListWidget(self)
        self.entry_list.setObjectName("groups-panel")
        self.entry_list.itemDoubleClicked.connect(self.EditEntry)
        self.entry_list.itemSelectionChanged.connect(self.ChangeEntry)

        # 'outline: none;' doesn't work for list widgets seemingly, so I can't use CSS to disable the
        # focus border. Thus, we do it the slightly worse way
        self.entry_list.setFocusPolicy(QtCore.Qt.NoFocus)

        # ********** Add All Major Pieces to details layout **********
        self.main_layout.addWidget(self.title)
        self.main_layout.addWidget(self.toolbar)
        self.main_layout.addWidget(self.entry_list)

    def CreateEntry(self, name, description, toggle: bool = False):
        """ Adds a new entry to the group list, and set its name and description using the given data """
        # Create the list item container
        list_item = QtWidgets.QListWidgetItem()
        self.entry_list.addItem(list_item)

        # Create the core part of the entry
        new_entry = GroupEntry(self.enable_togglable_entries)
        if self.enable_togglable_entries:
            new_entry.SetToggle(toggle)
            new_entry.SIG_USER_TOGGLE.connect(self.toggle_func)

        self.entry_list.setItemWidget(list_item, new_entry)
        new_entry.Set((name, description))

        # Adjust the size hint of the item container to match the contents
        list_item.setSizeHint(new_entry.sizeHint())

        # Select the new entry
        self.entry_list.setCurrentItem(list_item)

    def AddEntry(self):
        """ Prompts the user for entry information, and creates an entry with that information """
        # Create the prompt object, using the defaults for the params
        name, description = self.ConfigurePrompt()

        # If the data has been validated, then create the new entry
        if name:
            self.CreateEntry(name, description)

    def RemoveEntry(self):
        """ Deletes the selected entry if it is not the main entry """
        # Don't allow the user to delete the main entry
        if self.entry_list.currentRow() != 0:

            selected_row = self.entry_list.currentRow()
            self.entry_list.takeItem(selected_row)

    def EditEntry(self):
        selection = self.entry_list.selectedItems()[0]

        # Only allow editing for all entries other than the initial (main) entry
        if self.entry_list.currentRow() != 0:
            selected_entry = self.entry_list.itemWidget(selection)

            # Retrieves the tuple data of 'name' and 'description'
            data = selected_entry.Get()

            # Create the prompt object, providing the selected entry's data. Provide
            # the entry we're editing too so we bypass having to choose a new name
            new_data = self.ConfigurePrompt(data[0], data[1], selected_entry)

            # Update the entry only if the name is valid (description can be null)
            if new_data[0]:
                selected_entry.Set(new_data)
                self.ResizeEntry(selection, selected_entry)

    def ConfigurePrompt(self, name="New Name", description="New Description", source_entry=None) -> tuple:
        """ Prompts the user with a configuration window. Returns the new data if provided, or None if not """
        # Create the prompt object
        prompt = EditEntryPrompt(name, description)

        # Use a loop here to allow the user to continually try again until they choose to cancel the process
        # This is particularly useful in case they wrote a description they really don't want to lose
        # 0 = dialog was cancelled, 1 = dialogue was accepted
        while prompt.exec() == 1:
            new_data = prompt.Get()

            # Validate the name before we try creating the entry
            if self.ValidateEntryName(new_data[0], source_entry):

                # Name validated. Return the new data
                return new_data

            # The chosen name already exists. Inform the user
            else:
                QtWidgets.QMessageBox.about(
                    self, "Entry Name in Use!",
                    "The chosen entry name is already in use!\nPlease choose a new name"
                )
        # User cancelled
        return "", ""

    def ValidateEntryName(self, name, source_entry=None) -> bool:
        """
        Check if the provided entry name is acceptable. This includes the following checks:
        - Name isn't already in use
        - Name isn't null

        If a source entry is provided, then exempt it from being considered
        """
        if not name:

            # Name is null
            return False

        for entry_index in range(0, self.entry_list.count()):
            entry = self.entry_list.itemWidget(self.entry_list.item(entry_index))

            if entry == source_entry:
                continue

            if entry.Get()[0] == name:
                # Match found
                return False

        # No match found
        return True

    def ResizeEntry(self, entry: QtWidgets.QListWidgetItem, entry_data_obj):
        """ Resize the provided entry to match the size of its contents """
        entry.setSizeHint(entry_data_obj.sizeHint())

    def ChangeEntry(self, new_entry_index: int = -1):
        if new_entry_index > -1:
            self.entry_list.setCurrentRow(new_entry_index)

        selection = self.entry_list.itemWidget(self.entry_list.currentItem())

        if self.change_func:
            self.change_func(
                self.active_entry,
                selection
            )

        # Update the active entry to point to the newly selected entry
        self.active_entry = selection

    def GetCount(self):
        """ Return the number of entries """
        return self.entry_list.count()

    def GetEntryItemWidget(self, entry_index: int):
        """ Returns the item widget for the entry of the provided index """
        return self.entry_list.itemWidget(self.entry_list.item(entry_index))


class GroupEntry(QtWidgets.QWidget):
    """
    An entry for the Group Panel

    Attributes
        SIG_USER_TOGGLE: - Signal that reports (toggle_state, group_name)
    """
    SIG_USER_TOGGLE = QtCore.pyqtSignal(bool, str)

    def __init__(self, use_toggle: bool = False):
        super().__init__()

        # Store any necessary data associated with this entry (From another panel or otherwise)
        self.data = []

        # ****** DISPLAY WIDGETS ******
        # Due to some size shenanigans with the widgets when they have a certain amount of text, force them to use
        # the minimum where possible
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.setStretch(0, 10)

        self.info_layout = QtWidgets.QVBoxLayout(self)
        self.info_layout.setContentsMargins(4, 4, 0, 4)
        self.info_layout.setSpacing(0)
        self.main_layout.addLayout(self.info_layout)

        #@TODO: Investigate why QLabel size hint includes newlines needed for wordwrap
        # Name
        self.name_widget = QtWidgets.QLabel()
        self.name_widget.setObjectName("h2")
        self.name_widget.setWordWrap(True)
        self.name_widget.setText("Test Name")
        self.name_widget.setSizePolicy(size_policy)
        self.name_widget.heightForWidth(0)
        self.info_layout.addWidget(self.name_widget)

        # Details
        self.subtext_widget = QtWidgets.QLabel()
        self.subtext_widget.setObjectName("text-soft-italic")
        self.subtext_widget.setText('Test Description')
        self.subtext_widget.setAlignment(QtCore.Qt.AlignTop)
        self.subtext_widget.setSizePolicy(size_policy)
        self.info_layout.addWidget(self.subtext_widget)

        self.toggle_button = None
        if use_toggle:
            # Add a space to force the toggle button to the far end
            self.toggle_layout = QtWidgets.QHBoxLayout(self)
            self.toggle_layout.addStretch(10)
            self.toggle_button = SimpleCheckbox()
            self.toggle_button.setToolTip("Whether to use the global value specified in the project file for this entry")
            self.toggle_button.Connect()
            self.toggle_button.SIG_USER_UPDATE.connect(lambda toggle: self.SIG_USER_TOGGLE.emit(self.toggle_button.Get(), self.Get()[0]))
            self.toggle_layout.addWidget(self.toggle_button)
            self.main_layout.addLayout(self.toggle_layout)

    def Get(self):
        """ Returns a tuple of ('name', 'description') """
        return self.name_widget.text(), self.subtext_widget.text()

    def Set(self, data):
        """ Given a tuple of ('name' and 'description'), update the relevant widgets """
        self.name_widget.setText(data[0])
        self.subtext_widget.setText(data[1])

    def SetToggle(self, newState: bool):
        """ Sets the state of the toggle button """
        if self.toggle_button:
            self.toggle_button.Set(newState)

    def GetData(self) -> list:
        """ Returns the data stored in this entry """
        return self.data


class EditEntryPrompt(QtWidgets.QDialog):
    def __init__(self, name, description, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Entry Configuration")

        # Create layout and add widgets
        self.main_layout = QtWidgets.QVBoxLayout()

        # Name
        self.entry_name_header = QtWidgets.QLabel("Name:")
        self.entry_name_input = QtWidgets.QLineEdit(name)

        # Description
        self.entry_description_header = QtWidgets.QLabel("Description:")
        self.entry_description_input = QtWidgets.QPlainTextEdit(description)

        # Cancel & Accept
        self.button_layout = QtWidgets.QHBoxLayout()
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.accept_button = QtWidgets.QPushButton("Accept")
        self.button_layout.addWidget(self.accept_button)
        self.button_layout.addWidget(self.cancel_button)

        # Add everything together
        self.main_layout.addWidget(self.entry_name_header)
        self.main_layout.addWidget(self.entry_name_input)
        self.main_layout.addWidget(self.entry_description_header)
        self.main_layout.addWidget(self.entry_description_input)
        self.main_layout.addLayout(self.button_layout)

        # Set dialog layout
        self.setLayout(self.main_layout)

        # Connect buttons
        self.accept_button.clicked.connect(self.Accept)
        self.cancel_button.clicked.connect(self.Cancel)

    def Cancel(self):
        self.reject()

    def Accept(self):
        if self.entry_name_input.text() == "":
            Logger.getInstance.Log("No entry name provided - Cancelling prompt")
            self.reject()
        else:
            self.accept()

    def Get(self):
        """ Returns the name and description as a tuple """
        return self.entry_name_input.text(), self.entry_description_input.toPlainText()


