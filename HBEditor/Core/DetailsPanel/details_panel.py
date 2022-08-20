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
from HBEditor.Core.EditorUtilities import action_data_handler as adh


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
        self.details_layout.addWidget(self.details_tree)

    def Populate(self, selected_entry):
        """ Fill out the details tree based on the active entry's action data """
        if selected_entry is not self.active_entry:
            self.StoreData()
        self.active_entry = selected_entry

        self.Clear()
        self.AddItems(adh.GetActionRequirements(self.active_entry.action_data))

        self.details_tree.expandAll()

    def AddItems(self, req_data: dict, parent=None):
        """
        Recursively adds an InputEntry element into the details tree, including all of its children, for each action
        data dict item provided
        """
        for name, data in req_data.items():
            # Some reqs are strictly meant to use defaults or globals, and not be edited by the user. In these
            # circumstances,  don't display them
            if "editable" in data:
                if not data["editable"]:
                    continue

            # Some editors exclude certain requirements (IE. Point & Click doesn't make use ot 'post_wait')
            elif self.excluded_properties:
                if name in self.excluded_properties:
                    continue

            entry = iemh.Add(
                owner=self,
                view=self.details_tree,
                name=name,
                data=data,
                parent=parent,
                excluded_properties=self.excluded_properties,
                signal_func=self.ConnectSignals,
                refresh_func=self.UserUpdatedInputWidget
            )

            if "children" in data:
                self.AddItems(data["children"], entry)

    def ConnectSignals(self, tree_item):
        """ Connects the InputEntry signals to slots within this class """
        input_widget = self.details_tree.itemWidget(tree_item, 1)
        input_widget.SIG_USER_UPDATE.connect(self.UserUpdatedInputWidget)

        global_checkbox = self.details_tree.itemWidget(tree_item, 2)
        if global_checkbox:
            global_checkbox.SIG_USER_UPDATE.connect(self.UserClickedGlobalCheckbox)

    def StoreData(self, parent: QtWidgets.QTreeWidgetItem = None, initial_iter: bool = True) -> list:
        """
        Retrieves the values from all items in the details tree, and updates the active entry using the
        collected data
        """
        if self.active_entry:
            data_to_store = {}

            if not parent:
                parent = self.details_tree.invisibleRootItem()

            for entry_index in range(0, parent.childCount()):
                entry = parent.child(entry_index)
                entry_name = self.details_tree.itemWidget(entry, 0).text()
                entry_data = self.details_tree.itemWidget(entry, 1).Get()

                if "global" in entry_data:
                    global_checkbox = self.details_tree.itemWidget(entry, 2)
                    entry_data["global_active"] = global_checkbox.Get()

                if entry.childCount() > 0:
                    entry_data["children"] = self.StoreData(entry, False)

                data_to_store[entry_name] = entry_data

            if initial_iter and data_to_store:
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
        if self.active_entry:
            self.StoreData()

            # In order to provide the context of "which" input widget was updated, we need to provide the
            # full ancestry tree so there is a direct path to the widget in question
            # IE: [transition,type]
            parent_tree = []
            cur_entry = owning_tree_item

            stop = False
            while not stop:
                parent_tree.insert(-1, self.details_tree.itemWidget(cur_entry, 0).text())  # Descending order

                cur_entry = cur_entry.parent()
                if not cur_entry:
                    stop = True

            self.active_entry.Refresh(parent_tree)
