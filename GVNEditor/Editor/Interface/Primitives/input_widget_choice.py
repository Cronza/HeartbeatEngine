from PyQt5 import QtGui, QtWidgets, QtCore
from Editor.Interface.Primitives.input_entry_base import InputEntryBase
from Editor.Interface.Primitives.input_entry_dropdown import InputEntryDropdown

class InputEntryChoice(InputEntryBase):
    """
    An alternative to the regular dropdown customized to support the project's resolution settings

    The resolution settings are divided into two settings:
    - An int input representing the index of the selected resolution
    - A specialized dropdown representing resolution choices

    When the latter is changed, the former needs to be updated as well. Instead of trying to build
    a system for handling inter-input entry dependencies, this widget is given a reference to the project
    settings so it can go and update the former at it's leisure
    """

    def __init__(self, settings, branch_list, project_settings):
        super().__init__(settings, None)

        self.main_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.project_settings = project_settings

        #self.input_widget = QtWidgets.QLineEdit()
        #self.input_widget.setFont(self.settings.paragraph_font)
        #self.input_widget.setStyleSheet(settings.paragraph_color)
        #self.input_widget.setText("None")
        #self.input_widget.textChanged.connect(self.InputValueUpdated)
        #self.input_widget.setReadOnly(True)

        # Add Choice Button
        self.add_choice_button = QtWidgets.QToolButton()
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(self.settings.ConvertPartialToAbsolutePath("Content/Icons/Plus.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        self.add_choice_button.setIcon(icon)

        # Add input elements to the layout
        #self.main_layout.addWidget(self.input_widget)
        self.main_layout.addWidget(self.add_choice_button)

        # Connect Signals
        self.add_choice_button.clicked.connect(self.AddChoice)

    def AddChoice(self):
        """ Adds a choice entry to the choice list"""
        print("Adding Choice")
        new_child = InputEntryDropdown(self.settings, ["None", "None"], None)
        self.addChild(new_child)