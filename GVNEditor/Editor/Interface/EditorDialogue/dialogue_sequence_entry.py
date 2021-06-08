from PyQt5 import QtWidgets, QtGui


class DialogueEntry(QtWidgets.QWidget):
    def __init__(self, action_data, settings, select_func, size_refresh_func):
        super().__init__()
        self.settings = settings

        # Store a func object that is used when this entry is selected
        self.select_func = select_func

        # Store a func object that is used when the row containing this object should be resized based on the
        # subtext data in this object
        self.size_refresh_func = size_refresh_func

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
        self.name_widget.setText(self.action_data["display_name"])

        # Details
        self.subtext_widget = QtWidgets.QLabel()
        self.subtext_widget.setFont(settings.subtext_font)
        self.subtext_widget.setStyleSheet(settings.subtext_color)

        # Refresh the subtext
        self.UpdateSubtext()

        # Add everything to the layout
        self.main_layout.addWidget(self.name_widget)
        self.main_layout.addWidget(self.subtext_widget)

    def Get(self) -> dict:
        """ Returns the action data stored in this object """
        return self.action_data

    def UpdateSubtext(self):
        """ Updates the subtext displaying entry parameters """
        self.subtext_widget.setText(self.CompileSubtextString(self.action_data["requirements"]))

    def CompileSubtextString(self, data):
        """ Given a list of requirements from the ActionsDatabase file, compile them into a user-friendly string """
        cur_string = ""
        for param in data:
            if param["preview"]:

                # If cached data is available, use it. Otherwise display the default
                param_name = param["name"]
                param_data = None

                if param["type"] == "container":
                    # Recurse, searching the children as well
                    cur_string += f"{param_name}: ["
                    cur_string += self.CompileSubtextString(param['children'])
                    cur_string += "], "

                else:
                    if "cache" in param:
                        param_data = param["cache"]
                    else:
                        param_data = param["default"]

                    cur_string += f"{param_name}: {param_data}, "

        # Due to how the comma formatting is, strip it from the end of the string
        return cur_string.strip(', ')

    def Refresh(self):
        """
        Refresh is the common function used by elements that need refreshing when an important U.I change is made
        """

        self.UpdateSubtext()
        self.size_refresh_func()

