from PyQt5 import QtWidgets, QtGui


class DialogueEntry(QtWidgets.QWidget):
    def __init__(self, action_data, settings, select_func):
        super().__init__()
        self.settings = settings

        # Store a func object that is used when this entry is selected
        self.select_func = select_func

        # Store this entries action data
        self.action_data = action_data

        # As we edit and make changes, store that in here for quick reloading
        # Format:
        # {
        #   - <param>: <value>
        #   - ...
        # }
        # @TODO: TEMP - REVIEW THE IMPLEMENTATION OF THIS
        self.cache_data = {}

        # Load any defaults for this entry
        self.LoadDefaults()

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
        print(self.cache_data)
        # Populate the subtext with all params with preview enabled
        for param in self.action_data['requirements']:
            if param['preview']:
                cur_text = self.subtext_widget.text()
                name = param['name']
                if cur_text:
                    self.subtext_widget.setText(cur_text + f", {name}: {self.cache_data[name]}")
                else:
                    self.subtext_widget.setText(cur_text + f"{name}: {self.cache_data[name]}")

    def LoadDefaults(self):
        """ Updates the cache for this entry using whatever the default values are in the 'ActionsDatabase' file """

        for param in self.action_data['requirements']:
            # If this param has a global param available, use it as the default instead
            if 'global' in param:
                req_global_data = param['global']
                project_data_cat = self.settings.user_project_data[req_global_data['category']]
                project_global_value = project_data_cat[req_global_data['global_parameter']]

                self.cache_data[param['name']] = project_global_value

            # No global available - Use the 'default' value
            else:
                self.cache_data[param['name']] = param['default']