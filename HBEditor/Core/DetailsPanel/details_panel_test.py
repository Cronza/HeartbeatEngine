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
from PyQt5 import QtWidgets, QtCore
from HBEditor.Core.settings import Settings
from HBEditor.Core.Primitives.input_entries import *
from HBEditor.Core.Primitives.input_entry_updater import EntryUpdater
from HBEditor.Core.DataTypes.parameter_types import ParameterType
from HBEditor.Core.Primitives.simple_checkbox import SimpleCheckbox
from HBEditor.Core.Primitives import input_entry_model_handler as iemh


class DetailsPanel(QtWidgets.QWidget):
    def __init__(self, excluded_properties: list = None):
        super().__init__()

        self.active_entry = None

        # Allow the filtering of what properties can possibly appear
        self.excluded_properties = excluded_properties

        self.details_layout = QtWidgets.QVBoxLayout(self)
        self.details_layout.setContentsMargins(0, 0, 0, 0)
        self.details_layout.setSpacing(0)

        # Create title
        self.details_title = QtWidgets.QLabel(self)
        self.details_title.setObjectName("h1")
        self.details_title.setText("Details")

        # Create the toolbar
        #self.details_toolbar = QtWidgets.QToolBar(self)

        # Create search filter
        #self.details_filter = QtWidgets.QLineEdit(self.details_toolbar)
        #self.details_filter.setPlaceholderText("filter...")
        #self.details_toolbar.addWidget(self.details_filter)

        # Create Details List
        self.details_tree = QtWidgets.QTreeWidget(self)
        self.details_tree.setColumnCount(3)
        self.details_tree.setHeaderLabels(['Name', 'Input', 'G'])
        self.details_tree.setAutoScroll(False)
        self.details_tree.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.details_tree.header().setStretchLastSection(False)  # Disable to allow custom sizing
        self.details_tree.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Interactive)
        self.details_tree.header().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.details_tree.header().setSectionResizeMode(2, QtWidgets.QHeaderView.Fixed)
        self.details_tree.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        # --- Specialized Settings for the 'G' column ---
        # 1. Allow columns to be significantly smaller than normal
        self.details_tree.header().setMinimumSectionSize(round(self.details_tree.header().width() / 4))

        # 2. Force the last column to be barely larger than a standard checkbox
        self.details_tree.setColumnWidth(2, round(self.details_tree.header().width() / 5))

        # 3. Align the column header text to match the alignment of the checkbox
        self.details_tree.headerItem().setTextAlignment(2, QtCore.Qt.AlignCenter)

        # ********** Add All Major Pieces to details layout **********
        self.details_layout.addWidget(self.details_title)
        #self.details_layout.addWidget(self.details_toolbar)
        self.details_layout.addWidget(self.details_tree)

    def Populate(self, selected_entry):
        print("Populating...")
        if selected_entry is not self.active_entry:
            print("Current details do not match the active entry - We should refresh")
        self.active_entry = selected_entry

        iemh.Clear(self.details_tree)

        action_data = self.active_entry.action_data
        if "requirements" in action_data:
            for requirement in action_data['requirements']:
                entry = iemh.Add(
                     owner=self,
                     tree=self.details_tree,
                     data=requirement,
                     excluded_entries=self.excluded_properties
                )
                self.ConnectSignals(entry)

                if "children" in requirement and entry:
                    for child_requirement in requirement["children"]:
                        child_entry = iemh.Add(
                            owner=self,
                            tree=self.details_tree,
                            data=child_requirement,
                            parent=entry,
                            excluded_entries=self.excluded_properties
                        )
                        self.ConnectSignals(child_entry)

        # Expand all dropdowns automatically
        self.details_tree.expandAll()
        pass

    def ConnectSignals(self, tree_item):
        input_widget = self.details_tree.itemWidget(tree_item, 1)
        input_widget.SIG_USER_UPDATE.connect(self.UserUpdatedInputWidget)

        global_checkbox = self.details_tree.itemWidget(tree_item, 2)
        if global_checkbox:
            global_checkbox.SIG_USER_UPDATE.connect(self.UserClickedGlobalCheckbox)

    def CollectData(self):
        pass

    def AssignData(self):
        pass

    def StoreData(self):
        pass

    ### Slots ###

    def UserClickedGlobalCheckbox(self, owning_tree_item: QtWidgets.QTreeWidgetItem, global_active: bool):
        input_widget = self.details_tree.itemWidget(owning_tree_item, 1)
        if global_active:
            input_widget.SetEditable(2)
        else:
            input_widget.SetEditable(0)

    def UserUpdatedInputWidget(self, owning_tree_item: QtWidgets.QTreeWidgetItem):
        print("Input widget updated")

        if self.active_entry:
            # First, update the active entry with the current contents of the tree
            #self.UpdateCache()

            # Inform the active entry to refresh
            self.active_entry.Refresh()


    #def Request

