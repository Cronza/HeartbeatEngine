from PyQt6 import QtWidgets, QtCore
from HBEditor.Core import settings
from HBEditor.Core.DataTypes.parameter_types import ParameterType
from HBEditor.Core.Logger import logger


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
            logger.Log("Connection unchanged")
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

        # A list of 'FileType' that controls the available options in this browser
        self.supported_type = supported_type

        # Hide the OS header to lock its position
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.resize(640, 400)
        self.main_layout = QtWidgets.QVBoxLayout(self)

        # Options
        self.options_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.addLayout(self.options_layout)

        self.search_input = QtWidgets.QLineEdit(self)
        self.search_input.setPlaceholderText("Search...")
        self.search_input.textEdited.connect(self.GetSearchedVariables)  # Re-search on every char input
        self.options_layout.addWidget(self.search_input, 2)

        self.type_explanation = QtWidgets.QLabel(f"Expected Type: {self.supported_type.name}")
        self.options_layout.addWidget(self.type_explanation, 1)

        self.var_source = QtWidgets.QComboBox(self)
        self.var_source.addItems(["Variables", "Settings"])
        self.var_source.currentIndexChanged.connect(lambda: self.Populate(self.var_source.currentText()))
        self.options_layout.addWidget(self.var_source, 1)

        # Asset Tree
        self.variable_tree = QtWidgets.QTreeWidget(self)
        self.variable_tree.setColumnCount(1)
        self.variable_tree.header().hide()
        self.variable_tree.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)  # Disable multi-selection
        self.variable_tree.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)  # Disables cell selection
        self.variable_tree.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        """
        self.details_tree.setObjectName("no-top")
        self.details_tree.setColumnCount(3)
        self.details_tree.setHeaderLabels(['Name', 'Input', 'Connection'])
        self.details_tree.setAutoScroll(False)
        self.details_tree.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.details_tree.header().setStretchLastSection(False)  # Disable to allow custom sizing
        self.details_tree.header().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Interactive)
        self.details_tree.header().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Interactive)
        self.details_tree.header().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.details_tree.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        """

        self.main_layout.addWidget(self.variable_tree)

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
        """
        if self.exec():
            selection = self.variable_list.selectedItems()
            if selection:
                return selection[0].text()
        """
        if self.exec():
            pass
        return ""  # Since 'None' is a legitimate answer, use '' to represent a cancelled dialog


    def GetVariablesOfType(self, target_type: ParameterType, source: str = "Variables") -> dict:
        """ Returns a dict of categories with nested lists of variables that match the provided type """
        source_data = {}
        if source == "Variables":
            source_data = settings.user_project_variables
        else:
            source_data = settings.user_project_data

        applicable_variables = {}
        for cat_name, cat_data in source_data.items():
            for val_name, val_data in cat_data.items():
                if ParameterType[val_data['type']] == target_type:
                    if cat_name not in applicable_variables:
                        applicable_variables[cat_name] = []
                    applicable_variables[cat_name].append(val_name)

        return applicable_variables

    def GetSearchedVariables(self):
        """ Use the search_input text to hide all items that don't have it as a substring. Reveal those that do """
        self.variable_tree.clearSelection()

        search_criteria = self.search_input.text().lower()
        for cat_index in range(0, self.variable_tree.topLevelItemCount()):
            cat_item = self.variable_tree.topLevelItem(cat_index)
            for var_index in range(cat_item.childCount()):
                var_item = cat_item.child(var_index)
                if search_criteria not in var_item.text(0).lower():
                    var_item.setHidden(True)
                else:
                    var_item.setHidden(False)

    def SwitchContentDirectories(self):
        """
        Reloads the variable tree based on what source was chosen in the var_source dropdown
        """
        if self.GetUsingEngineContent():
            self.valid_assets = self.GetFilteredAssets(settings.engine_asset_registry)
            self.GenerateAssetEntries()
        else:
            self.valid_assets = self.GetFilteredAssets(settings.asset_registry)
            self.GenerateAssetEntries()

    def Populate(self, source: str = "Variables"):
        """
        Clear the variable tree, then create a entry for each category and a nested entry for each variable that
        matches the supported type
        """
        self.variable_tree.clear()

        applicable_vars = self.GetVariablesOfType(self.supported_type, source)
        for cat_name, cat_data in applicable_vars.items():
            new_cat_item = QtWidgets.QTreeWidgetItem()
            new_cat_item.setText(0, cat_name)
            new_cat_item.setFlags(new_cat_item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.variable_tree.addTopLevelItem(new_cat_item)

            for var_name in cat_data:
                new_var_item = QtWidgets.QTreeWidgetItem()
                new_var_item.setText(0, var_name)
                new_cat_item.addChild(new_var_item)

        self.variable_tree.expandAll()
