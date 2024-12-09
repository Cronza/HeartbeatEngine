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
from PyQt6 import QtWidgets, QtGui, QtCore
from HBEditor.Core.base_editor_ui import EditorBaseUI
from HBEditor.Core.DataTypes.parameter_types import ParameterType
from HBEditor.Core.EditorCommon.input_entries import InputEntryText
from HBEditor.Core.EditorCommon import input_entry_handler as ieh
from HBEditor.Core.EditorCommon.GroupsPanel.groups_panel import GroupsPanel


class EditorVariablesUI(EditorBaseUI):
    def __init__(self, core_ref):
        super().__init__(core_ref)
        # Track the active category, as we need a reference to it when we switch categories
        self.active_category = None

        # Build the core editor layout object
        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Allow the user to resize each section
        self.main_resize_container = QtWidgets.QSplitter(self)

        # Category Section
        self.categories = GroupsPanel("Categories", False, False)
        self.categories.SIG_USER_UPDATE.connect(self.SIG_USER_UPDATE.emit)
        self.categories.SIG_USER_GROUP_CHANGE.connect(self.core.SwitchCategories)

        # Variables Section
        self.variables = QtWidgets.QWidget()
        self.variables_layout = QtWidgets.QVBoxLayout(self)
        self.variables_layout.setContentsMargins(0, 0, 0, 0)
        self.variables_layout.setSpacing(0)
        self.variables.setLayout(self.variables_layout)
        self.variables_title = QtWidgets.QLabel(self)
        self.variables_title.setText("Variables")
        self.variables_title.setObjectName("h1")

        self.variables_table = VariablesTable(self)
        self.variables_table.SIG_USER_UPDATE.connect(self.SIG_USER_UPDATE.emit)

        self.variables_toolbar = QtWidgets.QToolBar()
        self.variables_toolbar.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.variables_toolbar.setObjectName("horizontal")
        self.variables_toolbar.addAction(
            QtGui.QIcon(QtGui.QPixmap("EditorContent:Icons/Plus.png")),
            "Add Variable",
            self.variables_table.AddVariable
        )

        self.variables_toolbar.addAction(
            QtGui.QIcon(QtGui.QPixmap("EditorContent:Icons/Minus.png")),
            "Remove Variable",
            self.variables_table.RemoveVariable
        )

        self.variables_layout.addWidget(self.variables_title)
        self.variables_layout.addWidget(self.variables_toolbar)
        self.variables_layout.addWidget(self.variables_table)

        # Assign everything to the main widget
        self.main_layout.addWidget(self.main_resize_container)
        self.main_resize_container.addWidget(self.categories)
        self.main_resize_container.addWidget(self.variables)

        # Adjust the space allocation to favor the settings section
        self.main_resize_container.setStretchFactor(0, 0)
        self.main_resize_container.setStretchFactor(1, 1)

    def PopulateVariables(self, variables: list):
        """ Clears existing entries nad Populates the variables list based on the selected category """
        self.variables_table.setRowCount(0)

        # Populate the variables table with the provided data
        for item in variables:
            for var_name, var_data in item.items():
                self.variables_table.AddVariable(var_name, var_data['type'], var_data['value'])

