"""
    The Heartbeat Engine is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    The Heartbeat Engine is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with the Heartbeat Engine. If not, see <https://www.gnu.org/licenses/>.
"""
import re
from PyQt5 import QtWidgets, QtGui, QtCore
from HBEditor.Core.settings import Settings
from HBEditor.Core.Primitives.simple_checkbox import SimpleCheckbox
from HBEditor.Core.Prompts.file_system_prompt import FileSystemPrompt

"""
List of available entries:
    - InputEntryBool
    - InputEntryColor
    - InputEntryContainer
    - InputEntryDropdown
    - InputEntryFileSelector
    - InputEntryFloat
    - InputEntryInt
    - InputEntryParagraph
    - InputEntryText
    - InputEntryTuple
    - InputEntryChoice
"""


class InputEntryBase(QtWidgets.QTreeWidgetItem):
    def __init__(self, refresh_func=None):
        super().__init__()

        # When the input widget is updated, in case another U.I element needs to refresh, use a callback
        self.refresh_func = refresh_func

        # Details entries have three main widgets: 'name_widget', 'input_widget' and 'global_toggle'.
        # - 'name_widget': A standalone text widget representing the name of the detail
        # - 'input_widget': Kept inside 'input_container' as to allow any number of input_widgets for child classes
        # - 'global_toggle': A checkbox representing whether to use a global value or the value in the 'input_widget'

        # 'name_widget' and 'input_widget' are declared, but not initialized as it is up to the subclass to
        # do that
        self.name_widget = QtWidgets.QLabel()

        self.input_widget = None
        self.input_container = QtWidgets.QWidget()

        # 'global_toggle' is not supposed to be shown for all entries. It's only used for entries that need it
        self.show_global_toggle = False
        ##########################################################
        self.global_toggle = SimpleCheckbox(self.GlobalToggle)
        self.global_toggle.setToolTip("Whether to use the global value specified in the project file for this entry")
        ##########################################################

        self.main_layout = QtWidgets.QHBoxLayout(self.input_container)
        self.main_layout.setContentsMargins(0,0,0,0)

    def Get(self):
        pass

    def Connect(self):
        """ Establish the signal for when the input_widget is updated """
        pass

    def Disconnect(self):
        """ Dismantle the signal that monitors the input_widget changes """
        self.input_widget.disconnect()

    def GetGlobal(self) -> bool:
        """ Returns the current value of the global checkbox """
        return self.global_toggle.Get()

    def SetEditable(self, state: int):
        """
        Enables or disables editability of relevant input widgets based on the provided state
        0 = Enabled, 2 = Disabled
        """
        pass

    def RefreshStyle(self):
        """ Refreshes the stylesheet to update any dynamic properties """
        pass

    def InputValueUpdated(self):
        """ When the input value for this entry is changed, call the refresh function provided to this class """
        # Any change to detail entries while the global toggle is enabled will toggle it off
        if self.global_toggle.Get():
            self.global_toggle.Set(False)

        if self.refresh_func:
            self.refresh_func(self)

    def GlobalToggle(self):
        """
        When the global checkbox is toggled on, call a provided function, passing a reference to this class
        This function is not meant to be overridden
        """
        if self.global_toggle.Get():
            self.SetEditable(2)
        else:
            self.SetEditable(0)


class InputEntryBool(InputEntryBase):
    def __init__(self, refresh_func=None):
        super().__init__(refresh_func)

        self.input_widget = QtWidgets.QCheckBox()

        # Add input elements to the layout
        self.main_layout.addWidget(self.input_widget)

        # Connect Signals
        self.input_widget.stateChanged.connect(self.InputValueUpdated)

    def Get(self) -> bool:
        return self.input_widget.isChecked()

    def Connect(self):
        self.input_widget.stateChanged.connect(self.InputValueUpdated)

    def SetEditable(self, state: int):
        if state == 0:
            self.input_widget.setEnabled(True)
        elif state == 2:
            self.input_widget.setEnabled(False)

        self.input_widget.style().polish(self.input_widget)


