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
from HBEditor.Core.Primitives.input_entries import InputEntryText, InputEntryDropdown
from HBEditor.Core.Primitives import input_entry_handler as ieh
from HBEditor.Core import settings


class VariableNameUndefined(Exception):
    pass


class VariableAlreadyExists(Exception):
    pass


class EditorVariablesUI(EditorBaseUI):
    def __init__(self, core_ref):
        super().__init__(core_ref)

        # Build the core editor layout object
        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Create the toolbar
        self.main_toolbar = QtWidgets.QToolBar()
        self.main_toolbar.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.main_toolbar.setObjectName("vertical")
        self.main_layout.addWidget(self.main_toolbar)

        # Main Table
        self.variables_table = VariablesTable(self)
        self.variables_table.SIG_USER_UPDATE.connect(self.SIG_USER_UPDATE.emit)
        self.main_layout.addWidget(self.variables_table)

        # Instead of having wrapper functions for modifying the table, I moved those inside the table itself.
        # As such, the buttons can be configured to point to the table functions directly
        # Toolbar - Add Button
        self.main_toolbar.addAction(
            QtGui.QIcon(QtGui.QPixmap("EditorContent:Icons/Plus.png")),
            "Add Variable",
            self.variables_table.AddValue
        )

        # Toolbar - Remove Button
        self.main_toolbar.addAction(
            QtGui.QIcon(QtGui.QPixmap("EditorContent:Icons/Minus.png")),
            "Remove Value",
            self.variables_table.RemoveValue
        )

    def AddValue(self, name: str = '', type_data: str = '', input_data: any = None):
        self.variables_table.AddValue(name, type_data, input_data)

    def RemoveValue(self):
        self.variables_table.RemoveValue()

    def GetData(self) -> dict:
        """ Returns a dict of {'var_name': {'type: <var_type>, 'value': 'var_data'}} """
        variables = {}
        for row_index in range(0, self.variables_table.rowCount()):
            var_name = self.variables_table.cellWidget(row_index, self.variables_table.name_column).Get()['value']
            var_type = self.variables_table.cellWidget(row_index, self.variables_table.type_column).Get()['value']
            var_input = self.variables_table.cellWidget(row_index, self.variables_table.input_column).Get()['value']

            if not var_name:
                raise VariableNameUndefined()
            elif var_name in variables:
                raise VariableAlreadyExists()
            else:
                variables[var_name] = {'type': var_type, 'value': var_input}

        return variables


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
        ParameterType.Asset_Scene,
        ParameterType.Asset_Dialogue,
        ParameterType.Asset_Data,
        ParameterType.Asset_Interface,
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

        self.hovered_column = -1 # TEST
        self.hovered_row = -1 # TEST
        self.is_dragging = False

        self.setObjectName('variables-table')
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
        self.itemEntered.connect(self.SetHoveredRow)

        # TODO: Investigate how to improve sizing calculations. It should be a percentage of the available space
        self.horizontalHeader().setDefaultSectionSize(self.horizontalHeader().defaultSectionSize() * 3)
        self.setColumnWidth(2, round(self.horizontalHeader().defaultSectionSize() / 2))
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked | QtWidgets.QAbstractItemView.EditTrigger.SelectedClicked)
        values_delegate = ValuesItemDelegate(self)
        self.setItemDelegate(values_delegate)

    def AddValue(self, name: str = '', type_data: str = '', input_data: any = None, index: int = -1):
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
        if name:
            name_input.Set(name)
        else:
            name_input.SetDefaultValue()
        self.setCellWidget(index, self.name_column, name_input)
        name_input.Connect()
        name_input.SIG_USER_UPDATE.connect(self.SIG_USER_UPDATE.emit)

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
        self.SwitchInputType(self.item(index, self.type_column), input_data)  # Populate the input colum based on the active type dropdown selection

        self.resizeRowsToContents() #@TODO: Resize only the relevent row, not everything each time
        self.SIG_USER_UPDATE.emit()

    def SwitchInputType(self, table_item: QtWidgets.QTableWidgetItem, data: any = None):
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
        self.SIG_USER_UPDATE.emit()

    def RemoveValue(self):
        selected_rows = self.selectedIndexes()
        if selected_rows:
            for row_index in reversed(range(0, len(selected_rows))):
                self.removeRow(selected_rows[row_index].row())

            self.SIG_USER_UPDATE.emit()

    def SetHoveredRow(self, item):
        self.hovered_column = item.column()
        self.hovered_row = item.row()
        self.viewport().update()

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
        self.AddValue(name, type_data, input_data, target_dest)


class ValuesItemDelegate(QtWidgets.QStyledItemDelegate):
    """ A custom item delegate that enforces unique 'Name' column values """
    def __init__(self, table_parent: VariablesTable):
        super().__init__()

        self.table_parent = table_parent

    def paint(self, painter, option, index):
        if not index.isValid():
            return

        if self.table_parent.hovered_column == 0:
            if index.row() == self.table_parent.hovered_row:
                option.state |= QtWidgets.QStyle.StateFlag.State_Enabled  # Allow the following updates
                option.state |= QtWidgets.QStyle.StateFlag.State_MouseOver  # Show

        # Disable selection visual state, otherwise the drag icons could be selected
        # which would look strange (This can't be controlled per-cell in CSS)
        option.state &= ~QtWidgets.QStyle.StateFlag.State_Selected

        super().paint(painter, option, index)
