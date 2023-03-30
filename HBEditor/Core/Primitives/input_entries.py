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
from HBEditor.Core.Logger.logger import Logger
from HBEditor.Core.EditorUtilities import action_data as adh
from HBEditor.Core.Dialogs.asset_browser import AssetBrowser

"""
List of available entries:
    - InputEntryBool
    - InputEntryColor
    - InputEntryDropdown
    - InputEntryAssetSelector
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


class InputEntryAssetSelector(InputEntryBase):
    def __init__(self, data: dict, details_panel: object, type_filter: list):
        super().__init__(data)

        self.details_panel = details_panel

        # Store a type filter to restrict what assets can be chosen in the browser
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

        self.file_select_button.clicked.connect(self.OpenAssetPrompt)

        # Paths are handled using the asset registry. Prevent the user from editing these paths manually
        self.input_widget.setReadOnly(True)

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
        elif state == 2:
            self.file_select_button.setDisabled(True)

        self.input_widget.style().polish(self.input_widget)

    def OpenAssetPrompt(self):
        """
        Prompts the user with the AssetBrowser, allowing them to select an asset matching the type
        for this object
        """
        asset_browser = AssetBrowser(self.type_filter)
        asset_path = asset_browser.GetAsset()
        if asset_path:
            self.input_widget.setText(asset_path)

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
    the actions_metadata
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

        # In order for the data to be recursively parsed, we need the 'children' key
        if "children" not in self.data:
            self.data["children"] = {}

        self.main_layout.setAlignment(QtCore.Qt.AlignLeft)

        self.add_item_button = QtWidgets.QToolButton()
        self.add_item_button.setObjectName("choice-add")
        self.add_item_button.clicked.connect(lambda: self.AddItems())
        self.main_layout.addWidget(self.add_item_button)

    def AddItems(self, name="", data=None, parent=None):
        if self.owning_model_item.childCount() >= self.child_limit and not data:  # Don't run when recursing
            Logger.getInstance().Log("Unable to add more elements - Limit Reached!", 3)
        else:
            if not data:
                data = copy.deepcopy(self.data["template"])

                # Array elements have generated names to avoid having to be stored as a list when caching or saving
                name = f"{adh.GetActionName(data)}_{self.owning_model_item.childCount()}"

            if not parent:
                parent = self.owning_model_item

            data_no_key = data[adh.GetActionName(data)]

            new_entry = self.add_func(
                owner=self,
                view=self.owning_view,
                name=name,
                data=data_no_key,
                parent=parent,
                excluded_properties=self.excluded_properties,
                signal_func=self.signal_func,
                refresh_func=self.refresh_func
            )
            if "children" in data_no_key:
                for child_name, child_data in data_no_key["children"].items():
                    if "editable" in child_data:
                        if not child_data["editable"]:
                            continue

                    self.AddItems(child_name, {child_name: child_data}, new_entry)

        if not parent:
            # Inform the owning U.I that we've added a child outside it's purview. Only do this once all recursion
            # is done
            self.refresh_func(self.owning_model_item)


class InputEntryArrayElement(InputEntryBase):
    SIG_USER_DELETE = QtCore.pyqtSignal(object, object)

    def __init__(self, data, owning_view: QtWidgets.QAbstractItemView):
        super().__init__(data)

        # Store a reference to the owning view in order to inform it when we're deleted, so the parent InputEntryArray
        # can recalculate its entries
        self.owning_view = owning_view

        # Delete button
        self.delete_button = QtWidgets.QToolButton()
        self.delete_button.setObjectName("choice-remove")
        self.main_layout.addWidget(self.delete_button)

        self.delete_button.clicked.connect(lambda: self.SIG_USER_DELETE.emit(self.owning_model_item, self.owning_view))


class InputEntryEvent(InputEntryBase):
    """
    A variant of the dropdown entry that uses a pre-set list of options which refer to an action in the
    actions_metadata. Once an option is selected, all properties related to that action are generated as children
    to this entry
    """
    def __init__(self, data: dict, owning_view: QtWidgets.QAbstractItemView,
                 add_func: callable, remove_func: callable, signal_func: callable, refresh_func: callable,
                 excluded_properties: dict = None):
        super().__init__(data)

        self.excluded_properties = []
        self.owning_view = owning_view

        # We need access to the return value of the created view item, so we must use a callback instead of a
        # signal / slot (Which don't allow return values)
        self.add_func = add_func
        self.remove_func = remove_func
        self.signal_func = signal_func
        self.refresh_func = refresh_func

        self.input_widget = QtWidgets.QComboBox()

        # In order for the data to be recursively parsed, we need the 'children' key
        if "children" not in self.data:
            self.data["children"] = {}

        # Pre-load the list of dropdown options
        self.options = data["options"]
        for option in self.options:
            self.input_widget.addItem(str(option))

        self.main_layout.addWidget(self.input_widget)

    def ChangeEvent(self):
        """ Switch the event, clearing all children and generating new ones """
        # Delete all existing children, as they're based on the active selection
        for i in range(self.owning_model_item.childCount()):
            self.remove_func(self.owning_model_item.child(0))
        self.data["children"].clear()

        if self.input_widget.currentText() != "None":
            # Since the entry children are properties of the action specified in the input_widget, we also need to specify
            # the action's name. This doesn't come as a part of the metadata clone, so we need to add the key manually
            #
            # For all intents and purposes, this doesn't need to be edited by the user, so we're opting out of adding it as
            # a visible entry, and instead writing it directly into the action_data
            self.data["children"]["action"] = {
                "type": "String",
                "value": self.input_widget.currentText()
            }

            # Grab the metadata for the event action, and generate children for all of its properties
            metadata = copy.deepcopy(settings.action_metadata[self.input_widget.currentText()])
            if metadata["requirements"]:
                self.AddItems(metadata["requirements"])

    def AddItems(self, req_data=None, parent=None):
        if not parent:
            parent = self.owning_model_item

        for name, data in req_data.items():
            # Some editors exclude certain requirements (IE. Point & Click doesn't make use of 'post_wait')
            if self.excluded_properties:
                if name in self.excluded_properties:
                    continue

            new_entry = self.add_func(
                owner=self,
                view=self.owning_view,
                name=name,
                data=data,
                parent=parent,
                excluded_properties=self.excluded_properties,
                signal_func=self.signal_func,
                refresh_func=self.refresh_func
            )
            if "children" in data:
                for child_name, child_data in data["children"].items():
                    if "editable" in child_data:
                        if not child_data["editable"]:
                            continue

                    self.AddItems(child_name, {child_name: child_data}, new_entry)

        if not parent:
            # Inform the owning U.I that we've added a child outside it's purview. Only do this once all recursion
            # is done
            self.refresh_func(self.owning_model_item)

    def Get(self):
        self.data["value"] = self.input_widget.currentText()
        return self.data

    def Set(self, data):
        if data:
            self.input_widget.setCurrentIndex(self.input_widget.findText(data))
        else:
            self.input_widget.setCurrentIndex(0)

    def Connect(self):
        self.input_widget.activated.connect(self.ChangeEvent)  # 'activated' only happens on user interaction
        self.input_widget.currentIndexChanged.connect(lambda: self.SIG_USER_UPDATE.emit(self.owning_model_item))

    def Disconnect(self):
        self.input_widget.disconnect()

    def SetEditable(self, state: int):
        if state == 0:
            self.input_widget.setEnabled(True)
        elif state == 2:
            self.input_widget.setEnabled(False)

        self.input_widget.style().polish(self.input_widget)


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
