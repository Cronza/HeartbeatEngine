from PyQt5 import QtWidgets


class BranchesEntry(QtWidgets.QWidget):
    def __init__(self, branch_data, settings, select_func):
        super().__init__()
        self.settings = settings

        # Store a func object that is used when this entry is selected
        self.select_func = select_func

        # Store this entries action data
        self.branch_data = branch_data

        # ****** DISPLAY WIDGETS ******
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Name
        self.name_widget = QtWidgets.QLabel()
        self.name_widget.setFont(settings.header_2_font)
        self.name_widget.setStyleSheet(settings.header_2_color)
        self.name_widget.setWordWrap(True)
        self.name_widget.setText("Test Name")

        # Details
        self.subtext_widget = QtWidgets.QLabel()
        self.subtext_widget.setFont(settings.subtext_font)
        self.subtext_widget.setStyleSheet(settings.subtext_color)
        self.subtext_widget.setWordWrap(True)
        self.subtext_widget.setText('Test Description')

        # Add everything to the layout
        self.main_layout.addWidget(self.name_widget)
        self.main_layout.addWidget(self.subtext_widget)

    def Get(self):
        """ Returns a tuple of 'branch name', 'branch description' """
        return self.name_widget.text(), self.subtext_widget.text()

    def Set(self, data):
        """ Given a tuple of 'branch name' and 'branch description', update the relevant widgets """
        self.name_widget.setText(data[0])
        self.subtext_widget.setText(data[1])

    def Refresh(self):
        """
        Refresh is the common function used by elements that need refreshing when an important U.I change is made
        """

        pass