class InputEntryColor(InputEntryBase):
    def __init__(self, refresh_func=None):
        super().__init__(refresh_func)
        # NOTE FOR THE LOGIC IN THIS FILE
        # Qt doesn't really have a great way of changing widget colors. While stylesheets are nice, retrieving data
        # from a stylesheet is a lesson in pain (You get ALL of the data, not just a part you actually want

        # Additionally, to my knowledge, changing stylesheets don't cause a signal change unless you hook onto the
        # underlying events. I try to avoid this complexity, so the way this file handles detecting changes is different
        # than other detail types
        self.input_widget = QtWidgets.QFrame()
        self.input_widget.setFrameStyle(QtWidgets.QFrame.Panel)
        self.input_widget.setStyleSheet("border: 1px solid rgb(122,122,122);background-color: rgb(255,255,255)")

        # @TODO: Replace style sheet assignment with a QPalette to retain button state styles
        # Create the color selector button, and style it accordingly
        self.color_select_button = QtWidgets.QToolButton()
        self.color_select_button.setObjectName("non-toolbar")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Icons/Color_Wheel.png"), QtGui.QIcon.Normal)
        icon.addPixmap(QtGui.QPixmap(":/Icons/Color_Wheel_Disabled.png"), QtGui.QIcon.Disabled)
        self.color_select_button.setIcon(icon)
        self.color_select_button.clicked.connect(self.OpenColorPrompt)

        # Add input elements to the layout
        self.main_layout.addWidget(self.input_widget)
        self.main_layout.addWidget(self.color_select_button)

    def Get(self):
        raw_style_sheet = self.input_widget.styleSheet()
        pattern = "background-color: rgb\((.*)\)"

        color = re.search(pattern, raw_style_sheet).group(1)
        return list(map(int, color.split(",")))

    def SetEditable(self, state: int):
        if state == 0:
            self.color_select_button.setEnabled(True)
        elif state == 2:
            self.color_select_button.setEnabled(False)

        self.input_widget.style().polish(self.input_widget)

    def OpenColorPrompt(self):
        color_choice = QtWidgets.QColorDialog.getColor()

        # 'rgb()' or 'getRgb()' return a QColor with alpha. We only want the RGB values (This feels wrong and I hate it)
        rgb = color_choice.red(), color_choice.green(), color_choice.blue()

        if color_choice.isValid():
            self.input_widget.setStyleSheet(f"background-color: rgb({', '.join(map(str, rgb))})")

            # Manually call the input change func since we know for a fact the input widget has changed
            self.InputValueUpdated()


class InputEntryContainer(InputEntryBase):
    def __init__(self, children: list, refresh_func=None):
        super().__init__(refresh_func)

    #@TODO: Does this class uh...need to exist? It basically does nothing special
    def Get(self):
        pass


class InputEntryDropdown(InputEntryBase):
    def __init__(self, options, refresh_func=None):
        """ A variant of the details entry that uses a pre-set list of options, instead of accepting anything """
        super().__init__(refresh_func)

        self.input_widget = QtWidgets.QComboBox()
        self.options = options

        # Pre-load the list of dropdown options
        for option in self.options:
            self.input_widget.addItem(str(option))

        self.input_widget.currentIndexChanged.connect(self.InputValueUpdated)

        # Add input elements to the layout
        self.main_layout.addWidget(self.input_widget)

    def Get(self):
        return self.input_widget.currentText()

    def Connect(self):
        self.input_widget.currentIndexChanged.connect(self.InputValueUpdated)

    def SetEditable(self, state: int):
        if state == 0:
            self.input_widget.setEnabled(True)
        elif state == 2:
            self.input_widget.setEnabled(False)

        self.input_widget.style().polish(self.input_widget)


