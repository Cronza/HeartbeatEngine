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
from PyQt5.QtWidgets import QWidget, QTreeView, QTreeWidgetItem, QLabel
from HBEditor.Core.Primitives.simple_checkbox import SimpleCheckbox
from HBEditor.Core.DataTypes.parameter_types import ParameterType
from HBEditor.Core.Primitives.input_entries_test import *


def Add(owner: QWidget, data: dict, tree: QTreeView,
        parent: QTreeWidgetItem = None, excluded_entries: dict = None) -> QTreeWidgetItem:
    """
    Adds a new InputEntry into the provided QTreeView. If a parent is provided, the InputEntry
    is added as a child to it instead. Returns the QTreeWidgetItem containing the InputEntry
    """

    if excluded_entries:
        if data["name"] in excluded_entries:
            return None

    entry = QTreeWidgetItem()
    if parent:
        parent.addChild(entry)
    else:
        tree.addTopLevelItem(entry)

    name_widget, input_widget, global_checkbox = Create(owner, data, entry)
    tree.setItemWidget(entry, 0, name_widget)
    tree.setItemWidget(entry, 1, input_widget)

    # The global checkbox isn't universally used, so only use it if relevant. If it's enabled, mark
    # the input widget as uneditable by the user
    if "global" in data:
        tree.setItemWidget(entry, 2, global_checkbox)
        if data["global"]["active"] == True:
            global_checkbox.Set(True)
            input_widget.SetEditable(2)
        else:
            global_checkbox.Set(False)

        global_checkbox.Connect()

    return entry


def Create(owner: QWidget, data: dict, owning_tree_item: QTreeWidgetItem) -> object:
    """
    Creates and returns each element of an entry in an Input Entry model:
    - QLabel (Name)
    - InputEntry
    - Global Checkbox (SimpleCheckbox)
    """
    # @TODO: Replace with a switch when the Python version is upgraded to allow it

    data_type = ParameterType[data["type"]]

    # Create the core input widget (Col 2)
    input_widget = None
    if data_type == ParameterType.String:
        input_widget = InputEntryText()
    elif data_type == ParameterType.Paragraph:
        input_widget = InputEntryParagraph()
    elif data_type == ParameterType.Vector2:
        input_widget = InputEntryTuple()
    elif data_type == ParameterType.Bool:
        input_widget = InputEntryBool()
    elif data_type == ParameterType.Color:
        input_widget = InputEntryColor()
    elif data_type == ParameterType.Int:
        input_widget = InputEntryInt()
    elif data_type == ParameterType.Float:
        input_widget = InputEntryFloat()
    elif data_type == ParameterType.File_Data:
        input_widget = InputEntryFileSelector(owner, Settings.getInstance().supported_content_types["Data"])
    elif data_type == ParameterType.File_Image:
        input_widget = InputEntryFileSelector(owner, Settings.getInstance().supported_content_types["Image"])
    elif data_type == ParameterType.File_Font:
        input_widget = InputEntryFileSelector(owner, Settings.getInstance().supported_content_types["Font"])
    elif data_type == ParameterType.File_Sound:
        input_widget = InputEntryFileSelector(owner, Settings.getInstance().supported_content_types["Sound"])
    elif data_type == ParameterType.Dropdown:
        input_widget = InputEntryDropdown(data['options'])
    elif data_type == ParameterType.Container:
        input_widget = InputEntryBase()
    #elif data_type == ParameterType.Choice:
    #    input_widget = InputEntryChoice(data, self.AddEntry, self.CreateEntryWidget, self.branch_list,
    #                            self.DetailEntryUpdated)

    # Types like containers don't use the value key
    if "value" in data:
        input_widget.Set(data["value"])

    input_widget.owning_tree_item = owning_tree_item
    input_widget.Connect()

    # Create the secondary widgets (Col 1 & 3)
    name_widget = QLabel(data["name"])
    global_checkbox = SimpleCheckbox()
    global_checkbox.owner = owning_tree_item
    global_checkbox.setToolTip("Whether to use the global value specified in the project file for this entry")

    return name_widget, input_widget, global_checkbox


def Clear(tree):
    tree.clear()
