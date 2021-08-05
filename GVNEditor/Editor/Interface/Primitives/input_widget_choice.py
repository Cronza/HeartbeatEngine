from PyQt5 import QtGui, QtWidgets, QtCore
from Editor.Interface.Primitives.input_entry_base import InputEntryBase
from Editor.Interface.Primitives.input_entry_dropdown import InputEntryDropdown
from Editor.Interface.Primitives.input_entry_container import InputEntryContainer

class InputEntryChoice(InputEntryBase):
    """
    A heavily specialized widget built to allow an optionally-expandable list of drop-downs,
    each presenting a choice of an existing branch

    Given this class has user-control over generating the children, it needs access to adding and
    rendering children
    """

    def __init__(self, settings, data, add_to_parent_func, create_input_widget_func, branches_list, project_settings):
        super().__init__(settings, None)

        # Since this class does a large amount of manual work in the creation of it's children, it needs
        # access to a number of things from it's parent:
        # - the entire data block from the ActionDatabase
        # - A function that can add given entries to the main containing widget (QTree, QList, etc)
        # - A function that creates the possible input widgets needed (This helps avoid having those
        #   potentially numerous dependencies in here)
        self.data = data
        self.add_to_parent_func = add_to_parent_func
        self.create_input_widget_func = create_input_widget_func
        self.branches_list = branches_list

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

    def Get(self):
        test_dict = [
            {"branch":"01"},
            {"branch":"02"},
        ]
        return test_dict

    def Set(self, data) -> None:
        print("Provided Choice Data")
        print(data)
        print(type(data))
        # Disconnect the input change signal to allow us to perform the change without flipping the global toggle
        #self.input_widget.disconnect()

        # Change the data without causing any signal calls
        #self.input_widget.setCurrentIndex(self.input_widget.findText(data))

        # Now that the input is changed, reconnect
        #self.input_widget.currentIndexChanged.connect(self.InputValueUpdated)

    def AddChoice(self):
        """
        Adds a choice entry to the choice list, filling it with input widgets for every item
        in the 'templates' dict
        """
        print("Adding Choice Container")
        print(self.data)
        new_choice_container = InputEntryContainer(self.settings, self.data)
        new_choice_container.name_widget.setText("01") #Investigate a programmatic naming convention (Should be the key)
        self.add_to_parent_func(new_choice_container, self)

        branch_names = []
        for index in range(0, self.branches_list.count()):
            branch_names.append(self.branches_list.itemWidget(self.branches_list.item(index)).Get()[0])

        # Before we populate the defaults, specially add the branch dropdown
        new_child = InputEntryDropdown(self.settings, branch_names, None)
        self.add_to_parent_func(new_child, new_choice_container)

        for item in self.data["template"]:
            new_choice_detail = self.create_input_widget_func(item)
            self.add_to_parent_func(new_choice_detail, new_choice_container)