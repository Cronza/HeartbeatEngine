from PyQt5 import QtWidgets, QtGui
from Editor.Interface.Generic.details_entry_base import DetailsEntryBase

class DetailsEntryTuple(DetailsEntryBase):
    def __init__(self, settings, refresh_func=None, global_toggle_func=None):
        super().__init__(settings, refresh_func, global_toggle_func)

        self.input_widget_title = QtWidgets.QLabel('x')
        self.input_widget = QtWidgets.QLineEdit()
        self.input_widget.textChanged.connect(self.InputValueUpdated)
        self.input_widget_alt_title = QtWidgets.QLabel('y')
        self.input_widget_alt = QtWidgets.QLineEdit()
        self.input_widget_alt.textChanged.connect(self.InputValueUpdated)

        # Limit entered values to int only
        self.validator = QtGui.QIntValidator()
        self.input_widget.setValidator(self.validator)
        self.input_widget_alt.setValidator(self.validator)

        # Assign default value
        self.input_widget.setText("0")
        self.input_widget_alt.setText("0")

        # Add input elements to the layout
        self.main_layout.addWidget(self.input_widget_title)
        self.main_layout.addWidget(self.input_widget)
        self.main_layout.addWidget(self.input_widget_alt_title)
        self.main_layout.addWidget(self.input_widget_alt)

    def Get(self):
        return f"{self.input_widget.text()},{self.input_widget_alt.text()}"

    def Set(self, data) -> None:
        # Disconnect the input change signal to allow us to perform the change without flipping the global toggle
        self.input_widget.disconnect()
        self.input_widget_alt.disconnect()

        # Change the data without causing any signal calls
        tuple_data = data.split(',')
        self.input_widget.setText(tuple_data[0])
        self.input_widget_alt.setText(tuple_data[1])

        # Now that the input is changed, reconnect
        self.input_widget.textChanged.connect(self.InputValueUpdated)
        self.input_widget_alt.textChanged.connect(self.InputValueUpdated)

    def MakeUneditable(self):
        self.input_widget.setReadOnly(True)
        self.input_widget_alt.setReadOnly(True)
        self.input_widget.setStyleSheet(self.settings.read_only_background_color);
        self.input_widget_alt.setStyleSheet(self.settings.read_only_background_color);



