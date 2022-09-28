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
import copy
from PyQt5 import QtWidgets, QtGui, QtCore
from HBEditor.Core import settings
from HBEditor.Core.DataTypes.file_types import FileType
from HBEditor.Core.Menus.ActionMenu.action_menu_option import ActionMenuOption

#@TODO: Should this class be split into a function class & a U.I class?


class ActionMenu(QtWidgets.QMenu):
    """
    A generic menu of categories and actions that the active editor can use. 'button' func is used when any menu option
    is clicked. 'available_actions' is a set of actions pulled from the action_metadata that will represent what's available
    in the menu
    """
    def __init__(self, button_func, editor_type: FileType):
        super().__init__()

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.NoDropShadowWindowHint)

        for category, data in settings.editor_action_metadata.items():
            # Create the category submenu
            cat_menu = QtWidgets.QMenu(self)
            cat_menu.setTitle(category)
            cat_menu.setIcon(QtGui.QIcon(data["icon"]))

            # Populate the category submenu
            for option_data in data['options']:
                for applicable_editor in option_data["applicable_editors"]:
                    if FileType[applicable_editor] == editor_type:
                        # The top level action name key gets removed when we try and access the data it contains. When
                        # we go to pass the metadata copy to the option, re-add this key
                        metadata_copy = copy.deepcopy(settings.action_metadata[option_data["name"]])
                        option = ActionMenuOption(self, {option_data["name"]: metadata_copy}, button_func)
                        option.setText(metadata_copy['display_name'])
                        cat_menu.addAction(option)
                        break

            # Only use the menu if there were any actions that are allowed for this editor type
            if len(cat_menu.actions()) > 0:
                self.addMenu(cat_menu)
