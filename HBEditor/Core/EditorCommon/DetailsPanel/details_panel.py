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
from HBEditor.Core.EditorUtilities import action_data as ad
from HBEditor.Core.Primitives import input_entry_handler as ieh


class DetailsPanel(QtWidgets.QWidget):
    """
    A TreeView for input widgets designed for displaying the 'ACTION_DATA' of actions

    Attributes
        SIG_USER_UPDATE: - Signal that fires whenever something was modified by the user in this panel
    """
    SIG_USER_UPDATE = QtCore.pyqtSignal()

    def __init__(self, excluded_properties: list = None):
        super().__init__()

        self.active_entry = None

        # Allow the filtering of what properties can possibly appear
        self.excluded_properties = excluded_properties

        self.details_layout = QtWidgets.QVBoxLayout(self)
        self.details_layout.setContentsMargins(0, 0, 0, 0)
        self.details_layout.setSpacing(0)

        # Create the toolbar
        #self.details_toolbar = QtWidgets.QToolBar(self)

        # Create search filter
        #self.details_filter = QtWidgets.QLineEdit(self.details_toolbar)
        #self.details_filter.setPlaceholderText("filter...")
        #self.details_toolbar.addWidget(self.details_filter)

        # Create Details List
        #@TODO: Investigate implementing 'dataChanged' signal so the Array entry can bubble up a refresh call
        self.details_tree = QtWidgets.QTreeWidget(self)
        self.details_tree.setObjectName("no-top")
        self.details_tree.setColumnCount(3)
        self.details_tree.setHeaderLabels(['Name', 'Input', 'C'])
        self.details_tree.setAutoScroll(False)
        self.details_tree.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.details_tree.header().setStretchLastSection(False)  # Disable to allow custom sizing
        self.details_tree.header().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Interactive)
        self.details_tree.header().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.details_tree.header().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.details_tree.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.details_tree.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # --- Specialized Settings for the 'C' column ---
        # 1. Allow columns to be significantly smaller than normal
        self.details_tree.header().setMinimumSectionSize(round(self.details_tree.header().width() / 4))

        # 2. Force the last column to be barely larger than a standard checkbox
        self.details_tree.setColumnWidth(2, round(self.details_tree.header().width() / 5))

        # 3. Align the column header text to match the alignment of the checkbox
        self.details_tree.headerItem().setTextAlignment(2, QtCore.Qt.AlignmentFlag.AlignCenter)

        # ********** Add All Major Pieces to details layout **********
        self.details_layout.addWidget(self.details_tree)

    def Populate(self, selected_entry):
        """
        Fill out the details tree based on the active entry's action data. If the provided item is the same as
        'active_entry', don't do anything
        """
        if selected_entry is not self.active_entry:
            self.StoreData()
            self.active_entry = selected_entry

        self.Clear()

        # Recursively create an entry for all parameters within the action_data
        # Note: This provides data to each by reference, so any changes made to data stored in each details entry
        # propagates directly back to the main entry
        self.AddItems(
            action_data=self.active_entry.action_data,
            excluded_properties=self.excluded_properties
        )

        self.details_tree.expandAll()

    def AddItems(self, action_data: dict, parent=None, excluded_properties: list = None):
        """
        Recursively adds an InputEntry element into the details tree, including all of its children, for each action
        data dict item provided
        """
        for name, data in action_data.items():
            if "flags" in data:
                # Some reqs are strictly meant to use defaults or globals, and not be edited by the user. In these
                # circumstances,  don't display them
                if "editable" not in data["flags"]:
                    continue

                # Some editors exclude certain requirements (IE. Scenes don't make use of 'post_wait'). Don't
                # generate entries for any excluded property. Make an exception if the 'no_exclusion' flag is used
                elif excluded_properties:
                    if name in excluded_properties:
                        if "no_exclusion" not in data["flags"]:
                            continue
            else:
                continue

            entry = ieh.Add(
                owner=self,
                view=self.details_tree,
                name=name,
                data=data,
                parent=parent,
                excluded_properties=excluded_properties,
                signal_func=self.ConnectSignals
            )

            if "children" in data:
                # If an entry includes the 'no_exclusion' flag, then
                # ignore this exclusion list for all child properties
                if "no_exclusion" in data["flags"]:
                    self.AddItems(data["children"], entry)
                else:
                    self.AddItems(data["children"], entry, excluded_properties)

    def ConnectSignals(self, tree_item):
        """ Connects the InputEntry signals to slots within this class """
        input_widget = self.details_tree.itemWidget(tree_item, 1)
        input_widget.SIG_USER_UPDATE.connect(self.UserUpdatedInputWidget)

        #global_checkbox = self.details_tree.itemWidget(tree_item, 2)
        #if global_checkbox:
        #    global_checkbox.SIG_USER_UPDATE.connect(self.UserClickedGlobalCheckbox)

    def StoreData(self, parent: QtWidgets.QTreeWidgetItem = None) -> dict:
        """
        Retrieves the values from all items in the details tree, and updates the active entry using the
        collected data
        """
        if self.active_entry:
            data_to_store = {}

            if not parent:
                parent = self.details_tree.invisibleRootItem()

            for entry_index in range(0, parent.childCount()):
                # Each entry is assigned data by reference to the original entry. Any changes we make will propagate
                # directly back to that entry
                entry = parent.child(entry_index)
                entry_name = self.details_tree.itemWidget(entry, 0).text()
                entry_data = self.details_tree.itemWidget(entry, 1).Get()
                if "global" in entry_data and "flags" in entry_data:
                    ad.RemoveFlag("global_active", entry_data)

                    global_checkbox = self.details_tree.itemWidget(entry, 2)
                    if global_checkbox.Get():
                        ad.AddFlag("global_active", entry_data)

                if entry_data["type"] == "Array":
                    # Arrays allow the user to remove their children, which can lead to a desync in the displayed child
                    # entries and the entries recorded in the action_data for the active entry. This issue exists as the
                    # data stored in the active_entry is the full clone from the ACTION_DATA, containing all
                    # parameters whether they're displayed in the editor or not. Since we only generate details
                    # entries for requirements that are displayed, this means we'd never store the data for any entries
                    # not visible
                    #
                    # If we forcefully update 'children', we'd stomp the hidden requirements. To avoid this, we use
                    # '.update' which applies changes to keys that already exist. However, since arrays remove data,
                    # the .update call won't remove the data that we deleted, thus leaving it perpetually there until
                    # the keys are overriden
                    #
                    # To avoid this, we take the unfortunate route of regenerating the entire stored data block from the
                    # template each time, removing any stagnant data, and updating it with the changes from the
                    # displayed entries

                    entry_data["children"] = {}
                    for child_index in range(0, entry.childCount()):
                        # Get the underlying element dict without the top-most key (It's usually replaced by a generated
                        # one)
                        # Since array elements use generated key names, the top-most key name of the template needs to
                        # be changed to match. However, we can't infer or deduce what names to use, so we'll fetch it
                        # directly from the child entries
                        child_entry = entry.child(child_index)
                        child_entry_name = self.details_tree.itemWidget(child_entry, 0).text()

                        # Stomp the stored data with a copy of the template updated with the generated name
                        template_copy = copy.deepcopy(entry_data["template"])
                        entry_data["children"][child_entry_name] = template_copy[ad.GetActionName(template_copy)]

                    # Update the children as usual now that the stagnant data has been removed
                    entry_data["children"].update(self.StoreData(entry))

                elif entry.childCount() > 0:

                    # We do an update here as not all items within the action_data were displayed (uneditable details
                    # aren't added). If we were to do a stomp using '=' instead, it'd erase the action data for these
                    entry_data["children"].update(self.StoreData(entry))

                data_to_store[entry_name] = entry_data

            return data_to_store

    def ClearActiveItem(self):
        """ Removes the active_item, storing any data currently in the panel within it before wiping the panel """
        self.StoreData()
        self.Clear()
        self.active_entry = None

    def Clear(self):
        self.details_tree.clear()

    ### Slots ###

    def UserClickedGlobalCheckbox(self, owning_tree_item: QtWidgets.QTreeWidgetItem, global_active: bool):
        input_widget = self.details_tree.itemWidget(owning_tree_item, 1)
        if global_active:
            input_widget.SetEditable(2)
        else:
            input_widget.SetEditable(0)

        self.SIG_USER_UPDATE.emit()

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
            self.SIG_USER_UPDATE.emit()
