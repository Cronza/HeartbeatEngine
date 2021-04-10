from PyQt5 import QtWidgets, QtGui


class DialogueEntry(QtWidgets.QWidget):
    def __init__(self, action_data, settings, select_func):
        super().__init__()
        self.settings = settings

        # Store a func object that is used when this entry is selected
        self.select_func = select_func

        # Store this entries action data
        self.action_data = action_data

        # ****** DISPLAY WIDGETS ******
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Name
        self.name_widget = QtWidgets.QLabel()
        self.name_widget.setFont(settings.header_2_font)
        self.name_widget.setStyleSheet(settings.header_2_color)
        self.name_widget.setText(self.action_data['display_name'])

        # Details
        self.subtext_widget = QtWidgets.QLabel()
        self.subtext_widget.setFont(settings.subtext_font)
        self.subtext_widget.setStyleSheet(settings.subtext_color)

        # Refresh the subtext
        self.UpdateSubtext()

        # Add everything to the layout
        self.main_layout.addWidget(self.name_widget)
        self.main_layout.addWidget(self.subtext_widget)

    def UpdateSubtext(self):
        """ Updates the subtext displaying entry parameters """
        # Clear text
        self.subtext_widget.setText("")

        # Populate the subtext with all params that have preview enabled
        for param in self.action_data['requirements']:
            if param['preview']:

                # If cached data is available, use it. Otherwise display the default
                param_name = param['name']
                param_data = None
                if 'cache' in param:
                    param_data = param['cache']
                else:
                    param_data = param['default']

                # If we've already started building the string, our concatenation will be a bit different
                cur_text = self.subtext_widget.text()
                if cur_text:
                    self.subtext_widget.setText(cur_text + f", {param_name}: {param_data}")
                else:
                    self.subtext_widget.setText(cur_text + f"{param_name}: {param_data}")

    def Refresh(self):
        """
        Refresh is the common function used by elements that need refreshing when an important U.I change is made
        """

        self.UpdateSubtext()
