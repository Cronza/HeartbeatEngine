from PyQt5 import QtWidgets, QtCore
from HBEditor.Core.settings import Settings
from HBEditor.Core.DataTypes.parameter_types import ParameterType
from HBEditor.Core.Primitives.input_entries import *


class EntryUpdater:
    """
    A utility class used to update the values of an InputEntry

    Due to an unknown crashing issue with entries updating their own 'input_widget', a third party object (this class)
    was created to facilitate applying the correct method of updating based on the type of entry
    """

    @staticmethod
    def GetType(type_str):
        # Convert the scheme type string into an actual parameter type
        try:
            return ParameterType[type_str]
        except Exception as exc:
            print(f"Failed to cast parameter type: {exc}")

    @staticmethod
    def Set(input_widget: InputEntryBase, value):
        """ Update the given input widget, casting the value to the respective type to match the widget """
        if isinstance(input_widget, InputEntryText):
            input_widget.input_widget.setText(value)
        elif isinstance(input_widget, InputEntryParagraph):
            input_widget.Disconnect()
            input_widget.input_widget.setPlainText(value)
            input_widget.Connect()
        elif isinstance(input_widget, InputEntryTuple):
            input_widget.input_widget.setText(str(value[0]))
            input_widget.input_widget_alt.setText(str(value[1]))
        elif isinstance(input_widget, InputEntryBool):
            input_widget.Disconnect()
            input_widget.input_widget.setChecked(value)
            input_widget.Connect()
        elif isinstance(input_widget, InputEntryColor):
            css = f"border: 1px solid rgb(122,122,122); background-color: rgb({','.join(map(str, value))})"
            input_widget.input_widget.setStyleSheet(css)
        elif isinstance(input_widget, InputEntryInt):
            input_widget.input_widget.setText(str(value))
        elif isinstance(input_widget, InputEntryFloat):
            input_widget.input_widget.setText(str(value))
        elif isinstance(input_widget, InputEntryFileSelector):
            input_widget.input_widget.setText(value)
        elif isinstance(input_widget, InputEntryDropdown):
            input_widget.Disconnect()
            input_widget.input_widget.setCurrentIndex(input_widget.input_widget.findText(value))
            input_widget.Connect()
        elif isinstance(input_widget, InputEntryChoice):
            input_widget.Set(value)
        else: #@TODO: Add Array & ArrayEntry
            print(f"Unknown Type: {type(input_widget)}")

