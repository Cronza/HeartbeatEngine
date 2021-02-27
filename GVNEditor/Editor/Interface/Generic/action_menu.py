from PyQt5 import QtWidgets, QtGui
from Editor.Interface.Generic.action_menu_option import ActionMenuOption


class ActionMenu(QtWidgets.QMenu):
    def __init__(self, settings, button_func):
        super().__init__()

        # Set the root styling for sub menus
        self.setFont(settings.button_font)
        self.setStyleSheet(settings.button_color)

        # Build the list of action options
        self.action_database = settings.action_database

        for category, data in self.action_database.items():
            # Build the category object and assign it
            cat_menu = QtWidgets.QMenu(self)
            cat_menu.setTitle(category)
            cat_menu.setIcon(QtGui.QIcon(data['icon']))
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
