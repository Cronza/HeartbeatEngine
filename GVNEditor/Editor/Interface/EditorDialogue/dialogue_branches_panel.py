from PyQt5 import QtWidgets, QtGui

class Branches(QtWidgets.QWidget):
    def __init__(self, settings):
        super().__init__()

        self.settings = settings

        self.branches_layout = QtWidgets.QVBoxLayout(self)
        self.branches_layout.setContentsMargins(0, 0, 0, 0)
        self.branches_layout.setSpacing(0)

        # Create title
        self.branches_title = QtWidgets.QLabel(self)
        self.branches_title.setFont(self.settings.header_1_font)
        self.branches_title.setStyleSheet(settings.header_1_color)
        self.branches_title.setText("Branches")

        # Create the toolbar
        self.branches_toolbar = QtWidgets.QFrame(self)
        self.branches_toolbar.setAutoFillBackground(False)
        self.branches_toolbar.setStyleSheet(
            "QFrame, QLabel, QToolTip {\n"
            "    border-radius: 4px;\n"
            f"   background-color: rgb({self.settings.toolbar_background_color});\n"
            "}"
        )
        self.branches_toolbar.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.branches_toolbar.setFrameShadow(QtWidgets.QFrame.Raised)
        self.branches_toolbar_layout = QtWidgets.QHBoxLayout(self.branches_toolbar)
        self.branches_toolbar_layout.setContentsMargins(2, 2, 2, 2)
        self.branches_toolbar_layout.setSpacing(0)

        # Create search filter
        self.branches_filter = QtWidgets.QLineEdit(self.branches_toolbar)
        self.branches_filter.setPlaceholderText("filter...")
        self.branches_toolbar_layout.addWidget(self.branches_filter)

        # Create Empty Space Spacer
        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.branches_toolbar_layout.addItem(spacer)

        # Create Details List
        self.branches_list = QtWidgets.QListWidget(self)

        # ********** Add All Major Pieces to details layout **********
        self.branches_layout.addWidget(self.branches_title)
        self.branches_layout.addWidget(self.branches_toolbar)
        self.branches_layout.addWidget(self.branches_list)

        self.TestPopulate()

    def TestPopulate(self):
        for i in range(0, 5):
            test = QtWidgets.QListWidgetItem(f"Test Item {i}")
            self.branches_list.addItem(test)