class InputEntryFileSelector(InputEntryBase):
    def __init__(self, details_panel, type_filter, refresh_func=None):
        super().__init__(refresh_func)

        self.details_panel = details_panel

        # Store a type filter to restrict what files can be chosen in the browser
        self.type_filter = type_filter

        self.input_widget = QtWidgets.QLineEdit()
        self.input_widget.setText("None")
        self.input_widget.textChanged.connect(self.InputValueUpdated)
        self.input_widget.setReadOnly(True)

        # Create the file selector button, and style it accordingly
        self.file_select_button = QtWidgets.QToolButton()
        self.file_select_button.setObjectName("non-toolbar")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Icons/Folder.png"), QtGui.QIcon.Normal)
        icon.addPixmap(QtGui.QPixmap(":/Icons/Folder_Disabled.png"), QtGui.QIcon.Disabled)
        self.file_select_button.setIcon(icon)

        # Add input elements to the layout
        self.main_layout.addWidget(self.input_widget)
        self.main_layout.addWidget(self.file_select_button)

        # Connect Signals
        self.file_select_button.clicked.connect(self.OpenFilePrompt)

    def Get(self):
        return self.input_widget.text()

    def SetEditable(self, state: int):
        if state == 0:
            self.file_select_button.setEnabled(True)
            #self.input_widget.setReadOnly(False)
        elif state == 2:
            self.file_select_button.setEnabled(False)
            #self.input_widget.setReadOnly(True)

        self.input_widget.style().polish(self.input_widget)

    def OpenFilePrompt(self) -> str:
        #@TODO: Replace file browser will popup list of files available in the project
        """ Prompts the user with a filedialog, accepting an existing file """
        prompt = FileSystemPrompt(self.details_panel)
        existing_file = prompt.GetFile(
            Settings.getInstance().GetProjectContentDirectory(),
            self.type_filter,
            "Choose a File to Open"
        )

        # Did the user choose a value?
        if existing_file:
            selected_dir = existing_file

            # Remove the project dir from the path, so that the selected dir only contains a relative path
            selected_dir = selected_dir.replace(Settings.getInstance().user_project_dir + "/", "")
            self.input_widget.setText(selected_dir)


class InputEntryFloat(InputEntryBase):
    def __init__(self, refresh_func=None):
        super().__init__(refresh_func)

        self.input_widget = QtWidgets.QLineEdit()
        self.input_widget.textEdited.connect(self.InputValueUpdated)

        # Limit entered values to float only
        self.validator = QtGui.QDoubleValidator()
        self.input_widget.setValidator(self.validator)

        # Assign default value
        self.input_widget.setText("0.0")

        # Add input elements to the layout
        self.main_layout.addWidget(self.input_widget)

    def Get(self) -> float:
        value = self.input_widget.text()

        # Since editing inputs can lead to live updates, the values must always be float castable. Since, as the user
        # edits, it might lead to an empty string or '-', always use 0 as a baseline instead of checking every scenario
        conv_val = 0
        try:
            conv_val = float(value)
        except:
            pass

        return conv_val

    def SetEditable(self, state: int):
        if state == 0:
            self.input_widget.setReadOnly(False)
        elif state == 2:
            self.input_widget.setReadOnly(True)

        self.input_widget.style().polish(self.input_widget)


class InputEntryInt(InputEntryBase):
    def __init__(self, refresh_func=None):
        super().__init__(refresh_func)

        self.input_widget = QtWidgets.QLineEdit()

        # Limit entered values to int only
        self.validator = QtGui.QIntValidator()
        self.input_widget.setValidator(self.validator)

        # Assign default value
        self.input_widget.setText("0")

        # Signal
        self.input_widget.textEdited.connect(self.InputValueUpdated)

        # Add input elements to the layout
        self.main_layout.addWidget(self.input_widget)

    def Get(self) -> int:
        value = self.input_widget.text()

        # Since editing inputs can lead to live updates, the values must always be int castable. Since, as the user
        # edits, it might lead to an empty string or '-', always use 0 as a baseline instead of checking every scenario
        conv_val = 0
        try:
            conv_val = int(value)
        except:
            pass

        return conv_val

    def SetEditable(self, state: int):
        if state == 0:
            self.input_widget.setReadOnly(False)
        elif state == 2:
            self.input_widget.setReadOnly(True)

        self.input_widget.style().polish(self.input_widget)

