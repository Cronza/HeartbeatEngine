from PyQt6 import QtWidgets, QtCore


class ConnectButton(QtWidgets.QToolButton):
    def __init__(self, parent = None):
        super().__init__(parent)
        print("Spawned Connect Button")

        self.clicked.connect(self.ShowConnectionDialog)

    def ShowConnectionDialog(self):
        dialog = ConnectionDialog()
        dialog.exec()

class ConnectionDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        # Hide the OS header to lock its position
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.resize(640, 480)
        self.main_layout = QtWidgets.QTabBar(self)

        self.value_tab = QtWidgets.QTabWidget()

        self.project_setting_tab = QtWidgets.QTabWidget()
        self.main_layout



        # Confirmation Buttons
        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.main_layout.addWidget(self.button_box)