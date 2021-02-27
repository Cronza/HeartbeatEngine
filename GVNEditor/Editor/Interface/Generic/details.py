from PyQt5 import QtWidgets, QtGui, QtCore
from Editor.Interface.Generic.details_entry_base import DetailsEntryBase
from Editor.Interface.Generic.details_widget_text import DetailsEntryText
from Editor.Interface.Generic.details_widget_bool import DetailsEntryBool
from Editor.Interface.Generic.details_widget_tuple import DetailsEntryTuple
from Editor.Interface.Generic.details_widget_int import DetailsEntryInt
from Editor.Interface.Generic.details_widget_file_selector import DetailsEntryFileSelector

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
        self.details_table = QtWidgets.QTableWidget(self)
        self.details_table.setColumnCount(2)
        self.details_table.horizontalHeader().hide()
        self.details_table.verticalHeader().hide()
        self.details_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.details_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)  # Disable multi-selection
        self.details_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)  # Disables cell selection

        # ********** Add All Major Pieces to details layout **********
        self.details_layout.addWidget(self.details_title)
        self.details_layout.addWidget(self.details_toolbar)
        self.details_layout.addWidget(self.details_table)

    def PopulateDetails(self, selected_entry):
        """
        Populates the details table with an entry for all relevant action_data parameters of the given entry.
        If an entry is already selected, cache the values of all detail entries in the entry, and load the cache from
        the new selection if applicable

        If this was called manually, skip the caching and just load from the existing cache
        """
        print("Heh")

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

    def CreateEntry(self, data) -> tuple:
        """ Given an action_data dict, create a tuple of <entry_name>, <data_widget> and return it """
        # Populate the name column for this row, making it non-editable
        entry_name = QtWidgets.QTableWidgetItem(data['name'])
        entry_name.setFlags(QtCore.Qt.ItemIsEnabled)

        # Populate the data column with the widget appropriate to the given type
        data_widget = self.GetDataWidget(data['type'])

        # Make the option read-only if applicable
        if not data['editable']:
            data_widget.MakeUneditable()

        return entry_name, data_widget

    def AddEntry(self, entry):
        """ Given a tuple of <entry_name>, <data_widget>, add them to the bottom of the details list """

        # Add a new, empty row
        self.details_table.insertRow(self.details_table.rowCount())

        # Populate the row with each element of this particular detail
        self.details_table.setItem(self.details_table.rowCount() - 1, 0, entry[0])
        self.details_table.setCellWidget(self.details_table.rowCount() - 1, 1, entry[1])

    def GetDataWidget(self, data_type: str):
        """ Given a data type, return the relevant object"""

        if data_type == "str":
             return DetailsEntryText(self.settings)

        elif data_type == "tuple":
            return DetailsEntryTuple(self.settings)

        elif data_type == "bool":
            return DetailsEntryBool(self.settings)

        elif data_type == "int":
            return DetailsEntryInt(self.settings)

        elif data_type == "file":
            return DetailsEntryFileSelector(self.settings)

    def Clear(self):
        """ Deletes all rows in the details table """
        self.details_table.setRowCount(0)
