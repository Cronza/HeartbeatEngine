from PyQt5 import QtWidgets, QtGui


class DialogueEntry(QtWidgets.QTableWidgetItem):
    def __init__(self, action_data, settings, select_func):
        super().__init__()

        # Store a func object that is used when this entry is selected
        self.select_func = select_func

        # Store this entries action data
        self.action_data = action_data

        # Initialize data
        self.setFont(settings.button_font)
        self.setText(self.action_data['display_name'])
