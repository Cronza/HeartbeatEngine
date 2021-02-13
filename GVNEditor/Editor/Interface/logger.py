from PyQt5 import QtWidgets, QtGui


class LoggerUI(QtWidgets.QWidget):
    def __init__(self, l_core):
        super().__init__()

        self.l_core = l_core

        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)

        # Main Container
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)

        # Main Layout
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(4, 2, 4, 2)
        self.main_layout.setSpacing(0)

        # Header
        self.logger_title = QtWidgets.QLabel(self)
        self.logger_title.setFont(self.l_core.e_ui.header_font)
        self.logger_title.setText("Logger")

        # Toolbar
        self.logger_toolbar = QtWidgets.QFrame(self)
        self.logger_toolbar.setAutoFillBackground(False)
        self.logger_toolbar.setStyleSheet("QFrame, QLabel, QToolTip {\n"
                                         "    border-radius: 4px;\n"
                                         "    background-color: rgb(44,53,57);\n"
                                         "}")
        self.logger_toolbar.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.logger_toolbar.setFrameShadow(QtWidgets.QFrame.Raised)
        self.logger_toolbar_layout = QtWidgets.QHBoxLayout(self.logger_toolbar)
        self.logger_toolbar_layout.setContentsMargins(2, 2, 2, 2)
        self.logger_toolbar_layout.setSpacing(0)

        # Generic Button Settings
        icon = QtGui.QIcon()
        button_style = (
            "background-color: rgb(44,53,57);\n"
        )

        # Clear Log Button
        self.clear_log_button = QtWidgets.QToolButton(self.logger_toolbar)
        self.clear_log_button.setStyleSheet(button_style)
        icon.addPixmap(QtGui.QPixmap("Content/Icons/Trash.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.clear_log_button.setIcon(icon)
        self.clear_log_button.clicked.connect(self.l_core.ClearLog)

        # Add buttons to toolbar
        self.logger_toolbar_layout.addWidget(self.clear_log_button)
        toolbar_spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.logger_toolbar_layout.addItem(toolbar_spacer)

        #Logger data list
        self.log_list = QtWidgets.QListWidget(self)
        self.log_list.setFont(self.l_core.e_ui.paragraph_font)

        # Add everything to the main container
        self.main_layout.addWidget(self.logger_title)
        self.main_layout.addWidget(self.logger_toolbar)
        self.main_layout.addWidget(self.log_list)
