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
from PyQt5 import QtWidgets, QtGui
from HBEditor.Interface.Menus.ActionMenu.action_menu_option import ActionMenuOption

#@TODO: Should this class be split into a function class & a U.I class?

""" 
A generic menu of categories and actions that the active editor can use. 'button' func is used when any menu option
is clicked. 'available_actions' is a set of actions pulled from the ActionsDatabase that will represent what's available
in the menu 
"""
class ActionMenu(QtWidgets.QMenu):
    def __init__(self, settings, button_func, available_actions):
        super().__init__()

        # Set the root styling for sub menus
        self.setFont(settings.button_font)
        self.setStyleSheet(settings.button_color)

        for category, data in available_actions.items():
            # Build the category object and assign it
            cat_menu = QtWidgets.QMenu(self)
            cat_menu.setTitle(category)
            cat_menu.setIcon(QtGui.QIcon(settings.editor_root + "/" + data["icon"]))
            cat_menu.setFont(settings.button_font)
            cat_menu.setStyleSheet(settings.button_color)
            self.addMenu(cat_menu)

            # Generate a list of options for this category
            for action in data['options']:
                option = ActionMenuOption(self, action, button_func)
                option.setFont(settings.button_font)
                #option.setStyleSheet(settings.button_color) @TODO: Find out why this doesn't work
                option.setText(action['display_name'])
                cat_menu.addAction(option)
