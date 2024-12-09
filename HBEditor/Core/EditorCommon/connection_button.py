from PyQt6 import QtWidgets, QtCore
from HBEditor.Core import settings
from HBEditor.Core.DataTypes.parameter_types import ParameterType
from HBEditor.Core.Logger import logger


class ConnectionButton(QtWidgets.QComboBox):
    SIG_USER_UPDATE = QtCore.pyqtSignal(object)
    SOURCE_OPTIONS  = ["Variables", "Settings"]

    def __init__(self, supported_type: ParameterType, owning_model_item: QtWidgets.QWidgetItem = None):
        super().__init__()
        self.owning_model_item = owning_model_item  # Track the owning widget so we can emit signals properly
        self.supported_type = supported_type
        self.setToolTip("Connect this parameter to a User Variable or Project Setting")

        # We can't store the category or the source in the dropdown, so store them here
        self.category = ""
        self.source = self.SOURCE_OPTIONS[0]

    def showPopup(self) -> None:
        result = self.ShowConnectionDialog()
        if result is None:
            logger.Log("Connection unchanged")
        else:
            self.Set(result)
            self.SIG_USER_UPDATE.emit(self.owning_model_item)

    def Get(self) -> tuple:
        """ Return a tuple of (Category_Name, Variable_Name, Source) """
        if self.currentText() == 'None':
            return None
        else:
            return self.category, self.currentText(), self.source

    def Set(self, data: tuple):
        """ Given a tuple of (Category_Name, Variable_Name, Source), update the selection """
        self.removeItem(0)

        if data is None:
            self.addItem('None')
            self.category = ''
            self.source = ''
        else:
            self.addItem(data[1])
            self.category = data[0]
            self.source = data[2]

    def ShowConnectionDialog(self) -> tuple:
        connect_dialog = DialogConnection(self.supported_type, self.SOURCE_OPTIONS)
        return connect_dialog.GetVariable()

class DialogConnection(QtWidgets.QDialog):
    def __init__(self, supported_type: ParameterType, source_options: list):
        super().__init__()

        # Contols for filtering or limiting shown options
        self.supported_type = supported_type
        self.source_options = source_options

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
        self.var_source.addItems(self.source_options)
        self.var_source.currentIndexChanged.connect(lambda: self.Populate(self.var_source.currentText()))
        self.options_layout.addWidget(self.var_source, 1)

        # Variable Tree
        self.variable_tree = QtWidgets.QTreeWidget(self)
        self.variable_tree.setColumnCount(1)
        self.variable_tree.header().hide()
        self.variable_tree.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)  # Disable multi-selection
        self.variable_tree.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectItems)  # Disables cell selection
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

    def GetVariable(self) -> tuple:
        """
        Activate the dialog, and return a tuple of (category_name, variable_name, source). If none were chosen, return 'None'
        """
        if self.exec():
            selection = self.variable_tree.selectedItems()
            if selection:
                return selection[0].parent().text(0), selection[0].text(0), self.var_source.currentText()

        return None


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
            new_cat_item.setFlags(new_cat_item.flags() & ~QtCore.Qt.ItemFlag.ItemIsSelectable)
            self.variable_tree.addTopLevelItem(new_cat_item)

            for var_name in cat_data:
                new_var_item = QtWidgets.QTreeWidgetItem()
                new_var_item.setText(0, var_name)
                new_var_item.setFlags(new_var_item.flags() | QtCore.Qt.ItemFlag.ItemIsSelectable)
                new_cat_item.addChild(new_var_item)

        self.variable_tree.expandAll()
