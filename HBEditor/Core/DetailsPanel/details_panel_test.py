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
from HBEditor.Core.Primitives.input_entries import *
from HBEditor.Core.Primitives import input_entry_model_handler as iemh


class DetailsPanel(QtWidgets.QWidget):
    def __init__(self, excluded_entries: list = None):
        super().__init__()

        self.active_entry = None

        # Allow the filtering of what properties can possibly appear
        self.excluded_entries = excluded_entries

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
        #@TODO: Investigate implementing 'dataChanged' signal so the Array entry can bubble up a refresh call
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
        """ Fill out the details tree based on the active entry's action data"""
        if selected_entry is not self.active_entry:
            self.StoreData()
        self.active_entry = selected_entry

        self.Clear()
        self.AddItems(self.active_entry.action_data["requirements"])

        self.details_tree.expandAll()

    def AddItems(self, data, parent=None):
        """ Recursively adds an InputEntry element into the details tree, including all of its children"""
        for requirement in data:
            entry = iemh.Add(
                owner=self,
                view=self.details_tree,
                data=requirement,
                parent=parent,
                excluded_entries=self.excluded_entries,
                signal_func=self.ConnectSignals,
                refresh_func=self.UserUpdatedInputWidget
            )

            if "children" in requirement:
                #if "template" in requirement:
                    # Anything that use templates handle creating their own children, as they instantiate the template
                    #for child_data in requirement["children"]:
                        #self.details_tree.itemWidget(entry, 1).AddItems(child_data)

                self.AddItems(requirement["children"], entry)

    def ConnectSignals(self, tree_item):
        input_widget = self.details_tree.itemWidget(tree_item, 1)
        input_widget.SIG_USER_UPDATE.connect(self.UserUpdatedInputWidget)

        global_checkbox = self.details_tree.itemWidget(tree_item, 2)
        if global_checkbox:
            global_checkbox.SIG_USER_UPDATE.connect(self.UserClickedGlobalCheckbox)

    def StoreData(self, parent: QtWidgets.QTreeWidgetItem=None, initial_iter: bool=True) -> list:
        """
        Retrieves the values from all items in the details tree, and updates the active entry using the
        collected data
        """
        if self.active_entry:
            data_to_store = []

            if not parent:
                parent = self.details_tree.invisibleRootItem()

            for entry_index in range(0, parent.childCount()):
                entry = parent.child(entry_index)
                entry_data = self.details_tree.itemWidget(entry, 1).Get()

                global_checkbox = self.details_tree.itemWidget(entry, 2)
                if global_checkbox:
                    entry_data["global"]["active"] = global_checkbox.Get()

                if entry.childCount() > 0:
                    entry_data["children"] = self.StoreData(entry, False)

                data_to_store.append(entry_data)

            if initial_iter:
                self.active_entry.action_data["requirements"] = data_to_store

            return data_to_store

    def Clear(self):
        self.details_tree.clear()

    ### Slots ###

    def UserClickedGlobalCheckbox(self, owning_tree_item: QtWidgets.QTreeWidgetItem, global_active: bool):
        input_widget = self.details_tree.itemWidget(owning_tree_item, 1)
        if global_active:
            input_widget.SetEditable(2)
        else:
            input_widget.SetEditable(0)

    def UserUpdatedInputWidget(self, owning_tree_item: QtWidgets.QTreeWidgetItem):
        #@TODO: Change to only store / refresh the item that changed, not the whole tree
        if self.active_entry:
            self.StoreData()
            self.active_entry.Refresh()
