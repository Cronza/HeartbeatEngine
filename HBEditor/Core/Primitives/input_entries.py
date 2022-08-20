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
import copy
from PyQt5 import QtWidgets, QtGui, QtCore
from HBEditor.Core import settings
from HBEditor.Core.Prompts.file_system_prompt import FileSystemPrompt
from HBEditor.Core.Logger.logger import Logger
from HBEditor.Core.DataTypes.parameter_types import ParameterType

"""
List of available entries:
    - InputEntryBool
    - InputEntryColor
    - InputEntryDropdown
    - InputEntryFileSelector
    - InputEntryFloat
    - InputEntryInt
    - InputEntryParagraph
    - InputEntryText
    - InputEntryTuple
    - InputEntryArray
    - InputEntryArrayElement
"""


class InputEntryBase(QtWidgets.QWidget):
    SIG_USER_UPDATE = QtCore.pyqtSignal(object)

    def __init__(self, data):
        super().__init__()

        self.data = data

        # QWidgets don't natively know if they've been added as a child to a model widget item, so we need our own
        # way of storing that information
        self.owning_model_item = None

        # It's up to the children to add the input_widget to the layout
        self.input_widget = None

        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(0,0,0,0)

    def Get(self):
        return self.data

    def Set(self, data):
        self.data = data

    def Connect(self):
        pass

    def Disconnect(self):
        pass

    def SetEditable(self, state: int):
        pass


class InputEntryBool(InputEntryBase):
    def __init__(self, data):
        super().__init__(data)
        self.input_widget = QtWidgets.QCheckBox()
        self.main_layout.addWidget(self.input_widget)

    def Get(self):
        self.data["value"] = self.input_widget.isChecked()
        return self.data

    def Set(self, data):
        self.input_widget.setChecked(bool(data))

    def Connect(self):
        self.input_widget.stateChanged.connect(lambda: self.SIG_USER_UPDATE.emit(self.owning_model_item))

    def Disconnect(self):
        self.input_widget.disconnect()

    def SetEditable(self, state: int):
        if state == 0:
            self.input_widget.setEnabled(True)
        elif state == 2:
            self.input_widget.setEnabled(False)

        self.input_widget.style().polish(self.input_widget)


class InputEntryColor(InputEntryBase):
    def __init__(self, data):
        super().__init__(data)
        self.input_widget = QtWidgets.QFrame()
        self.input_widget.setFrameStyle(QtWidgets.QFrame.Panel)
        self.input_widget.setStyleSheet("border: 1px solid rgb(122,122,122);background-color: rgb(255,255,255)")

        # @TODO: Replace style sheet assignment with a QPalette to retain button state styles
        self.color_select_button = QtWidgets.QToolButton()
        self.color_select_button.setObjectName("non-toolbar")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Icons/Color_Wheel.png"), QtGui.QIcon.Normal)
        icon.addPixmap(QtGui.QPixmap(":/Icons/Color_Wheel_Disabled.png"), QtGui.QIcon.Disabled)
        self.color_select_button.setIcon(icon)
        self.color_select_button.clicked.connect(self.OpenColorPrompt)

        self.main_layout.addWidget(self.input_widget)
        self.main_layout.addWidget(self.color_select_button)

    def Get(self):
        raw_style_sheet = self.input_widget.styleSheet()
        pattern = "background-color: rgb\((.*)\)"

        color = re.search(pattern, raw_style_sheet).group(1)
        self.data["value"] = list(map(int, color.split(",")))
        return self.data

    def Set(self, data):
        css = f"border: 1px solid rgb(122,122,122); background-color: rgb({','.join(map(str, data))})"
        self.input_widget.setStyleSheet(css)

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
            self.SIG_USER_UPDATE.emit(self.owning_model_item)

