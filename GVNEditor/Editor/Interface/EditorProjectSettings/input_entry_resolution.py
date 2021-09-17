from PyQt5 import QtWidgets
from GVNEditor.Editor.Interface.Primitives.input_entry_base import InputEntryBase


class InputEntryResolution(InputEntryBase):
    """
    An alternative to the regular dropdown customized to support the project's resolution settings

    The resolution settings are divided into two settings:
    - An int input representing the index of the selected resolution
    - A specialized dropdown representing resolution choices

    When the latter is changed, the former needs to be updated as well. Instead of trying to build
    a system for handling inter-input entry dependencies, this widget is given a reference to the project
    settings so it can go and update the former at it's leisure
    """

    def __init__(self, settings, resolution_options, project_settings):
        super().__init__(settings, None)

        self.project_settings = project_settings

        self.input_widget = QtWidgets.QComboBox()
        self.input_widget.setFont(self.settings.paragraph_font)
        self.input_widget.setStyleSheet(settings.paragraph_color)
        self.options = resolution_options

        for option in self.options:
            self.input_widget.addItem(str(option))

        # Use the value of the "Int" widget mentioned in the class docstring to switch the active option
        # @TODO: Figure out how to avoid hard-coding the category name here
        self.input_widget.setCurrentIndex(self.project_settings["Window"]["resolution"])

        # Add input elements to the layout
        self.main_layout.addWidget(self.input_widget)

        self.input_widget.currentIndexChanged.connect(self.InputValueUpdated)

    def Get(self):
        # Typically, this function is used when retrieving the data and storing it somewhere. When this happens,
        # let's make sure to update the additional "Int" widget mentioned in the class docstring

        #@TODO: Figure out how to avoid hard-coding the category name here
        self.project_settings["Window"]["resolution"] = self.input_widget.currentIndex()

        return self.options
    