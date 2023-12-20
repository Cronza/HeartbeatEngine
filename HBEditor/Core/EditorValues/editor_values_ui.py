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
from HBEditor.Core.base_editor_ui import EditorBaseUI
from HBEditor.Core.Primitives.input_entries import InputEntryText
from HBEditor.Core.Primitives import input_entry_handler as ieh


class EditorValuesUI(EditorBaseUI):
    def __init__(self, core_ref):
        super().__init__(core_ref)

        # Build the core editor layout object
        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Create the toolbar
        self.main_toolbar = QtWidgets.QToolBar()
        self.main_toolbar.setOrientation(QtCore.Qt.Vertical)
        self.main_toolbar.setObjectName("vertical")
        self.main_layout.addWidget(self.main_toolbar)

        # Add Button
        self.main_toolbar.addAction(
            QtGui.QIcon(QtGui.QPixmap(":/Icons/Plus.png")),
            "Add Value",
            self.AddValue
        )

        # Remove Button
        self.main_toolbar.addAction(
            QtGui.QIcon(QtGui.QPixmap(":/Icons/Minus.png")),
            "Remove Value",
            self.RemoveValue
        )

        # Main Table
        self.values_table = QtWidgets.QTableWidget(self)
        self.values_table.setObjectName('values-table')
        self.values_table.setColumnCount(2)
        self.values_table.verticalHeader().hide()
        self.values_table.setHorizontalHeaderLabels(['Name', 'Value'])
        self.values_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Interactive)
        self.values_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.values_table.setAlternatingRowColors(True)
        self.values_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.values_table.setFocusPolicy(QtCore.Qt.NoFocus)  # Disable the selection outline
        self.values_table.setSortingEnabled(True)
        # TODO: Investigate how to improve the sizing for the first col. It should be a percentage of the available space
        self.values_table.horizontalHeader().setDefaultSectionSize(self.values_table.horizontalHeader().defaultSectionSize() * 3)
        self.main_layout.addWidget(self.values_table)

    def AddValue(self):
        self.values_table.insertRow(self.values_table.rowCount())
        self.values_table.resizeRowsToContents()

    def RemoveValue(self):
        selected_rows = self.values_table.selectedIndexes()
        for row_index in reversed(range(0, len(selected_rows))):
            self.values_table.removeRow(selected_rows[row_index].row())

    def UserUpdatedInputWidget(self, owning_tree_item: QtWidgets.QTreeWidgetItem):
        self.SIG_USER_UPDATE.emit()
