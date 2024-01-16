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
from PyQt6.QtWidgets import QWidget, QTreeWidgetItem, QLabel
from HBEditor.Core.Primitives.simple_checkbox import SimpleCheckbox
from HBEditor.Core.DataTypes.parameter_types import ParameterType
from HBEditor.Core.DataTypes.file_types import FileType
from HBEditor.Core.Primitives.input_entries import *


def Add(owner: QWidget, name: str, data: dict, view: QtWidgets.QTreeView,
        parent: QTreeWidgetItem = None, excluded_properties: list = None,
        signal_func: callable = None, refresh_func: callable = None) -> QTreeWidgetItem:
    """
    Adds a new InputEntry into the provided QTreeView, along with its name and global checkbox elements.
    If a parent is provided, the elements are added as a child to it instead. Returns the QTreeWidgetItem
    containing the elements

    If 'signal_func' is provided, then:
    - Invoke it when we insert the QTreeWidgetItem into the tree (So the caller can connect the appropriate signals)
    - Pass by ref to any entries that have the ability to create child entries (So they can be connected properly)

    If "refresh_func" is provided, provide it to any entries that may perform actions later on that require
    the caller to know about it. When they call it, they'll provide their owning widget item
    """

    entry = QTreeWidgetItem()
    if parent:
        parent.addChild(entry)
    else:
        view.addTopLevelItem(entry)

    name_widget, input_widget, global_checkbox = Create(
        owner, name, data, entry, view, signal_func, refresh_func, excluded_properties
    )
    view.setItemWidget(entry, 0, name_widget)
    view.setItemWidget(entry, 1, input_widget)

    if signal_func:
        signal_func(entry)

    return entry


def Create(owner: QWidget, name: str, data: dict, owning_model_item: QTreeWidgetItem,
           owning_view: QtWidgets.QAbstractItemView, signal_func: callable = None,
           refresh_func: callable = None, excluded_properties: dict = None) -> object:
    """
    Creates and returns each element of an InputEntry:
    - QLabel (Name)
    - InputEntry
    - Global Checkbox (SimpleCheckbox)
    """
    # @TODO: Replace with a switch when the Python version is upgraded to allow it (3.10)
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
    elif data_type == ParameterType.Dropdown:
        input_widget = InputEntryDropdown(data)
    elif data_type == ParameterType.Container:
        input_widget = InputEntryBase(data)
    elif data_type == ParameterType.Array_Element:
        input_widget = InputEntryArrayElement(data, owning_view)
        input_widget.SIG_USER_DELETE.connect(Remove)
    elif data_type == ParameterType.Array:
        input_widget = InputEntryArray(data, owning_view, Add, signal_func, refresh_func, excluded_properties)
    elif data_type == ParameterType.Event:
        input_widget = InputEntryEvent(data, owning_view, Add, Remove, signal_func, refresh_func, excluded_properties)
    elif data_type == ParameterType.CUST_Resolution:
        input_widget = InputEntryResolution(data)

        # Asset selectors
    elif data_type == ParameterType.Asset_Scene:
        input_widget = InputEntryAssetSelector(data, owner, {FileType.Scene})
    elif data_type == ParameterType.Asset_Dialogue:
        input_widget = InputEntryAssetSelector(data, owner, {FileType.Dialogue})
    elif data_type == ParameterType.Asset_Interface:
        input_widget = InputEntryAssetSelector(data, owner, {FileType.Interface})
    elif data_type == ParameterType.Asset_Data:
        input_widget = InputEntryAssetSelector(data, owner, {FileType.Asset_Data})
    elif data_type == ParameterType.Asset_Image:
        input_widget = InputEntryAssetSelector(data, owner, {FileType.Asset_Image})
    elif data_type == ParameterType.Asset_Font:
        input_widget = InputEntryAssetSelector(data, owner, {FileType.Asset_Font})
    elif data_type == ParameterType.Asset_Sound:
        input_widget = InputEntryAssetSelector(data, owner, {FileType.Asset_Sound})

    input_widget.owning_model_item = owning_model_item
    input_widget.Connect()

    # Update the entry with the value key if applicable. Otherwise, use the default value
    if "value" in data:
        input_widget.Set(data["value"])
    elif "default" in data:
        data["value"] = data["default"]
        input_widget.Set(data["value"])

    name_widget = QLabel(name)

    # The global checkbox isn't universally used, so only use it if relevant. If it's enabled, mark
    # the input widget as uneditable by the user
    global_checkbox = None
    if "global" in data and "flags" in data:
        global_checkbox = SimpleCheckbox()
        global_checkbox.owner = owning_model_item
        global_checkbox.setToolTip("Whether to use the global value specified in the project file for this entry")
        owning_view.setItemWidget(owning_model_item, 2, global_checkbox)
        if "global_active" in data["flags"]:
            global_checkbox.Set(True)
            input_widget.SetEditable(2)
        else:
            global_checkbox.Set(False)

        global_checkbox.Connect()
        global_checkbox.SIG_USER_UPDATE.connect(refresh_func)

    return name_widget, input_widget, global_checkbox


def Remove(item: QTreeWidgetItem, owning_view: QtWidgets.QAbstractItemView = None):
    parent = item.parent()
    if parent:
        parent.removeChild(item)

    if owning_view:
        parent_input_widget = owning_view.itemWidget(parent, 1)
        if isinstance(parent_input_widget, InputEntryArray):
            # ArrayElements need to inform their owning array when they are deleted in order to recalculate properly
            for child_index in range(0, parent.childCount()):
                array_element = parent.child(child_index)
                name_widget = owning_view.itemWidget(array_element, 0)

                # We need to fetch the index that is a part of the name (IE. 'choice_01'). Just in case the name
                # makes use of more than one '_', only fetch the last instance as the delimiter
                name_split = name_widget.text().split("_")
                name_split.pop(-1)
                name_widget.setText("_".join(name_split) + f"_{child_index}")
