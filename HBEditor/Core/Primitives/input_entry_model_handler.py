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
from PyQt5.QtWidgets import QWidget, QTreeWidgetItem, QLabel
from HBEditor.Core.Primitives.simple_checkbox import SimpleCheckbox
from HBEditor.Core.DataTypes.parameter_types import ParameterType
from HBEditor.Core.Primitives.input_entries_test import *


def Add(owner: QWidget, data: dict, view: QtWidgets.QAbstractItemView,
        parent: QTreeWidgetItem = None, excluded_entries: dict = None,
        signal_func: callable = None, refresh_func: callable = None) -> QTreeWidgetItem:
    """
    Adds a new InputEntry into the provided QAbstractItemModel, along with its name and global checkbox elements.
    If a parent is provided, the elements are added as a child to it instead. Returns the QTreeWidgetItem
    containing the elements

    If 'signal_func' is provided, then:
    - Invoke it when we insert the QTreeWidgetItem into the tree (So the caller can connect the appropriate signals)
    - Pass by ref to any entries that have the ability to create child entries (So they can be connected properly)

    If "refresh_func" is provided, provide it to any entries that may perform actions later on that require
    the caller to know about it. When they call it, they'll provide their owning widget item
    """

    if excluded_entries:
        if data["name"] in excluded_entries:
            return None

    entry = QTreeWidgetItem()
    if parent:
        parent.addChild(entry)
    else:
        view.addTopLevelItem(entry)

    name_widget, input_widget, global_checkbox = Create(
        owner, data, entry, view, signal_func, refresh_func, excluded_entries
    )
    view.setItemWidget(entry, 0, name_widget)
    view.setItemWidget(entry, 1, input_widget)

    if signal_func:
        signal_func(entry)

    return entry


def Create(owner: QWidget, data: dict, owning_model_item: QTreeWidgetItem,
           owning_view: QtWidgets.QAbstractItemView, signal_func: callable = None,
           refresh_func: callable = None, excluded_entries: dict = None) -> object:
    """
    Creates and returns each element of an InputEntry:
    - QLabel (Name)
    - InputEntry
    - Global Checkbox (SimpleCheckbox)
    """
    # @TODO: Replace with a switch when the Python version is upgraded to allow it
    data_type = ParameterType[data["type"]]

    input_widget = None
    if data_type == ParameterType.String:
        input_widget = InputEntryText(data)
    elif data_type == ParameterType.Paragraph:
        input_widget = InputEntryParagraph(data)
    elif data_type == ParameterType.Vector2:
        input_widget = InputEntryTuple(data)
    elif data_type == ParameterType.Bool:
        input_widget = InputEntryBool(data)
    elif data_type == ParameterType.Color:
        input_widget = InputEntryColor(data)
    elif data_type == ParameterType.Int:
        input_widget = InputEntryInt(data)
    elif data_type == ParameterType.Float:
        input_widget = InputEntryFloat(data)
    elif data_type == ParameterType.File_Data:
        input_widget = InputEntryFileSelector(data, owner, Settings.getInstance().supported_content_types["Data"])
    elif data_type == ParameterType.File_Image:
        input_widget = InputEntryFileSelector(data, owner, Settings.getInstance().supported_content_types["Image"])
    elif data_type == ParameterType.File_Font:
        input_widget = InputEntryFileSelector(data, owner, Settings.getInstance().supported_content_types["Font"])
    elif data_type == ParameterType.File_Sound:
        input_widget = InputEntryFileSelector(data, owner, Settings.getInstance().supported_content_types["Sound"])
    elif data_type == ParameterType.Dropdown:
        input_widget = InputEntryDropdown(data)
    elif data_type == ParameterType.Container:
        input_widget = InputEntryBase(data)
    elif data_type == ParameterType.Closable_Container:
        input_widget = InputEntryClosableContainer(data)
        input_widget.SIG_USER_DELETE.connect(Remove)
    elif data_type == ParameterType.Array:
        input_widget = InputEntryArray(data, owning_view, Add, signal_func, refresh_func, excluded_entries)

    input_widget.owning_model_item = owning_model_item
    input_widget.Connect()

    # Update the entry with the value key if available, or using the entire data block
    if "value" in data:
        input_widget.Set(data["value"])
    else:
        input_widget.Set(data)

    name_widget = QLabel(data["name"])
    global_checkbox = SimpleCheckbox()
    global_checkbox.owner = owning_model_item
    global_checkbox.setToolTip("Whether to use the global value specified in the project file for this entry")

    # The global checkbox isn't universally used, so only use it if relevant. If it's enabled, mark
    # the input widget as uneditable by the user
    if "global" in data:
        owning_view.setItemWidget(owning_model_item, 2, global_checkbox)
        if data["global"]["active"]:
            global_checkbox.Set(True)
            input_widget.SetEditable(2)
        else:
            global_checkbox.Set(False)

        global_checkbox.Connect()

    return name_widget, input_widget, global_checkbox


def Remove(item: QTreeWidgetItem):
    parent = item.parent()
    if parent:
        parent.removeChild(item)


def Clear(tree):
    tree.clear()
