from PyQt5 import QtWidgets


class EditorBaseUI(QtWidgets.QWidget):
    def __init__(self, core_ref):
        super().__init__()

        self.core = core_ref
