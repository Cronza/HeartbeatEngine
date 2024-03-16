from PyQt6 import QtWidgets, QtCore, QtGui
from HBEditor.Core import settings
from HBEditor.Core.Primitives.input_entries import InputEntryDropdown
from HBEditor.Core.DataTypes.parameter_types import ParameterType
from HBEditor.Core.Primitives.simple_checkbox import SimpleCheckbox
from HBEditor.Core.Logger.logger import Logger


class ConnectButton(SimpleCheckbox):
    SIG_USER_UPDATE = QtCore.pyqtSignal(object, str)
    
    def __init__(self, supported_type: ParameterType):
        super().__init__()
        self.checkbox.setObjectName("connect-button")
        #self.checkbox.setTristate(True)
        self.state = QtCore.Qt.CheckState.Checked  # Track existing state to compare against new states
        self.setToolTip("Connect this parameter to a variable, or to the global setting")
        self.supported_type = supported_type  # Allow filtering the list of possible connection targets

        # Track the setting chosen by the user. This is either 'None', '<global>' or a name of a variable
        self.data = ''

    def ShowConnectionDialog(self) -> str:
        connect_dialog = DialogConnection(self.supported_type)
        return connect_dialog.GetVariable()

    def ValidateState(self, new_state: int):
        """ Based on the new state, show the connection prompt before setting the state appropriately """
        result = self.ShowConnectionDialog()

        if result == self.data or result == '':
            self.Disconnect()
            self.checkbox.setCheckState(self.state)
            self.Connect()
            Logger.getInstance().Log("Connection unchanged")
        else:
            if result != '':
                if new_state == 2:  # User is activating button while it's not set to something
                    if result == '<Global>':
                        self.Disconnect()
                        self.checkbox.setCheckState(QtCore.Qt.CheckState.PartiallyChecked)  # Differentiate global references
                        self.Connect()
                    elif result == 'None':
                        self.Disconnect()
                        print("State", self.state)
                        self.checkbox.setCheckState(self.state)
                        self.Connect()
                else:  # User is activating button while it's set to something
                    if result == '<Global>':
                        self.Disconnect()
                        self.checkbox.setCheckState(QtCore.Qt.CheckState.PartiallyChecked)  # Undo state change
                        self.Connect()
                    elif result != 'None':
                        self.Disconnect()
                        self.checkbox.setCheckState(self.state)
                        self.Connect()

                # Update stored data and state, then inform onlookers
                self.data = result
                self.state = self.checkbox.checkState()
                self.SIG_USER_UPDATE.emit(self.owner, result)




    def Get(self) -> str:
        """ Returns whether the checkbox is checked """
        return self.data

    def Set(self, value: str) -> None:
        if value == 'None':
            self.checkbox.setCheckState(QtCore.Qt.CheckState.Unchecked)
        if value == '<Global>':
            self.checkbox.setCheckState(QtCore.Qt.CheckState.PartiallyChecked)
        elif value:
            self.checkbox.setCheckState(QtCore.Qt.CheckState.Checked)

        self.state = self.checkbox.checkState()
        self.data = value

    def Connect(self):
        self.checkbox.stateChanged.connect(self.ValidateState)

    def Disconnect(self):
        self.checkbox.disconnect()


class DialogConnection(QtWidgets.QDialog):
    def __init__(self, supported_type: ParameterType):
        super().__init__()

        # A list of 'FileType' that controls the available files in this browser
        self.supported_type = supported_type

        # Hide the OS header to lock its position
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.resize(640, 400)
        self.main_layout = QtWidgets.QVBoxLayout(self)

        # Options - Search and Active Content Directory
        self.options_layout = QtWidgets.QHBoxLayout(self)
        self.search_input = QtWidgets.QLineEdit(self)
        self.search_input.setPlaceholderText("Search...")
        self.search_input.textEdited.connect(self.GetSearchedVariables)  # Re-search on every char input
        self.options_layout.addWidget(self.search_input, 2)
        self.type_explanation = QtWidgets.QLabel(f"Expected Type: {self.supported_type.name}")
        self.options_layout.addWidget(self.type_explanation, 1)
        self.main_layout.addLayout(self.options_layout)

        # Asset List
        self.variable_list = QtWidgets.QListWidget(self)
        self.main_layout.addWidget(self.variable_list)

        # Confirmation Buttons
        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.main_layout.addWidget(self.button_box)

        self.Populate()

    def GetVariable(self) -> str:
        """
        Activate the dialog, and return the name of the variable selected. If none were chosen, return 'None'
        """
        if self.exec():
            selection = self.variable_list.selectedItems()
            if selection:
                return selection[0].text()

        return ""  # Since 'None' is a legitimate answer, use '' to represent a cancelled dialog

    def GetVariablesOfType(self, target_type: ParameterType):
        """ Returns a list of names for all variables that match the provided type """
        applicable_variables = ['None', '<Global>']
        for val_name, val_data in settings.user_project_variables.items():
            if ParameterType[val_data['type']] == target_type:
                applicable_variables.append(val_name)

        return applicable_variables

    def GetSearchedVariables(self):
        """ Use the search_input text to hide all items that don't have it as a substring. Reveal those that do """
        self.variable_list.clearSelection()
        search_criteria = self.search_input.text().lower()
        for item_index in range(0, self.variable_list.count()):
            var_item = self.variable_list.item(item_index)
            if search_criteria not in var_item.text().lower():
                var_item.setHidden(True)
            else:
                var_item.setHidden(False)

    def Populate(self):
        """ Clear the variable list, then create an entry for each variable that matches the supported type. Lastly,
        add them to 'variable_list' """
        self.variable_list.clear()

        applicable_vars = self.GetVariablesOfType(self.supported_type)
        for item in applicable_vars:
            new_item = QtWidgets.QListWidgetItem()
            new_item.setText(item)
            self.variable_list.addItem(new_item)
