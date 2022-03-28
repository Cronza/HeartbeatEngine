from PyQt5.QtWidgets import QWidget
from HBEditor.Core.DataTypes.parameter_types import ParameterType
from HBEditor.Core.Primitives.input_entries_test import *


def Add(owner: QWidget, data: dict, entry_updated_func: object, excluded_entries: dict = None):
        print("Adding via the handler")

        if excluded_entries:
            if not data["name"] in excluded_entries:
                pass
                # Create a new entry, and add it to the details list
                #self.AddEntry(self.CreateEntryWidget(requirement))

def Create(owner: QWidget, data: dict, entry_updated_func):
    # @TODO: Replace with a switch when the Python version is upgraded to allow it

    data_type = ParameterType[data["type"]]

    new_entry = None
    if data_type == ParameterType.String:
        new_entry = InputEntryText()
    elif data_type == ParameterType.Paragraph:
        new_entry = InputEntryParagraph()
    elif data_type == ParameterType.Vector2:
        new_entry = InputEntryTuple()
    elif data_type == ParameterType.Bool:
        new_entry = InputEntryBool()
    elif data_type == ParameterType.Color:
        new_entry = InputEntryColor()
    elif data_type == ParameterType.Int:
        new_entry = InputEntryInt()
    elif data_type == ParameterType.Float:
        new_entry = InputEntryFloat()
    elif data_type == ParameterType.File_Data:
        new_entry = InputEntryFileSelector(owner, Settings.getInstance().supported_content_types["Data"])
    elif data_type == ParameterType.File_Image:
        new_entry = InputEntryFileSelector(owner, Settings.getInstance().supported_content_types["Image"])
    elif data_type == ParameterType.File_Font:
        new_entry = InputEntryFileSelector(owner, Settings.getInstance().supported_content_types["Font"])
    elif data_type == ParameterType.File_Sound:
        new_entry = InputEntryFileSelector(owner, Settings.getInstance().supported_content_types["Sound"])
    elif data_type == ParameterType.Dropdown:
        new_entry = InputEntryDropdown(data['options'])
    #elif data_type == ParameterType.Choice:
    #    new_entry = InputEntryChoice(data, self.AddEntry, self.CreateEntryWidget, self.branch_list,
    #                            self.DetailEntryUpdated)
    #elif data_type == ParameterType.Container:
    #    new_entry = InputEntryContainer(data['children'])
    #    for child in data['children']:
    #        new_entry.addChild(self.CreateEntryWidget(child))

    #    return new_entry

    new_entry.Connect(entry_updated_func)

def Clear(tree):
    tree.clear()




def Remove():
    pass

def Set():
    pass

def Get():
    pass


