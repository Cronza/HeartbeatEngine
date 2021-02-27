from PyQt5 import QtWidgets, QtGui
from Editor.Interface.Generic.details_entry_base import DetailsEntryBase

class DetailsEntryFileSelector(DetailsEntryBase):
    def __init__(self, settings):
        super().__init__(settings)

        self.input_widget = QtWidgets.QLineEdit()

        self.file_select_button = QtWidgets.QToolButton()

        # Create the file selector button, ands style it accordingly
        self.file_select_button.setStyleSheet(self.settings.details_button_style)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Content/Icons/Folder.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.file_select_button.setIcon(icon)
        self.file_select_button.clicked.connect(self.OpenFilePrompt)

        # Assign default value
        self.input_widget.setText("None")

        # By default, the user can't manually add a value to the input widget
        self.MakeUneditable()

        # Add input elements to the layout
        self.main_layout.addWidget(self.input_widget)
        self.main_layout.addWidget(self.file_select_button)


    def Get(self):
        return self.input_widget.text()

    def Set(self, data) -> None:
        self.input_widget.setText(data)

    def MakeUneditable(self):
        self.input_widget.setReadOnly(True)
        self.input_widget.setStyleSheet(self.settings.read_only_background_color);

    def OpenFilePrompt(self) -> str:
        #@TODO: Replace file browser will popup list of files available in the project
        """ Prompts the user with a filedialog, accepting an existing file """
        file_path = QtWidgets.QFileDialog.getOpenFileName(self, "Open File")
        print(file_path)
        if file_path[0]:
            self.Set(file_path[0])



