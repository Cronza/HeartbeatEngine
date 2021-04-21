from PyQt5 import QtWidgets, QtGui, QtCore
from Editor.Interface.Generic.details_entry_base import DetailsEntryBase
from Editor.Interface.Generic.details_widget_text import DetailsEntryText
from Editor.Interface.Generic.details_widget_bool import DetailsEntryBool
from Editor.Interface.Generic.details_widget_tuple import DetailsEntryTuple
from Editor.Interface.Generic.details_widget_int import DetailsEntryInt
from Editor.Interface.Generic.details_widget_file_selector import DetailsEntryFileSelector
from Editor.Interface.Generic.details_widget_dropdown import DetailsEntryDropdown
from Editor.Interface.Generic.details_widget_container import DetailsEntryContainer


# @TODO: Split this file up into a functions class & U.I class
# @TODO: Make this class agnostic to the dialogue editor


class DetailsPanel(QtWidgets.QWidget):
    def __init__(self, settings):
        super().__init__()

        self.settings = settings

        # In order to save details as we switch between active dialogue entries, keep track of the last selected entry
        self.active_entry = None

        self.details_layout = QtWidgets.QVBoxLayout(self)
        self.details_layout.setContentsMargins(0, 0, 0, 0)
        self.details_layout.setSpacing(0)
        
        # Create title
        self.details_title = QtWidgets.QLabel(self)
        self.details_title.setFont(self.settings.header_1_font)
        self.details_title.setStyleSheet(settings.header_1_color)
        self.details_title.setText("Details")

        # Create the toolbar
        self.details_toolbar = QtWidgets.QFrame(self)
        self.details_toolbar.setAutoFillBackground(False)
        self.details_toolbar.setStyleSheet(
            "QFrame, QLabel, QToolTip {\n"
            "    border-radius: 4px;\n"
            f"   background-color: rgb({self.settings.toolbar_background_color});\n"
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
        self.details_table = QtWidgets.QTreeWidget(self)
        self.details_table.setColumnCount(3)
        self.details_table.setHeaderLabels(['Name', 'Input', 'G'])
        self.details_table.setAutoScroll(False)
        self.details_table.header().setFont(self.settings.button_font)
        self.details_table.header().setStretchLastSection(False)  # Disable to allow custom sizing
        self.details_table.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        self.details_table.header().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.details_table.header().setSectionResizeMode(2, QtWidgets.QHeaderView.Fixed)
        self.details_table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        # --- Specialized Settings for the 'G' column ---
        # 1. Allow columns to be significantly smaller than normal
        self.details_table.header().setMinimumSectionSize(round(self.details_table.header().width() / 4))

        # 2. Force the last column to be barely larger than a standard checkbox
        self.details_table.setColumnWidth(2, round(self.details_table.header().width() / 5))

        # 3. Align the column header text to match the alignment of the checkbox
        self.details_table.headerItem().setTextAlignment(2, QtCore.Qt.AlignCenter)

        # ********** Add All Major Pieces to details layout **********
        self.details_layout.addWidget(self.details_title)
        self.details_layout.addWidget(self.details_toolbar)
        self.details_layout.addWidget(self.details_table)

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

        # Generate each entry
        for requirement in self.active_entry.action_data['requirements']:

            # Create a new entry, and add it to the details list
            self.AddEntry(self.CreateEntryWidget(requirement))

    def UpdateCache(self):
        """
        Cache any changes to details in the entry, so next time its selected, that data can be shown
        """
        # Instead of using the cache, just update the action data directly
        if self.active_entry:

            details_entry_count = self.details_table.invisibleRootItem().childCount()
            for details_entry_index in range(0, details_entry_count):

                details_entry = self.details_table.invisibleRootItem().child(details_entry_index)
                details_entry_name = details_entry.name_widget.text()

                # Since the requirements list is a list, we need to parse through for specifically for the
                # match for this entry
                for requirement in self.active_entry.action_data['requirements']:
                    if requirement['name'] == details_entry_name:

                        # If this details_entry has children (IE. It's a container), consider it's children
                        # Currently this does a depth search of 1. A future upgrade may involve using recursion to
                        # achieve a depth search of n
                        if details_entry.childCount() > 0:

                            for child_entry_index in range(0, details_entry.childCount()):
                                child_entry = details_entry.child(child_entry_index)
                                child_entry_name = child_entry.name_widget.text()

                                # Repeat the search process. If a child is found, cache a value
                                for child_requirement in requirement['children']:
                                    if child_requirement['name'] == child_entry_name:
                                        child_requirement['cache'] = child_entry.Get()

                        # Containers don't store values themselves, so the above code accounts solely for it's children
                        # If this entry is not a container, lets cache normally
                        else:
                            requirement['cache'] = details_entry.Get()

    def CreateEntryWidget(self, data):
        """ Given an action_data dict, create a new details entry widget and return it """
        # Populate the data column with the widget appropriate to the given type
        details_widget = self.GetDetailsWidget(data)

        # Set the name (Applicable for all widget types)
        details_widget.name_widget.setText(data["name"])

        # Containers are special in that they don't hold data, so generally ignore them for certain actions
        if not data["type"] == "container":
            # Only show the global toggle if this detail has a global setting. By default, all settings with global
            # values use them by default
            if 'global' in data:
                details_widget.show_global_toggle = True
                details_widget.global_toggle.Set(True)

            # Update the contents of the entry
            if 'cache' in data:
                details_widget.Set(data["cache"])
            else:
                details_widget.Set(data["default"])

            # Make the option read-only if applicable
            if not data["editable"]:
                details_widget.MakeUneditable()

        return details_widget

    def AddEntry(self, entry, parent=None):
        """
        Given a details widget, add it to the bottom of the details tree
        Optionally, if a parent is provided, the entry is assigned as a child to it
        """

        if parent:
            parent.addChild(entry)
        else:
            self.details_table.addTopLevelItem(entry)

        self.details_table.setItemWidget(entry, 0, entry.name_widget)
        self.details_table.setItemWidget(entry, 1, entry.input_container)
        if entry.show_global_toggle:
            self.details_table.setItemWidget(entry, 2, entry.global_toggle)

        # If the entry has any children, add them all via recursion
        if entry.childCount() > 0:
            for childIndex in range(0, entry.childCount()):
                self.AddEntry(entry.child(childIndex), entry)

    def GetDetailsWidget(self, data: dict):
        """ Given an action data dict, create and return the relevant details widget """
        #@TODO: Can this be converted to use an enum?

        data_type = data['type']

        if data_type == "str":
             return DetailsEntryText(self.settings, self.DetailEntryUpdated, self.GlobalToggleEnabled)

        elif data_type == "tuple":
            return DetailsEntryTuple(self.settings, self.DetailEntryUpdated, self.GlobalToggleEnabled)

        elif data_type == "bool":
            return DetailsEntryBool(self.settings, self.DetailEntryUpdated, self.GlobalToggleEnabled)

        elif data_type == "int":
            return DetailsEntryInt(self.settings, self.DetailEntryUpdated, self.GlobalToggleEnabled)

        elif data_type == "file":
            return DetailsEntryFileSelector(self.settings, "", self.DetailEntryUpdated, self.GlobalToggleEnabled)

        elif data_type == "file_image":
            return DetailsEntryFileSelector(self.settings, self.settings.SUPPORTED_CONTENT_TYPES['Image'], self.DetailEntryUpdated, self.GlobalToggleEnabled)

        elif data_type == "dropdown":
            return DetailsEntryDropdown(self.settings, data['default'], self.DetailEntryUpdated, self.GlobalToggleEnabled)

        elif data_type == "container":
            new_entry = DetailsEntryContainer(self.settings, data['children'])
            for child in data['children']:
                new_entry.addChild(self.CreateEntryWidget(child))

            return new_entry

    def Clear(self):
        """ Deletes all data in the details table """
        self.details_table.clear()

    def DetailEntryUpdated(self, details_entry):
        """
        Whenever a details entry is changed, we need to inform the active entry so it can refresh necessary elements
        """
        if self.active_entry:
            # First update the cache so the active entry is updated to use the data from the detail entries
            self.UpdateCache()

            # Inform the active entry to refresh
            self.active_entry.Refresh()

    def GlobalToggleEnabled(self, details_entry):
        """
        Whenever a details entry's global checkbox is used, we need to refresh that entry with the relevant
        global information stored in the active entry
        """
        key_name = details_entry.name_widget.text()
        for requirement in self.active_entry.action_data['requirements']:
            if requirement['name'] == key_name:
                requirement['cache'] = self.settings.GetGlobalSetting(
                    requirement['global']['category'],
                    requirement['global']['global_parameter']
                )

                # Since we have the details entry reference, let's update it's input
                details_entry.Set(requirement['cache'])

                # Refresh the active entry
                self.active_entry.Refresh()


