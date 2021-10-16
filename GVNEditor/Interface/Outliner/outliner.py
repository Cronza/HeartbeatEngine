from PyQt5 import QtWidgets
from GVNEditor.Interface.Outliner.file_system_tree import FileSystemTree


class OutlinerUI(QtWidgets.QWidget):
    def __init__(self, core, settings):
        super().__init__()

        self.core = core
        self.settings = settings

        # Main Layout
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(4, 2, 4, 2)
        self.main_layout.setSpacing(0)

        # Directory view
        self.fs_tree = FileSystemTree(
            self,
            self.settings,
            self.core.gvn_core.OpenFile,
            self.core.CreateFile,
            self.core.CreateFolder,
            self.core.DeleteFile,
            self.core.DeleteFolder
        )

        # Add everything to the main container
        self.main_layout.addWidget(self.fs_tree)