class InputEntryParagraph(InputEntryBase):
    def __init__(self, refresh_func=None):
        super().__init__(refresh_func)

        self.input_widget = QtWidgets.QPlainTextEdit()
        self.input_widget.setMaximumHeight(100)

        self.input_widget.textChanged.connect(self.InputValueUpdated)

        # Add input elements to the layout
        self.main_layout.addWidget(self.input_widget)

    def Get(self) -> str:
        return self.input_widget.toPlainText()

    def Connect(self):
        self.input_widget.textChanged.connect(self.InputValueUpdated)

    def SetEditable(self, state: int):
        if state == 0:
            self.input_widget.setReadOnly(False)

        elif state == 2:
            self.input_widget.setReadOnly(True)


class InputEntryText(InputEntryBase):
    def __init__(self, refresh_func=None):
        super().__init__(refresh_func)

        self.input_widget = QtWidgets.QLineEdit()
        self.input_widget.textEdited.connect(self.InputValueUpdated)

        # Add input elements to the layout
        self.main_layout.addWidget(self.input_widget)

    def Get(self) -> str:
        return self.input_widget.text()

    def Connect(self):
        self.input_widget.textChanged.connect(self.InputValueUpdated)

    def SetEditable(self, state: int):
        if state == 0:
            self.input_widget.setReadOnly(False)
        elif state == 2:
            self.input_widget.setReadOnly(True)

        self.input_widget.style().polish(self.input_widget)


class InputEntryTuple(InputEntryBase):
    def __init__(self, refresh_func=None):
        super().__init__(refresh_func)

        #@TODO: Make this two floats, not two ints
        self.input_widget_title = QtWidgets.QLabel('X')
        self.input_widget = QtWidgets.QLineEdit()

        self.input_widget_alt_title = QtWidgets.QLabel('Y')
        self.input_widget_alt = QtWidgets.QLineEdit()

        # Limit entered values to int only
        validator = QtGui.QDoubleValidator(-2, 2, 8, notation=QtGui.QDoubleValidator.StandardNotation)
        self.input_widget.setValidator(validator)
        self.input_widget_alt.setValidator(validator)

        # Assign default value
        self.input_widget.setText("0")
        self.input_widget_alt.setText("0")

        # Signals
        self.input_widget.textEdited.connect(self.InputValueUpdated)
        self.input_widget_alt.textEdited.connect(self.InputValueUpdated)

        # Add input elements to the layout
        self.main_layout.addWidget(self.input_widget_title)
        self.main_layout.addWidget(self.input_widget)
        self.main_layout.addWidget(self.input_widget_alt_title)
        self.main_layout.addWidget(self.input_widget_alt)

    def Get(self):
        text_x = self.input_widget.text()
        text_y = self.input_widget_alt.text()

        conv_x = 0
        conv_y = 0

        # Since editing inputs can lead to live updates, the values must always be float castable. Since, as the user
        # edits, it might lead to an empty string or '-', always use 0 as a baseline instead of checking every scenario
        try:
            conv_x = float(text_x)
        except:
            pass

        try:
            conv_y = float(text_y)
        except:
            pass

        return [conv_x, conv_y]

    def SetEditable(self, state: int):
        if state == 0:
            self.input_widget.setReadOnly(False)
            self.input_widget_alt.setReadOnly(False)
        elif state == 2:
            self.input_widget.setReadOnly(True)
            self.input_widget_alt.setReadOnly(True)

        self.input_widget.style().polish(self.input_widget)
        self.input_widget_alt.style().polish(self.input_widget_alt)


