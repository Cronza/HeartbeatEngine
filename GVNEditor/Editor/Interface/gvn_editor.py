from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from Editor.Core.Generic.logger import Logger


class GVNEditorUI:
    def __init__(self, e_core, settings):
        super().__init__()

        self.e_core = e_core
        self.settings = settings

    def setupUi(self, MainWindow):
        # Configure the Window
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1024, 720)
        MainWindow.setWindowIcon(QtGui.QIcon('Content/Icons/GVNEngine_Logo.png'))

        # Build the core window widget object
        self.central_widget = QtWidgets.QWidget(MainWindow)
        MainWindow.setCentralWidget(self.central_widget)

        # Build the core window layout object
        self.central_grid_layout = QtWidgets.QGridLayout(self.central_widget)
        self.central_grid_layout.setContentsMargins(0, 0, 0, 0)
        self.central_grid_layout.setSpacing(0)

        # Initialize the Menu Bar
        self.CreateMenuBar(MainWindow)

        # Initialize the Logger
        self.logger = Logger(self, self.settings)

        # Allow the user to resize each row
        self.main_resize_container = QtWidgets.QSplitter(self.central_widget)
        self.main_resize_container.setOrientation(Qt.Vertical)

        # ****** Add everything to the interface ******
        self.central_grid_layout.addWidget(self.main_resize_container, 0, 0)
        self.CreateGettingStartedDisplay()
        self.main_resize_container.addWidget(self.logger.log_ui)

        #Adjust the main editor container so it takes up as much space as possible
        self.main_resize_container.setStretchFactor(0, 10)

        # Hook up buttons
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Update the text of all U.I elements using a translation function. That way, we centralize text updates
        # through a common point where localization can take place
        self.retranslateUi(MainWindow)

        self.logger.Log("Initialized Editor Interface")

    def CreateMenuBar(self, main_window):
        # *** Build the Menu Bar ***
        self.menu_bar = QtWidgets.QMenuBar(main_window)
        self.menu_bar.setGeometry(QtCore.QRect(0, 0, 1024, 21))
        self.menu_bar.setFont(self.settings.button_font)
        self.menu_bar.setStyleSheet(self.settings.button_color)

        self.file_menu = QtWidgets.QMenu(self.menu_bar)
        self.file_menu.setFont(self.settings.button_font)
        self.file_menu.setStyleSheet(self.settings.button_color)
        self.a_new_file = QtWidgets.QAction(main_window)
        self.a_new_file.triggered.connect(self.e_core.NewFile)
        self.a_save_file_as = QtWidgets.QAction(main_window)
        self.a_save_file_as.triggered.connect(self.e_core.SaveAs)
        self.a_new_project = QtWidgets.QAction(main_window)
        self.a_new_project.triggered.connect(self.e_core.NewProject)
        self.a_open_project = QtWidgets.QAction(main_window)
        self.a_open_project.triggered.connect(self.e_core.OpenProject)
        self.file_menu.addAction(self.a_new_file)
        self.file_menu.addAction(self.a_save_file_as)
        self.file_menu.addAction(self.a_new_project)
        self.file_menu.addAction(self.a_open_project)

        self.editors_menu = QtWidgets.QMenu(self.menu_bar)
        self.editors_menu.setFont(self.settings.button_font)
        self.editors_menu.setStyleSheet(self.settings.button_color)
        self.a_open_dialogue_editor = QtWidgets.QAction(main_window)
        self.a_open_dialogue_editor.triggered.connect(self.e_core.OpenDialogueEditor)
        self.editors_menu.addAction(self.a_open_dialogue_editor)

        # Add each menu to the menu bar
        self.menu_bar.addAction(self.file_menu.menuAction())
        self.menu_bar.addAction(self.editors_menu.menuAction())

        # Initialize the Menu Bar
        main_window.setMenuBar(self.menu_bar)

    def retranslateUi(self, MainWindow):
        """ Sets the text of all UI components using available translation """
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", f"GVNEditor - {self.settings.user_project_name}"))

        # *** Update Engine Menu Bar ***
        # Menu Headers
        self.file_menu.setTitle(_translate("MainWindow", "File"))
        self.editors_menu.setTitle(_translate("MainWindow", "Editors"))

        # 'File Menu' Actions
        self.a_new_file.setText(_translate("MainWindow", "New File"))
        self.a_new_file.setShortcut(_translate("MainWindow", "Ctrl+N"))
        self.a_save_file_as.setText(_translate("MainWindow", "Save"))
        self.a_save_file_as.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.a_new_project.setText(_translate("MainWindow", "New Project"))
        self.a_open_project.setText(_translate("MainWindow", "Open Project"))

        # 'Editors' Actions
        self.a_open_dialogue_editor.setText(_translate("MainWindow", "Open Dialogue Editor"))
        self.a_open_dialogue_editor.setShortcut(_translate("MainWindow", "Ctrl+Alt+D"))

    def CreateTabEditor(self):
        """ Creates the main tab editor window, allowing specific editors to be added to it """

        self.main_editor_container = QtWidgets.QWidget()
        self.main_editor_layout = QtWidgets.QVBoxLayout(self.main_editor_container)
        self.main_editor_layout.setContentsMargins(2,2,2,2)
        self.main_editor_layout.setSpacing(0)
        self.main_tab_editor = QtWidgets.QTabWidget(self.main_editor_container)
        self.main_tab_editor.setFont(self.settings.button_font)
        self.main_tab_editor.setStyleSheet(self.settings.button_color)

        self.main_editor_layout.addWidget(self.main_tab_editor)
        self.main_resize_container.insertWidget(0, self.main_editor_container)

        # QSplitter's use a more verbose method of auto-scaling it's children. We need to ensure that it's going to
        # scale our tab editor accordingly, so set it to take priority here
        self.main_resize_container.setStretchFactor(0, 1)

    def CreateGettingStartedDisplay(self):
        """ Creates some temporary UI elements that inform the user how to prepare the editor """

        self.getting_started_container = QtWidgets.QWidget()
        self.getting_started_layout = QtWidgets.QVBoxLayout(self.getting_started_container)

        getting_started_title = QtWidgets.QLabel("Getting Started")
        getting_started_title.setFont(self.settings.editor_info_title_font)
        getting_started_title.setStyleSheet(self.settings.editor_info_title_color)

        getting_started_message = QtWidgets.QLabel()
        getting_started_message.setText(
            "To access editor features, please open a GVN Project: \n\n"
            "1) Go to 'File' -> 'New Project' to Create a new GVN Project\n"
            "2) Go to 'File' -> 'Open Project' to Open an existing GVN Project"
        )
        getting_started_message.setFont(self.settings.editor_info_paragraph_font)
        getting_started_message.setStyleSheet(self.settings.editor_info_paragraph_color)

        self.getting_started_layout.setAlignment(Qt.AlignCenter)
        self.getting_started_layout.addWidget(getting_started_title)
        self.getting_started_layout.addWidget(getting_started_message)

        self.main_resize_container.addWidget(self.getting_started_container)

#if __name__ == "__main__":
#    import sys
#    app = QtWidgets.QApplication(sys.argv)
#    MainWindow = QtWidgets.QMainWindow()
    #ui = Ui_MainWindow()
#    ui.setupUi(MainWindow)
#    MainWindow.show()
#    sys.exit(app.exec_())
