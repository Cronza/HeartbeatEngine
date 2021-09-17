from PyQt5 import QtWidgets, QtGui
from GVNEditor.Editor.Interface.Primitives.input_entry_base import InputEntryBase

class InputEntryTuple(InputEntryBase):
    def __init__(self, settings, refresh_func=None):
        super().__init__(settings, refresh_func)

        self.input_widget_title = QtWidgets.QLabel('X')
        self.input_widget_title.setFont(self.settings.paragraph_font)
        self.input_widget_title.setStyleSheet(settings.paragraph_color)
        self.input_widget = QtWidgets.QLineEdit()
        self.input_widget.setFont(self.settings.paragraph_font)
        self.input_widget.setStyleSheet(settings.paragraph_color)
        self.input_widget.textChanged.connect(self.InputValueUpdated)

        self.input_widget_alt_title = QtWidgets.QLabel('Y')
        self.input_widget_alt_title.setFont(self.settings.paragraph_font)
        self.input_widget_alt_title.setStyleSheet(settings.paragraph_color)
        self.input_widget_alt = QtWidgets.QLineEdit()
        self.input_widget_alt.setFont(self.settings.paragraph_font)
        self.input_widget_alt.setStyleSheet(settings.paragraph_color)
        self.input_widget_alt.textChanged.connect(self.InputValueUpdated)

        # Limit entered values to int only
        #self.validator = QtGui.QIntValidator()
        #self.input_widget.setValidator(self.validator)
        #self.input_widget_alt.setValidator(self.validator)
        validator = QtGui.QDoubleValidator(0, 1, 8)
        self.input_widget.setValidator(validator)
        self.input_widget_alt.setValidator(validator)

        # Assign default value
        self.input_widget.setText("0")
        self.input_widget_alt.setText("0")

        # Add input elements to the layout
        self.main_layout.addWidget(self.input_widget_title)
        self.main_layout.addWidget(self.input_widget)
        self.main_layout.addWidget(self.input_widget_alt_title)
        self.main_layout.addWidget(self.input_widget_alt)

    def Get(self):
        text_x = self.input_widget.text()
        text_y = self.input_widget_alt.text()

        if text_x == "":
            text_x = 0
        if text_y == "":
            text_y = 0

        return [float(text_x), float(text_y)]

    def Set(self, data) -> None:
        # Disconnect the input change signal to allow us to perform the change without flipping the global toggle
        self.input_widget.disconnect()
        self.input_widget_alt.disconnect()

        # Change the data without causing any signal calls
        self.input_widget.setText(str(data[0]))
        self.input_widget_alt.setText(str(data[1]))

        # Now that the input is changed, reconnect
        self.input_widget.textChanged.connect(self.InputValueUpdated)
        self.input_widget_alt.textChanged.connect(self.InputValueUpdated)

    def MakeUneditable(self):
        self.input_widget.setReadOnly(True)
        self.input_widget_alt.setReadOnly(True)
        self.input_widget.setStyleSheet(self.settings.read_only_background_color)
        self.input_widget_alt.setStyleSheet(self.settings.read_only_background_color)

    def MakeEditable(self):
        self.input_widget.setReadOnly(False)
        self.input_widget.setStyleSheet("")
        self.input_widget_alt.setReadOnly(False)
        self.input_widget_alt.setStyleSheet("")