class InputEntryDropdown(InputEntryBase):
    def __init__(self, data):
        """ A variant of the details entry that uses a pre-set list of options, instead of accepting anything """
        super().__init__(data)

        self.input_widget = QtWidgets.QComboBox()
        self.options = data["options"]

        # Pre-load the list of dropdown options
        for option in self.options:
            self.input_widget.addItem(str(option))

        self.main_layout.addWidget(self.input_widget)

    def Get(self):
        self.data["value"] = self.input_widget.currentText()
        return self.data

    def Set(self, data):
        self.input_widget.setCurrentIndex(self.input_widget.findText(data))

    def Connect(self):
        self.input_widget.currentIndexChanged.connect(lambda: self.SIG_USER_UPDATE.emit(self.owning_model_item))

    def Disconnect(self):
        self.input_widget.disconnect()

    def SetEditable(self, state: int):
        if state == 0:
            self.input_widget.setEnabled(True)
        elif state == 2:
            self.input_widget.setEnabled(False)

        self.input_widget.style().polish(self.input_widget)


class InputEntryFileSelector(InputEntryBase):
    def __init__(self, data, details_panel, type_filter):
        super().__init__(data)

        self.details_panel = details_panel

        # Store a type filter to restrict what files can be chosen in the browser
        self.type_filter = type_filter

        self.input_widget = QtWidgets.QLineEdit()
        self.input_widget.setText("None")

        # Create the file selector button, and style it accordingly
        self.file_select_button = QtWidgets.QToolButton()
        self.file_select_button.setObjectName("non-toolbar")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Icons/Folder.png"), QtGui.QIcon.Normal)
        icon.addPixmap(QtGui.QPixmap(":/Icons/Folder_Disabled.png"), QtGui.QIcon.Disabled)
        self.file_select_button.setIcon(icon)
        self.main_layout.addWidget(self.input_widget)
        self.main_layout.addWidget(self.file_select_button)

        self.file_select_button.clicked.connect(self.OpenFilePrompt)

    def Get(self):
        self.data["value"] = self.input_widget.text()
        return self.data

    def Set(self, data):
        self.input_widget.setText(data)

    def Connect(self):
        self.input_widget.textChanged.connect(lambda: self.SIG_USER_UPDATE.emit(self.owning_model_item))

    def SetEditable(self, state: int):
        if state == 0:
            self.file_select_button.setDisabled(False)
            self.input_widget.setReadOnly(False)
        elif state == 2:
            self.file_select_button.setDisabled(True)
            self.input_widget.setReadOnly(True)

        self.input_widget.style().polish(self.input_widget)

    def OpenFilePrompt(self) -> str:
        #@TODO: Replace file browser will popup list of files available in the project
        """ Prompts the user with a filedialog, accepting an existing file """
        prompt = FileSystemPrompt(self.details_panel)
        existing_file = prompt.GetFile(
            settings.GetProjectContentDirectory(),
            self.type_filter,
            "Choose a File to Open"
        )

        # Did the user choose a value?
        if existing_file:
            selected_dir = existing_file

            # Remove the project dir from the path, so that the selected dir only contains a relative path
            selected_dir = selected_dir.replace(settings.user_project_dir + "/", "")
            self.input_widget.setText(selected_dir)


class InputEntryFloat(InputEntryBase):
    def __init__(self, data):
        super().__init__(data)

        self.input_widget = QtWidgets.QLineEdit()

        # Limit entered values to float only
        self.validator = QtGui.QDoubleValidator()
        self.input_widget.setValidator(self.validator)
        self.input_widget.setText("0.0")
        self.main_layout.addWidget(self.input_widget)

    def Get(self):
        value = self.input_widget.text()

        # Since editing inputs can lead to live updates, the values must always be float castable. Since, as the user
        # edits, it might lead to an empty string or '-', always use 0 as a baseline instead of checking every scenario
        conv_val = 0
        try:
            conv_val = float(value)
        except:
            pass

        self.data["value"] = conv_val
        return self.data

    def Set(self, data):
        self.input_widget.setText(str(data))

    def Connect(self):
        self.input_widget.textEdited.connect(lambda: self.SIG_USER_UPDATE.emit(self.owning_model_item))

    def SetEditable(self, state: int):
        if state == 0:
            self.input_widget.setReadOnly(False)
        elif state == 2:
            self.input_widget.setReadOnly(True)

        self.input_widget.style().polish(self.input_widget)


