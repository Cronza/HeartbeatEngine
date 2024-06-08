from PyQt6 import QtWidgets, QtCore
from HBEditor.Core import settings
from HBEditor.Core.DataTypes.parameter_types import ParameterType
from HBEditor.Core.Logger.logger import Logger


class ConnectionButton(QtWidgets.QComboBox):
    SIG_USER_UPDATE = QtCore.pyqtSignal(object, str)

    def __init__(self, supported_type: ParameterType, owning_model_item: QtWidgets.QWidgetItem = None):
        super().__init__()
        self.owning_model_item = owning_model_item  # Track the owning widget so we can emit signals properly
        self.supported_type = supported_type
        self.setToolTip("Connect this parameter to a project variable")

    def showPopup(self) -> None:
        result = self.ShowConnectionDialog()
        if result == self.currentText() or result == '':
            Logger.getInstance().Log("Connection unchanged")
        else:
            self.Set(result)
            self.SIG_USER_UPDATE.emit(self.owning_model_item, result)

    def Get(self) -> str:
        return self.currentText()

    def Set(self, new_value: str):
        self.removeItem(0)
        self.addItem(new_value)

    def ShowConnectionDialog(self) -> str:
        connect_dialog = DialogConnection(self.supported_type)
        return connect_dialog.GetVariable()


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
        applicable_variables = ['None']
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