class VariablesTable(QtWidgets.QTableWidget):
    SIG_USER_UPDATE = QtCore.pyqtSignal()

    # Limit what data types are allowed as some (such as Array or Event) are complex and would require
    # additional work to allow user control
    POSSIBLE_INPUT_TYPES = [
        ParameterType.String,
        ParameterType.Bool,
        ParameterType.Int,
        ParameterType.Float,
        ParameterType.Vector2,
        ParameterType.Paragraph,
        ParameterType.Color,
        ParameterType.Scene,
        ParameterType.Dialogue,
        ParameterType.Interface,
        ParameterType.Asset_Data,
        ParameterType.Asset_Font,
        ParameterType.Asset_Image,
        ParameterType.Asset_Sound
    ]

    def __init__(self, parent=None):
        super().__init__(parent)

        # We reference columns *a lot* in this script, so simplify references by storing the values
        self.icon_column = 0
        self.name_column = 1
        self.type_column = 2
        self.input_column = 3

        self.hovered_column = -1
        self.hovered_row = -1
        self.is_dragging = False

        #self.setObjectName('variables-table')
        self.setColumnCount(4)
        self.verticalHeader().hide()

        self.setHorizontalHeaderLabels(['', 'Name', 'Type', 'Value'])
        self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Interactive)
        self.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Interactive)
        self.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setHighlightSections(False)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)  # Disable the selection outline
        self.setSortingEnabled(False)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)
        self.setDefaultDropAction(QtCore.Qt.DropAction.MoveAction)
        self.setDropIndicatorShown(False)
        self.setAcceptDrops(True)

        # TODO: Investigate how to improve sizing calculations. It should be a percentage of the available space
        self.horizontalHeader().setDefaultSectionSize(self.horizontalHeader().defaultSectionSize() * 3)
        self.setColumnWidth(2, round(self.horizontalHeader().defaultSectionSize() / 2))
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked | QtWidgets.QAbstractItemView.EditTrigger.SelectedClicked)
        variables_delegate = VariablesItemDelegate(self)
        self.setItemDelegate(variables_delegate)

    def AddVariable(self, name: str = '', type_data: str = '', input_data: any = None, index: int = -1):
        """ Adds a new row, populating each column with the provided data if applicable """
        if index == -1:
            index = self.rowCount()
        self.insertRow(index)

        # Drag Item Column
        icon_item = QtWidgets.QTableWidgetItem()
        icon_item.setFlags(QtCore.Qt.ItemFlag.NoItemFlags)
        icon_item.setFlags(icon_item.flags() | QtCore.Qt.ItemFlag.ItemIsEnabled)
        icon_item.setFlags(icon_item.flags() | QtCore.Qt.ItemFlag.ItemIsDragEnabled)
        icon_item.setFlags(icon_item.flags() | QtCore.Qt.ItemFlag.ItemIsSelectable)
        icon_item.setIcon(QtGui.QIcon(QtGui.QPixmap("EditorContent:Icons/Drag.png")))
        self.setItem(index, self.icon_column, icon_item)

        # Name Column
        name_item = QtWidgets.QTableWidgetItem()
        name_item.setFlags(QtCore.Qt.ItemFlag.NoItemFlags)
        self.setItem(index, self.name_column, name_item)
        name_input = InputEntryText({})
        name_input.owning_model_item = name_item
        self.setCellWidget(index, self.name_column, name_input)
        if name:
            name_input.Set(name)
        else:
            var_names = {}
            for row_index in range(0, self.rowCount()):
                var_names[self.cellWidget(row_index, self.name_column).Get()['value']] = ''
            name_input.Set(self.DetermineNewVariableName(var_names))
        name_input.Connect()
        name_input.SIG_USER_UPDATE.connect(self.SIG_USER_UPDATE.emit)
        name_input.SIG_USER_COMMIT.connect(self.ValidateVariable)

        # Type Column
        type_item = QtWidgets.QTableWidgetItem()
        type_item.setFlags(QtCore.Qt.ItemFlag.NoItemFlags)
        self.setItem(index, self.type_column, type_item)
        type_input = ieh.Create(
            owner=self,
            name="",
            data={"type": "Dropdown", "options": [param_type.name for param_type in self.POSSIBLE_INPUT_TYPES]},
            owning_model_item=self.item(index, self.type_column),
            owning_view=self
        )[1]
        if type_data:
            type_input.Set(type_data)
        else:
            type_input.SetDefaultValue()
        type_input.SIG_USER_UPDATE.connect(self.SwitchInputType)
        self.setCellWidget(index, self.type_column, type_input)

        # Input Column
        input_item = QtWidgets.QTableWidgetItem()
        input_item.setFlags(QtCore.Qt.ItemFlag.NoItemFlags)
        self.setItem(index, self.input_column, input_item)
        self.SwitchInputType(self.item(index, self.type_column), input_data, False)  # Populate the input colum based on the active type dropdown selection
        self.resizeRowsToContents() #@TODO: Resize only the relevent row, not everything each time

    def SwitchInputType(self, table_item: QtWidgets.QTableWidgetItem, data: any = None, report: bool = True):
        """ Creates and replaces the input entry type for the provided item """
        row = self.row(table_item)
        input_entry = ieh.Create(
            owner=self,
            name="",
            data={"type": self.cellWidget(row, self.type_column).Get()['value']},
            owning_model_item=self.item(row, self.input_column),
            owning_view=self
        )[1]
        if data:
            input_entry.Set(data)
        else:
            input_entry.SetDefaultValue()

        input_entry.Connect()
        input_entry.SIG_USER_UPDATE.connect(self.SIG_USER_UPDATE.emit)
        self.setCellWidget(row, self.input_column, input_entry)

        self.resizeRowsToContents()

        if report:
            self.SIG_USER_UPDATE.emit()

    def RemoveVariable(self):
        selected_rows = self.selectedIndexes()
        if selected_rows:
            for row_index in reversed(range(0, len(selected_rows))):
                self.removeRow(selected_rows[row_index].row())

            self.SIG_USER_UPDATE.emit()

    def ValidateVariable(self, var_name_item: QtWidgets.QTableWidgetItem) -> bool:
        name = self.cellWidget(var_name_item.row(), var_name_item.column()).Get()['value']
        validation_failed = False

        # Preliminary Action: Build a dict of all var names for quick lookups
        var_names = {}
        for row_index in range(0, self.rowCount()):
            if row_index == var_name_item.row():
                # Exempt the row that was edited
                continue

            var_names[self.cellWidget(row_index, self.name_column).Get()['value']] = ''

        # Check 1 - Variable Name can't be blank
        if not name:
            QtWidgets.QMessageBox.about(
                self,
                "Invalid Variable Name",
                "Variables are required to have a name. Please specify a name for all variables and try again."
            )

            validation_failed = True

        # Check 2 - Variable Name must be unique
        else:
            if name in var_names:
                QtWidgets.QMessageBox.about(
                    self,
                    "Invalid Variable Name",
                    f"Variable Name '{name}' already exists. Please ensure all variables have a unique name and try again."
                )

                validation_failed = True

        if validation_failed:
            # Reset the name to a generic one in case we can't prevent any destructive action that invokes this
            input_entry = self.cellWidget(var_name_item.row(), var_name_item.column())
            input_entry.Set(self.DetermineNewVariableName(var_names))
            return False
        else:
            # All checks have passed
            return True

    def DetermineNewVariableName(self, var_names: dict) -> str:
        """ Given a dict of all variable names, generate a name with a unique identifier and return it """
        iter = 0
        stop_checking = False
        fallback_name = f"New_Variable_{iter}"
        while not stop_checking:
            if fallback_name not in var_names:
                stop_checking = True
            else:
                iter += 1
                fallback_name = f"New_Variable_{iter}"

        return fallback_name

    def startDrag(self, supportedActions: QtCore.Qt.DropAction) -> None:
        if supportedActions.MoveAction:
            new_drag = QtGui.QDrag(self)
            drag_img_obj = QtWidgets.QLabel("Drag row to")
            drag_img_obj.setObjectName("drag-source")
            drag_image = QtGui.QPixmap(drag_img_obj.size())
            drag_img_obj.render(drag_image)
            new_drag.setPixmap(drag_image)
            row_items = [
                self.item(self.selectedIndexes()[0].row(), 1),  # Name
                self.item(self.selectedIndexes()[0].row(), 2),  # Type
                self.item(self.selectedIndexes()[0].row(), 3),  # input
            ]

            new_drag.setMimeData(self.mimeData(row_items))
            new_drag.exec(supportedActions)
        else:
            super().startDrag(supportedActions)

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        # Since we only support internal moves, we don't need to deal with mimeData decoding, and can act on
        # the current state of the model / view
        row_to_move = self.selectedIndexes()[0].row()
        target_dest = self.indexAt(event.position().toPoint()).row()

        # Cell widgets are exclusively owned the by the view, and any attempt to move them to another row (usually
        # through removing them from their prior locations) results if them being destroyed. Since we can't prevent
        # this, we need to pull their data to pass along to the new widgets
        name = self.cellWidget(row_to_move, 1).Get()['value']
        type_data = self.cellWidget(row_to_move, 2).Get()['value']
        input_data = self.cellWidget(row_to_move, 3).Get()['value']

        # Remove the old item, destroyed its widget contents
        self.removeRow(row_to_move)

        # Add the new item
        self.AddVariable(name, type_data, input_data, target_dest)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        index = self.indexAt(event.pos())
        if index.row() != self.hovered_row or index.column() != self.hovered_column:
            self.hovered_row = index.row()

            # Only the first column can be hovered
            if index.column() == 0:
                self.hovered_column = index.column()
            else:
                self.hovered_column = -1

            self.viewport().update()

    def leaveEvent(self, a0):
        super().leaveEvent(a0)
        self.hovered_row = -1
        self.hovered_column = -1


class VariablesItemDelegate(QtWidgets.QStyledItemDelegate):
    """ A custom item delegate that enables certain highlight characteristics """
    def __init__(self, table_parent: VariablesTable):
        super().__init__()

        self.table_parent = table_parent

    def paint(self, painter, option, index):
        if not index.isValid():
            return

        if index.column() == 0 and self.table_parent.hovered_column == 0:
            selected_row = -1
            if self.table_parent.selectedIndexes():
                selected_row = self.table_parent.selectedIndexes()[0].row()

            if index.row() == selected_row:
                option.state |= QtWidgets.QStyle.StateFlag.State_Enabled  # Allow the following updates
                option.state |= QtWidgets.QStyle.StateFlag.State_Selected

            elif index.row() == self.table_parent.hovered_row:
                option.state |= QtWidgets.QStyle.StateFlag.State_Enabled  # Allow the following updates
                option.state |= QtWidgets.QStyle.StateFlag.State_MouseOver  # Show

        super().paint(painter, option, index)
