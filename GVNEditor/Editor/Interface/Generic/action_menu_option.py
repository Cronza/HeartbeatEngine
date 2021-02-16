from PyQt5 import QtWidgets


class ActionMenuOption(QtWidgets.QWidgetAction):
    def __init__(self, parent, action_data, func):
        super().__init__(parent)

        # Store this entries action data
        self.action_data = action_data

        # Hook this button up
        self.triggered.connect(lambda button: func(self.action_data))
