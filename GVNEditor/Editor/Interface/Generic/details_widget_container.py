from PyQt5 import QtWidgets, QtGui
from Editor.Interface.Generic.details_entry_base import DetailsEntryBase


class DetailsEntryContainer(DetailsEntryBase):
    def __init__(self, settings, children: list):
        super().__init__(settings)
        print("creating container")
        #self.input_widget = QtWidgets.QTableWidget()
        #self.input_widget = QtWidgets.QTableWidget(self)
        #self.input_widget.setColumnCount(2)
        #self.input_widget.horizontalHeader().hide()
        #self.input_widget.verticalHeader().hide()
        #self.input_widget.horizontalHeader().setStretchLastSection(True)
        #self.input_widget.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        #self.input_widget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)  # Disable multi-selection
        #self.input_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)  # Disables cell selection
        #self.input_widget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)      # <---
        #self.input_widget.verticalScrollBar().hide()
        #self.input_widget.horizontalScrollBar().hide()
        #self.input_widget.adjustSize()
        #self.input_widget.setText("None"



        # Add input elements to the layout
        #self.main_layout.addWidget(self.input_widget)
        #self.main_layout.addWidget(self.file_select_button)

    def Get(self):
        #return self.input_widget.text()
        return "Test"

    def Set(self, data) -> None:
        #self.input_widget.setText(data)
        #return "test"
        pass

    def MakeUneditable(self):
        #self.input_widget.setReadOnly(True)
        #self.input_widget.setStyleSheet(self.settings.read_only_background_color);
        pass

    def AddEntry(self, entry):
        """ Given a tuple of <entry_name>, <data_widget>, add them to the container """

        # Add a new, empty row
        self.input_widget.insertRow(self.input_widget.rowCount())

        # Populate the row with each element of this particular detail
        new_row = self.input_widget.rowCount() - 1
        self.input_widget.setItem(new_row, 0, entry[0])
        self.input_widget.setCellWidget(new_row, 1, entry[1])

        self.input_widget.resizeRowToContents(new_row)


        # TEMP
        for row in range(0, self.input_widget.rowCount()):
            thing = self.input_widget.cellWidget(row, 1)
            print(thing.height())
            self.input_widget.setMinimumSize(500,500)
            #self.input_widget.size().setHeight((500))
            #self.input_widget.setFixedHeight(500)
            #self.input_widget.adjustSize()
            #self.input_widget.sizeAdjustPolicy()

        #self.input_widget.adjustSize()
        print(self.input_widget.sizeHint())

        #self.



