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


# @TODO: Split this file up into a functions class & U.I class
# @TODO: Make this class agnostic to the dialogue editor


class DetailsPanel(QtWidgets.QWidget):
    def __init__(self, excluded_properties: list = None):
        super().__init__()

        # In order to save details as we switch between active dialogue entries, keep track of the last selected entry
        self.active_entry = None

        # Optional dependencies (Some input widgets might need certain references depending on the owner)
        self.branch_list = None

        # Allow the filtering of what properties can possibly appear
        self.excluded_properties = excluded_properties

        self.details_layout = QtWidgets.QVBoxLayout(self)
        self.details_layout.setContentsMargins(0, 0, 0, 0)
        self.details_layout.setSpacing(0)

        # Create title
        self.details_title = QtWidgets.QLabel(self)
        self.details_title.setFont(Settings.getInstance().header_1_font)
        self.details_title.setStyleSheet(Settings.getInstance().header_1_color)
        self.details_title.setText("Details")

        # Create the toolbar
        self.details_toolbar = QtWidgets.QFrame(self)
        self.details_toolbar.setAutoFillBackground(False)
        self.details_toolbar.setStyleSheet(
            "QFrame, QLabel, QToolTip {\n"
            "    border-radius: 4px;\n"
            f"   background-color: rgb({Settings.getInstance().toolbar_background_color});\n"
            "}"
        )
        self.details_toolbar.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.details_toolbar.setFrameShadow(QtWidgets.QFrame.Raised)
        self.details_toolbar_layout = QtWidgets.QHBoxLayout(self.details_toolbar)
        self.details_toolbar_layout.setContentsMargins(2, 2, 2, 2)
        self.details_toolbar_layout.setSpacing(0)

        # Create search filter
        self.details_filter = QtWidgets.QLineEdit(self.details_toolbar)
        self.details_filter.setPlaceholderText("filter...")
        self.details_toolbar_layout.addWidget(self.details_filter)

        # Create Empty Space Spacer
        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.details_toolbar_layout.addItem(spacer)

        # Create Details List
        self.details_tree = QtWidgets.QTreeWidget(self)
        self.details_tree.setColumnCount(3)
        self.details_tree.setHeaderLabels(['Name', 'Input', 'G'])
        self.details_tree.setAutoScroll(False)
        self.details_tree.header().setFont(Settings.getInstance().button_font)
        self.details_tree.header().setStretchLastSection(False)  # Disable to allow custom sizing
        self.details_tree.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
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
        self.details_layout.addWidget(self.details_toolbar)
        self.details_layout.addWidget(self.details_tree)

    def PopulateDetails(self, selected_entry):
        """
        Populates the details table with an entry for all relevant action_data parameters of the given entry.
        If an entry is already selected, cache the values of all detail entries in the previously selected entry,
        and load the cache from the new selection if applicable

        If this was called manually (the previously selected and the newly selected entries are the same), skip
        updating the caching and just load from the existing cache
        """

        if selected_entry is not self.active_entry:
            self.UpdateCache()

        # Clear the existing details
        self.Clear()

        # Update the active entry
        self.active_entry = selected_entry

        # Generate each entry (If there are any requirements)
        if "requirements" in self.active_entry.action_data:
            for requirement in self.active_entry.action_data['requirements']:

                if self.excluded_properties:
                    if requirement["name"] in self.excluded_properties:
                        continue

                # Create a new entry, and add it to the details list
                self.AddEntry(self.CreateEntryWidget(requirement))

        # Expand all dropdowns automatically
        self.details_tree.expandAll()

    def UpdateCache(self, parent_entry=None, action_data=None):
        """
        Collect all inputs for all detail entries, and cache them in the active entry's action data

        If 'parent_entry' and 'action_data' are provided, parse them. Otherwise, only consider
        entries at the root. Either way, recurse for any children found
        """
        if self.active_entry:
            # If we've been provided a parent (due to recursion or otherwise), target's it's children and data.
            # Otherwise, target the root entries and action data
            details_entry_parent = None
            action_data_target = None
            if parent_entry:
                details_entry_parent = parent_entry
                action_data_target = action_data
            else:
                details_entry_parent = self.details_tree.invisibleRootItem()
                if "requirements" in self.active_entry.action_data:
                    action_data_target = self.active_entry.action_data["requirements"]

            for details_entry_index in range(0, details_entry_parent.childCount()):
                details_entry = details_entry_parent.child(details_entry_index)
                details_entry_name = details_entry.name_widget.text()

                # Are there any requirements to cache?
                if action_data_target:
                    # Since the requirements list is a list, we need to parse through for specifically for the
                    # match for this entry
                    for requirement in action_data_target:
                        if requirement["name"] == details_entry_name:
                            # If this details_entry has children (IE. It's a container), recursively update the cache for
                            # any and all children entries
                            if details_entry.childCount() > 0 and "children" in requirement: #@TODO: TESTING: Please review
                                self.UpdateCache(details_entry, requirement["children"])

                            # Containers don't store values themselves, so the above code accounts solely for it's children
                            # If this entry is not a container, lets cache normally
                            else:
                                requirement["value"] = details_entry.Get()

                                # If this entry has a global option, keep track of it's value
                                if details_entry.show_global_toggle:
                                    global_value = details_entry.GetGlobal()
                                    requirement["global"]["active"] = global_value

    def CreateEntryWidget(self, data):
        """ Given an action_data dict, create a new details entry widget and return it """
        # Populate the data column with the widget appropriate to the given type
        details_widget = self.GetDetailsWidget(data)

        # Set the name (Applicable for all widget types)
        details_widget.name_widget.setText(data["name"])

        # Containers are special in that they don't hold data, so generally ignore them for certain actions
        if not data["type"] == "container":

            # Only show the global toggle if this detail has a global setting. By default, all settings with global
            # values use the global toggle
            if 'global' in data:
                details_widget.show_global_toggle = True

                # Keep the global toggle off if the user previously turned it off
                if "active" in data["global"]:
                    if data["global"]["active"]:
                        details_widget.global_toggle.Set(True)
                    else:
                        details_widget.global_toggle.Set(False)
                else:
                    details_widget.global_toggle.Set(True)

            # Update the contents of the entry
            details_widget.Set(data["value"])

            # Make the option read-only if applicable
            if not data["editable"]:
                details_widget.SetEditable(2)

        return details_widget

    def AddEntry(self, entry, parent=None):
        """
        Given a details widget, add it to the bottom of the details tree. If the details widget has any children, add
        all of them through recursion
        """
        if parent:
            parent.addChild(entry)
        else:
            self.details_tree.addTopLevelItem(entry)

        self.details_tree.setItemWidget(entry, 0, entry.name_widget)
        self.details_tree.setItemWidget(entry, 1, entry.input_container)
        if entry.show_global_toggle:
            self.details_tree.setItemWidget(entry, 2, entry.global_toggle)

        # If the entry has any children, add them all via recursion
        if entry.childCount() > 0:
            for childIndex in range(0, entry.childCount()):
                self.AddEntry(entry.child(childIndex), entry)

    def GetDetailsWidget(self, data: dict):
        """ Given an action data dict, create and return the relevant details widget """
        #@TODO: Can this be converted to use an enum?

        data_type = data['type']

        if data_type == "str":
             return InputEntryText(self.DetailEntryUpdated)
        elif data_type == "paragraph":
            return InputEntryParagraph(self.DetailEntryUpdated)
        elif data_type == "vector2":
            return InputEntryTuple(self.DetailEntryUpdated)
        elif data_type == "bool":
            return InputEntryBool(self.DetailEntryUpdated)
        elif data_type == "color":
            return InputEntryColor(self.DetailEntryUpdated)
        elif data_type == "int":
            return InputEntryInt(self.DetailEntryUpdated)
        elif data_type == "float":
            return InputEntryFloat(self.DetailEntryUpdated)
        elif data_type == "file":
            return InputEntryFileSelector(self, "", self.DetailEntryUpdated)
        elif data_type == "file_data":
            return InputEntryFileSelector(self, Settings.getInstance().supported_content_types["Data"], self.DetailEntryUpdated)
        elif data_type == "file_image":
            return InputEntryFileSelector(self, Settings.getInstance().supported_content_types["Image"], self.DetailEntryUpdated)
        elif data_type == "file_font":
            return InputEntryFileSelector(self, Settings.getInstance().supported_content_types["Font"], self.DetailEntryUpdated)
        elif data_type == "file_sound":
            return InputEntryFileSelector(self, Settings.getInstance().supported_content_types["Sound"], self.DetailEntryUpdated)
        elif data_type == "dropdown":
            return InputEntryDropdown(data['options'], self.DetailEntryUpdated)
        elif data_type == "choice":
            return InputEntryChoice(data, self.AddEntry, self.CreateEntryWidget, self.branch_list, self.DetailEntryUpdated)
        elif data_type == "container":
            new_entry = InputEntryContainer(data['children'])
            for child in data['children']:
                new_entry.addChild(self.CreateEntryWidget(child))

            return new_entry

    def Clear(self):
        """ Deletes all data in the details table """
        self.details_tree.clear()

    def DetailEntryUpdated(self, details_entry):
        """
        Whenever a details entry is changed, we need to inform the active entry so it can refresh necessary elements
        """
        if self.active_entry:
            # First update the cache so the active entry is updated to use the data from the detail entries
            self.UpdateCache()

            # Inform the active entry to refresh
            self.active_entry.Refresh()