class InputEntryInt(InputEntryBase):
    def __init__(self, data):
        super().__init__(data)

        self.input_widget = QtWidgets.QLineEdit()

        # Limit entered values to int only
        self.validator = QtGui.QIntValidator()
        self.input_widget.setValidator(self.validator)
        self.input_widget.setText("0")
        self.main_layout.addWidget(self.input_widget)

    def Get(self):
        value = self.input_widget.text()

        # Since editing inputs can lead to live updates, the values must always be int castable. Since, as the user
        # edits, it might lead to an empty string or '-', always use 0 as a baseline instead of checking every scenario
        conv_val = 0
        try:
            conv_val = int(value)
        except:
            pass

        self.data["value"] = conv_val
        return self.data

    def Set(self, data):
        self.input_widget.setText(str(data))

    def Connect(self):
        self.input_widget.textEdited.connect(lambda: self.SIG_USER_UPDATE.emit(self.owning_model_item))

    def SetEditable(self, state: int):
        if state == 0:
            self.input_widget.setReadOnly(False)
        elif state == 2:
            self.input_widget.setReadOnly(True)

        self.input_widget.style().polish(self.input_widget)


class InputEntryParagraph(InputEntryBase):
    def __init__(self,data):
        super().__init__(data)

        self.input_widget = QtWidgets.QPlainTextEdit()
        self.input_widget.setMaximumHeight(100)
        self.main_layout.addWidget(self.input_widget)

    def Get(self):
        self.data["value"] = self.input_widget.toPlainText()
        return self.data

    def Set(self, data):
        # self.input_widget.setPlainText("This is a test string\nI wonder if the line break worked") # DEBUG
        self.input_widget.setPlainText(data)

    def Connect(self):
        self.input_widget.textChanged.connect(lambda: self.SIG_USER_UPDATE.emit(self.owning_model_item))

    def Disconnect(self):
        self.input_widget.disconnect()

    def SetEditable(self, state: int):
        if state == 0:
            self.input_widget.setReadOnly(False)

        elif state == 2:
            self.input_widget.setReadOnly(True)


class InputEntryText(InputEntryBase):
    def __init__(self, data):
        super().__init__(data)

        self.input_widget = QtWidgets.QLineEdit()
        self.main_layout.addWidget(self.input_widget)

    def Get(self):
        self.data["value"] = self.input_widget.text()
        return self.data

    def Set(self, data):
        self.input_widget.setText(data)
        self.input_widget.setCursorPosition(0)

    def Connect(self):
        self.input_widget.textEdited.connect(lambda: self.SIG_USER_UPDATE.emit(self.owning_model_item))

    def SetEditable(self, state: int):
        if state == 0:
            self.input_widget.setReadOnly(False)
        elif state == 2:
            self.input_widget.setReadOnly(True)

        self.input_widget.style().polish(self.input_widget)


class InputEntryTuple(InputEntryBase):
    def __init__(self, data):
        super().__init__(data)

        #@TODO: Make this two floats, not two ints
        self.input_widget_title = QtWidgets.QLabel('X')
        self.input_widget = QtWidgets.QLineEdit()

        self.input_widget_alt_title = QtWidgets.QLabel('Y')
        self.input_widget_alt = QtWidgets.QLineEdit()

        # Limit entered values to int only
        validator = QtGui.QDoubleValidator(-2, 2, 8, notation=QtGui.QDoubleValidator.StandardNotation)
        self.input_widget.setValidator(validator)
        self.input_widget_alt.setValidator(validator)
        self.input_widget.setText("0")
        self.input_widget_alt.setText("0")

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

        self.data["value"] = [conv_x, conv_y]
        return self.data

    def Set(self, data):
        self.input_widget.setText(str(data[0]))
        self.input_widget_alt.setText(str(data[1]))
        self.input_widget.setCursorPosition(0)
        self.input_widget_alt.setCursorPosition(0)

    def Connect(self):
        self.input_widget.textEdited.connect(lambda: self.SIG_USER_UPDATE.emit(self.owning_model_item))
        self.input_widget_alt.textEdited.connect(lambda: self.SIG_USER_UPDATE.emit(self.owning_model_item))

    def SetEditable(self, state: int):
        if state == 0:
            self.input_widget.setReadOnly(False)
            self.input_widget_alt.setReadOnly(False)
        elif state == 2:
            self.input_widget.setReadOnly(True)
            self.input_widget_alt.setReadOnly(True)

        self.input_widget.style().polish(self.input_widget)
        self.input_widget_alt.style().polish(self.input_widget_alt)


