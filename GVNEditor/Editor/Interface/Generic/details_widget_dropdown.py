from PyQt5 import QtWidgets, QtGui
from Editor.Interface.Generic.details_entry_base import DetailsEntryBase


#@TODO: Finish this


class DetailsEntryDropdown(DetailsEntryBase):
    def __init__(self, settings, options: str, refresh_func=None):
        """ A variant of the details entry that uses a pre-set list of options, instead of accepting anything """
        super().__init__(settings, refresh_func)

        self.input_widget = QtWidgets.QComboBox()
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





