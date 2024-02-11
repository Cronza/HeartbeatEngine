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


class EditorValuesUI(EditorBaseUI):
    def __init__(self, core_ref):
        super().__init__(core_ref)

        # Limit what editing types are usable as some (such as Array or Event) are complex and would require
        # additional work to allow user control
        self.possible_input_types = [
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

        # Build the core editor layout object
        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Create the toolbar
        self.main_toolbar = QtWidgets.QToolBar()
        self.main_toolbar.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.main_toolbar.setObjectName("vertical")
        self.main_layout.addWidget(self.main_toolbar)

        # Add Button
        self.main_toolbar.addAction(
            QtGui.QIcon(QtGui.QPixmap("EditorContent:Icons/Plus.png")),
            "Add Value",
            self.AddValue
        )

        # Remove Button
        self.main_toolbar.addAction(
            QtGui.QIcon(QtGui.QPixmap("EditorContent:Icons/Minus.png")),
            "Remove Value",
            self.RemoveValue
        )

        # Main Table
        self.values_table = QtWidgets.QTableWidget(self)
        self.values_table.setObjectName('values-table')
        self.values_table.setColumnCount(3)
        self.values_table.verticalHeader().hide()
        self.values_table.setHorizontalHeaderLabels(['Type', 'Name', 'Value'])
        self.values_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Interactive)
        self.values_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Interactive)
        self.values_table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.values_table.setAlternatingRowColors(True)
        self.values_table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.values_table.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)  # Disable the selection outline
        self.values_table.setSortingEnabled(True)

        # TODO: Investigate how to improve sizing calculations. It should be a percentage of the available space
        self.values_table.horizontalHeader().setDefaultSectionSize(self.values_table.horizontalHeader().defaultSectionSize() * 3)
        self.values_table.setColumnWidth(0, round(self.values_table.horizontalHeader().defaultSectionSize() / 2))

        self.values_table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked | QtWidgets.QAbstractItemView.EditTrigger.SelectedClicked)
        values_delegate = ValuesItemDelegate(self)
        self.values_table.setItemDelegate(values_delegate)
        self.values_table.itemChanged.connect(lambda: self.SIG_USER_UPDATE.emit())
        self.main_layout.addWidget(self.values_table)

    def AddValue(self, data: tuple = None):
        self.values_table.insertRow(self.values_table.rowCount())

        # Populate the row with items
        self.values_table.setItem(self.values_table.rowCount() - 1, 0, QtWidgets.QTableWidgetItem())
        self.values_table.setItem(self.values_table.rowCount() - 1, 1, QtWidgets.QTableWidgetItem())
        self.values_table.setItem(self.values_table.rowCount() - 1, 2, QtWidgets.QTableWidgetItem())

        # Add the type dropdown
        #type_input = InputEntryDropdown({"options": [param_type.name for param_type in self.possible_input_types]})
        type_input = ieh.Create(
            owner=self,
            name="",
            data={"type": "Dropdown", "options": [param_type.name for param_type in self.possible_input_types]},
            owning_model_item=self.values_table.item(self.values_table.rowCount() - 1, 2),
            owning_view=self.values_table
        )[1]
        type_input.SIG_USER_UPDATE.connect(self.SwitchInputType)
        self.values_table.setCellWidget(self.values_table.rowCount() - 1, 0, type_input)
        self.SwitchInputType(self.values_table.item(self.values_table.rowCount() - 1, 0))

        # Load data if provided
        if data:
            row = self.values_table.rowCount() - 1
            self.values_table.item(row, 0).setData(0, data[0])
            self.values_table.item(row, 1).setData(0, data[1])
            self.values_table.item(row, 2).setData(0, data[2])

        self.values_table.resizeRowsToContents()
        self.SIG_USER_UPDATE.emit()

    def SwitchInputType(self, table_item: QtWidgets.QTableWidgetItem):
        """ Creates and replaces the input entry type for the provided item s"""
        row = self.values_table.row(table_item)
        input_entry = ieh.Create(
            owner=self,
            name="",
            data={"type": self.values_table.cellWidget(row, 0).Get()['value']},
            owning_model_item=self.values_table.item(row, 2),
            owning_view=self.values_table
        )[1]
        self.values_table.setCellWidget(row, 2, input_entry)

    def RemoveValue(self):
        selected_rows = self.values_table.selectedIndexes()
        if selected_rows:
            for row_index in reversed(range(0, len(selected_rows))):
                self.values_table.removeRow(selected_rows[row_index].row())

            self.SIG_USER_UPDATE.emit()

    def GetData(self) -> dict:
        """ Returns a dict of {'value_name': 'value_data'} """
        values = {}
        for row_index in range(0, self.values_table.rowCount()):
            # Only the name is mandatory. While having unset data will likely lead to runtime issues, it's still allowed
            val_name = self.values_table.item(row_index, 0).data(0)
            val_data = self.values_table.item(row_index, 1).data(0)

            values[val_name] = val_data
        return values


class ValuesItemDelegate(QtWidgets.QStyledItemDelegate):
    """ A custom item delegate that enforces unique 'Name' column values """

    def setModelData(self, editor: QtWidgets.QWidget, model: QtCore.QAbstractItemModel, index: QtCore.QModelIndex) -> None:
        if index.column() == 0:
            edited_row_index = index.row()
            new_data = editor.text()

            # Validate the data for uniqueness before we commit it. If a problem is found, reject and revert the change
            for row_index in range(0, model.rowCount()):
                if row_index != edited_row_index:
                    row_data = model.data(model.index(row_index, 0))

                    if row_data == new_data and (row_data != "" and new_data != ""):
                        QtWidgets.QMessageBox.about(
                            self.parent(),
                            "Value already exists",
                            "A value already exists with that name. Please choose another name and try again.\n"
                        )

                        # Modify the editor to use the unedited data
                        editor.setText(model.data(index))
                        super().setModelData(editor, model, index)

                        return

            # Validation completed without issue! Commit the change
            super().setModelData(editor, model, index)
            return
        else:
            # No validation applied. Commit the change
            super().setModelData(editor, model, index)
            return