class InputEntryArray(InputEntryBase):
    """
    A highly specialized container that allows the generation of child entries based on a template defined in
    the ActionsDatabase
    """
    def __init__(self, data: dict, owning_view: QtWidgets.QAbstractItemView,
                 add_func: callable, signal_func: callable, refresh_func: callable,
                 excluded_properties: dict = None):
        super().__init__(data)
        self.excluded_properties = excluded_properties
        self.owning_view = owning_view

        self.child_limit = 6

        # We need access to the return value of the created view item, so we must use a callback instead of a
        # signal / slot (Which don't allow return values)
        self.add_func = add_func
        self.signal_func = signal_func
        self.refresh_func = refresh_func

        self.main_layout.setAlignment(QtCore.Qt.AlignLeft)

        self.add_item_button = QtWidgets.QToolButton()
        self.add_item_button.setObjectName("choice-add")
        self.add_item_button.clicked.connect(lambda: self.AddItems())
        self.main_layout.addWidget(self.add_item_button)

    def AddItems(self, data=None, parent=None):
        if self.owning_model_item.childCount() >= self.child_limit:
            Logger.getInstance().Log("Unable to add more elements - Limit Reached!", 3)
        else:
            if not data:
                data = copy.deepcopy(self.data["template"])
            if not parent:
                parent = self.owning_model_item

            #@TODO: Investigate how to incorporate this functionality with saving / loading
            new_entry = self.add_func(
                owner=self,
                view=self.owning_view,
                data=data,
                parent=parent,
                excluded_properties=self.excluded_properties,
                signal_func=self.signal_func,
                refresh_func=self.refresh_func
            )

            if "children" in data:
                for child_data in data["children"]:
                    self.AddItems(child_data, new_entry)

        # Inform the owning U.I that we've added a child outside it's purview
        self.refresh_func(self.owning_model_item)


class InputEntryArrayElement(InputEntryBase):
    SIG_USER_DELETE = QtCore.pyqtSignal(object)

    def __init__(self, data):
        super().__init__(data)

        # Delete button
        self.delete_button = QtWidgets.QToolButton()
        self.delete_button.setObjectName("choice-remove")
        self.main_layout.addWidget(self.delete_button)

        self.delete_button.clicked.connect(lambda: self.SIG_USER_DELETE.emit(self.owning_model_item))


class InputEntryResolution(InputEntryBase):
    """
    An alternative to the regular dropdown customized to support the project's resolution settings

    The resolution settings are divided into two settings:
    - An int input representing the index of the selected resolution
    - A specialized dropdown of resolution choices

    When the latter is changed, the former needs to be updated as well. Instead of trying to build
    a system for handling input entries communicating to eachother, this widget directly references the project
    settings, so it can go and update the former at its leisure
    """

    def __init__(self, data):
        super().__init__(data)
        self.input_widget = QtWidgets.QComboBox()

        # Example value for 'data':
        # {'name': 'resolution_options', 'type': 'CUST_Resolution', 'value': [[1280, 720], [1920, 1080]]}
        for option in self.data["value"]:
            self.input_widget.addItem(str(option))

        # Use the value of the "Int" widget mentioned in the class docstring to switch the active option
        self.input_widget.setCurrentIndex(settings.user_project_data["Window"]["resolution"])

        self.main_layout.addWidget(self.input_widget)

    def Set(self, data):
        self.data["value"] = data

    def Get(self):
        # Typically, this function is used when retrieving the data and storing it somewhere. Since this entry is
        # technically representing 2 different values, only the resolution option would be stored, not the associated
        # index value.
        #
        # To account for this, let's store the index value before we return the list of options
        settings.user_project_data["Window"]["resolution"] = self.input_widget.currentIndex()

        return self.data
