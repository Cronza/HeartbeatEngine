from PyQt5 import QtWidgets, QtGui, QtCore
from Editor.Interface.Generic.details_entry_base import DetailsEntryBase
from Editor.Interface.Generic.details_widget_text import DetailsEntryText
from Editor.Interface.Generic.details_widget_bool import DetailsEntryBool
from Editor.Interface.Generic.details_widget_tuple import DetailsEntryTuple
from Editor.Interface.Generic.details_widget_int import DetailsEntryInt
from Editor.Interface.Generic.details_widget_file_selector import DetailsEntryFileSelector
from Editor.Interface.Generic.details_widget_dropdown import DetailsEntryDropdown
from Editor.Interface.Generic.details_widget_container import DetailsEntryContainer


class Details(QtWidgets.QWidget):
    def __init__(self, settings):
        super().__init__()

        # Main editor ref
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
        self.details_table.setColumnCount(2)  # 2 columns: Name & input

        #self.details_view.header().setStretchLastSection(True)
        #self.details_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        #self.details_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        """
        self.details_table.horizontalHeader().hide()
        self.details_table.verticalHeader().hide()
        self.details_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.details_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)  # Disable multi-selection
        self.details_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)  # Disables cell selection
        """


        # ********** Add All Major Pieces to details layout **********
        self.details_layout.addWidget(self.details_title)
        self.details_layout.addWidget(self.details_toolbar)
        self.details_layout.addWidget(self.details_table)

    def PopulateDetails(self, selected_entry):
        # Clear the existing details
        self.Clear()

        self.active_entry = selected_entry
        for requirement in self.active_entry.action_data['requirements']:
            # Create a new entry, and add it to the details list
            self.AddEntry(self.CreateEntry(requirement))

            # TEST ADD
            """
            new_details_entry = QtWidgets.QTreeWidgetItem()
            new_details_entry.setData(0, 0, requirement['name'])

            #Add the new widget, and set the data widget for each column
            self.details_table.addTopLevelItem(new_details_entry)
            self.details_table.setItemWidget(new_details_entry, 1, QtWidgets.QTextEdit("Test Text"))
            """

        # Adjust the rows to fit their contents
        #self.details_table.resizeRowsToContents()

        """
        Populates the details table with an entry for all relevant action_data parameters of the given entry.
        If an entry is already selected, cache the values of all detail entries in the entry, and load the cache from
        the new selection if applicable

        If this was called manually, skip the caching and just load from the existing cache
        """
        """
        # Cache any changes to details in the entry, so next time its selected, that data can be shown
        # Optionally, if this was called manually, then the selected entry will match our active one. In this case,
        # skip caching the data, and treat this as a reload
        if selected_entry is not self.active_entry:
            for row in range(0, self.details_table.rowCount()):
                param_name = self.details_table.item(row, 0).text()
                param_value = self.details_table.cellWidget(row, 1).Get()
                self.active_entry.cache_data[param_name] = param_value

        # Clear the existing details
        self.Clear()

        self.active_entry = selected_entry
        for requirement in self.active_entry.action_data['requirements']:

            # Create a new entry, and add it to the details list
            self.AddEntry(self.CreateEntry(requirement))

        # Adjust the rows to fit their contents
        self.details_table.resizeRowsToContents()

        # If this entry has cached data in it, load it
        if self.active_entry.cache_data:
            for row in range(0, self.details_table.rowCount()):
                param_name = self.details_table.item(row, 0).text()

                # The cache uses a dict model where keys are the param names. Use the param name to fetch any stored
                # value
                cached_value = self.active_entry.cache_data[param_name]
                self.details_table.cellWidget(row, 1).Set(cached_value)
        """

    def CreateEntry(self, data) -> tuple:
        """ Given an action_data dict, create a new details entry widget and return it """
        # Populate the data column with the widget appropriate to the given type
        details_widget = self.GetDetailsWidget(data)

        # Set the name
        details_widget.name_widget.setText(data['name'])

        # Make the option read-only if applicable
        if not data['type'] == 'container':
            if not data['editable']:
                details_widget.MakeUneditable()

        return details_widget

    def AddEntry(self, entry, parent):
        """
        Given a details widget, add it to the bottom of the details tree
        Optionally, if a parent is provided, the entry is assigned as a child to it
        """

        #new_details_entry = QtWidgets.QTreeWidgetItem()
        if parent:
            print("Parent specified - Adding as a child")
            self.details_table.parent.addChild(entry)
        else:
            print("Parent not specified - Adding to root")
            self.details_table.addTopLevelItem(entry)

        self.details_table.setItemWidget(entry, 0, entry.name_widget)
        self.details_table.setItemWidget(entry, 1, entry.input_container)



        """
        # Add a new, empty row
        self.details_table.insertRow(self.details_table.rowCount())

        # Populate the row with each element of this particular detail
        new_row = self.details_table.rowCount() - 1
        self.details_table.setItem(new_row, 0, entry[0])
        self.details_table.setCellWidget(new_row, 1, entry[1])

        self.details_table.resizeRowToContents(new_row)
        """
    def GetDetailsWidget(self, data: dict):
        """ Given an action data dict, create and return the relevant details widget """
        #@TODO: Can this be converted to use an enum?

        data_type = data['type']

        if data_type == "str":
             return DetailsEntryText(self.settings)

        elif data_type == "tuple":
            return DetailsEntryTuple(self.settings)

        elif data_type == "bool":
            return DetailsEntryBool(self.settings)

        elif data_type == "int":
            return DetailsEntryInt(self.settings)

        elif data_type == "file":
            return DetailsEntryFileSelector(self.settings, "")

        elif data_type == "file_image":
            return DetailsEntryFileSelector(self.settings, self.settings.SUPPORTED_CONTENT_TYPES['Image'])

        elif data_type == "dropdown":
            return DetailsEntryDropdown(self.settings, data['default'])

        elif data_type == "container":
            new_entry = DetailsEntryContainer(self.settings, data['children'])
            for child in data['children']:
                print(child)
                child_entry = self.CreateEntry(child)
                #new_entry.AddEntry(child_entry)

            return new_entry

    def Clear(self):
        """ Deletes all data in the details table """
        self.details_table.clear()
