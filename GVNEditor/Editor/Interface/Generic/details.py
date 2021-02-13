from PyQt5 import QtWidgets, QtGui

class Details(QtWidgets.QWidget):
    def __init__(self, e_ui):
        super().__init__()

        # Main editor ref
        self.e_ui = e_ui

        self.details_layout = QtWidgets.QVBoxLayout(self)
        self.details_layout.setContentsMargins(0, 0, 0, 0)
        self.details_layout.setSpacing(0)
        
        # Create title
        self.details_title = QtWidgets.QLabel(self)
        self.details_title.setFont(self.e_ui.header_font)
        self.details_title.setText("Details")

        # Create the toolbar
        self.details_toolbar = QtWidgets.QFrame(self)
        self.details_toolbar.setAutoFillBackground(False)
        self.details_toolbar.setStyleSheet("QFrame, QLabel, QToolTip {\n"
                                              "    border-radius: 4px;\n"
                                              "    background-color: rgb(44,53,57);\n"
                                              "}")
        self.details_toolbar.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.details_toolbar.setFrameShadow(QtWidgets.QFrame.Raised)
        self.details_toolbar_layout = QtWidgets.QHBoxLayout(self.details_toolbar)
        self.details_toolbar_layout.setContentsMargins(2, 2, 2, 2)
        self.details_toolbar_layout.setSpacing(0)

        # Create search filter
        self.details_filter = QtWidgets.QLineEdit(self.details_toolbar)
        self.details_filter.setPlaceholderText("filter...")
        self.details_toolbar_layout.addWidget(self.details_filter)

        # Create Empty Space Spacer
        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.details_toolbar_layout.addItem(spacer)

        # Create Details List
        self.details_list = QtWidgets.QListView(self)

        # ********** Add All Major Pieces to details layout **********
        self.details_layout.addWidget(self.details_title)
        self.details_layout.addWidget(self.details_toolbar)
        self.details_layout.addWidget(self.details_list)
