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
from PyQt6 import QtWidgets, QtGui, QtCore
from HBEditor.Core import settings
from HBEditor.Core.DataTypes.file_types import FileType


class ActionMenu(QtWidgets.QMenu):
    """
    A generic menu of categories and actions that the active editor can use. 'button' func is used when any menu option
    is clicked.
    """
    def __init__(self, button_func, editor_type: FileType):
        super().__init__()

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowType.NoDropShadowWindowHint)

        for category, data in settings.available_actions.items():
            # Create the category submenu
            cat_menu = QtWidgets.QMenu(self)
            cat_menu.setTitle(category)
            cat_menu.setIcon(QtGui.QIcon(data["icon"]))

            # Populate the category submenu
            for option_data in data['options']:
                for applicable_editor in option_data["applicable_editors"]:
                    if FileType[applicable_editor] == editor_type:
                        option = ActionMenuOption(self, option_data['name'], option_data['display_name'])
                        option.SIG_USER_CLICKED.connect(button_func)
                        cat_menu.addAction(option)
                        break

            # Only use the menu if there were any actions that are allowed for this editor type
            if len(cat_menu.actions()) > 0:
                self.addMenu(cat_menu)


class ActionMenuOption(QtWidgets.QWidgetAction):
    SIG_USER_CLICKED = QtCore.pyqtSignal(str)

    def __init__(self, parent, action_name: str, display_name: str):
        super().__init__(parent)

        self.action_name = action_name  # The real action name, separate from the user-facing display name
        self.setText(display_name)
        self.triggered.connect(lambda: self.SIG_USER_CLICKED.emit(self.action_name))