class InputEntryChoice(InputEntryBase):
    """
    A heavily specialized widget built to allow an optionally-expandable list of drop-downs,
    each presenting a choice of an existing branch

    Given this class has user-control over generating the children, it needs access to adding and
    rendering children
    """

    def __init__(self, data, add_to_parent_func, create_input_widget_func, branches_list, project_settings):
        super().__init__(None)

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

        # Add Choice Button
        self.add_choice_button = QtWidgets.QToolButton()
        self.add_choice_button.setObjectName("choice-add")

        # Add input elements to the layout
        self.main_layout.addWidget(self.add_choice_button)

        # Connect Signals
        self.add_choice_button.clicked.connect(self.AddChoice)

    def Get(self):
        # Since the choice entry is so custom, we have to build the entire dict, children included to be returned
        branch_list = []
        for container_index in range(0, self.childCount()):
            choice_container = self.child(container_index)
            branch_dict = {}
            for input_index in range(0, choice_container.childCount()):
                input_widget = choice_container.child(input_index)
                # Omit the value if the global toggle is enabled
                if not input_widget.show_global_toggle or not input_widget.GetGlobal():
                    branch_dict[input_widget.name_widget.text()] = input_widget.Get()

            branch_list.append(branch_dict)
        return branch_list

    def Set(self, data) -> None:
        for choice_data in data:
            self.AddChoice(choice_data)

    def AddChoice(self, data=None):
        """
        Adds a choice entry to the choice list, filling it with input widgets for every item
        in the 'templates' dict. If 'data' is provided, use it to populate the input widgets
        """
        # Each choice is given a parent container to help organize the choice's input widgets. This is also customized
        # to have a close button which deletes the choice from the list
        new_choice_container = InputEntryContainer(self.data)

        # Delete button
        delete_choice_button = QtWidgets.QToolButton()
        delete_choice_button.setObjectName("choice-remove")

        new_choice_container.input_widget = delete_choice_button
        new_choice_container.input_widget.clicked.connect(lambda delete: self.DeleteChoice(new_choice_container))
        new_choice_container.main_layout.addWidget(new_choice_container.input_widget)
        self.add_to_parent_func(new_choice_container, self)

        # Collect the current list of available branch names
        branch_names = []
        for index in range(0, self.branches_list.count()):
            branch_names.append(self.branches_list.itemWidget(self.branches_list.item(index)).Get()[0])

        # Add special options before we add the requirements from the template
        branch_dropdown = InputEntryDropdown(branch_names, None)
        branch_dropdown.name_widget.setText("branch")
        self.add_to_parent_func(branch_dropdown, new_choice_container)
        key_input = InputEntryText(lambda change: self.UpdateChoiceName(new_choice_container))
        key_input.name_widget.setText("key")
        self.add_to_parent_func(key_input, new_choice_container)

        from HBEditor.Core.Primitives.input_entry_updater import EntryUpdater
        if data:
            EntryUpdater.Set(key_input, data["key"])
            EntryUpdater.Set(branch_dropdown, data["branch"])
        else:
            EntryUpdater.Set(key_input, f"Choice_{self.childCount()}")

        # Add an input widget for each item in the 'template' dict
        for item in self.data["template"]:
            new_choice_detail = self.create_input_widget_func(item)
            self.add_to_parent_func(new_choice_detail, new_choice_container)
            if data:
                if item["name"] in data:
                    EntryUpdater.Set(new_choice_detail, data[item["name"]])

        # Change the entry to use the key name (Faster than using the update function since we already have the ref)
        new_choice_container.name_widget.setText(key_input.Get())

    def UpdateChoiceName(self, choice_container):
        """ Updates the name of the choic entry to use the value of the 'key' entry """
        # While we could loop through the children for the key input, it's a bit inefficient. Let's lazily
        # assume which index it is
        key_input = choice_container.child(1)
        choice_container.name_widget.setText(key_input.Get())

    def DeleteChoice(self, choice_container_widget):
        """ Deletes the chosen choice entry """
        self.removeChild(choice_container_widget)
