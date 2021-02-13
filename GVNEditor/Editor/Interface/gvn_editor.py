from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from Editor.Core.logger import Logger


class GVNEditorUI():
    def __init__(self, editor_core):
        super().__init__()
        self.e_core = editor_core

    def setupUi(self, MainWindow):
        # Configure the Window
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1024, 720)

        # Load editor settings so objects can use shared values
        self.load_settings()

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
        self.logger = Logger(self)

        # Build the Main Editor Window
        self.main_editor_container = QtWidgets.QTabWidget(self.central_widget)
        self.main_editor_container.setFont(self.button_font)

        # Allow the user to resize each row
        self.main_resize_container = QtWidgets.QSplitter(self.central_widget)
        self.main_resize_container.setOrientation(Qt.Vertical)

        # ****** Add everything to the interface ******
        self.central_grid_layout.addWidget(self.main_resize_container, 0, 0)
        self.main_resize_container.addWidget(self.main_editor_container)
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
        self.menu_bar.setFont(self.button_font)

        self.file_menu = QtWidgets.QMenu(self.menu_bar)
        self.file_menu.setFont(self.button_font)
        self.file_menu.font
        self.a_new_project = QtWidgets.QAction(main_window)
        self.a_new_project.triggered.connect(self.e_core.NewProject)
        self.a_open_project = QtWidgets.QAction(main_window)
        self.a_open_project.triggered.connect(self.e_core.OpenProject)
        self.a_save = QtWidgets.QAction(main_window)
        self.file_menu.addAction(self.a_new_project)
        self.file_menu.addAction(self.a_open_project)
        self.file_menu.addAction(self.a_save)

        self.dialogue_menu = QtWidgets.QMenu(self.menu_bar)
        self.dialogue_menu.setFont(self.button_font)
        self.a_open_dialogue_editor = QtWidgets.QAction(main_window)
        self.a_open_dialogue_editor.triggered.connect(self.e_core.OpenDialogueEditor)
        self.dialogue_menu.addAction(self.a_open_dialogue_editor)

        # Add each menu to the menu bar
        self.menu_bar.addAction(self.file_menu.menuAction())
        self.menu_bar.addAction(self.dialogue_menu.menuAction())

        # Initialize the Menu Bar
        main_window.setMenuBar(self.menu_bar)

    def retranslateUi(self, MainWindow):
        """ Sets the text of all UI components using available translation """
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "GVNEditor"))

        # *** Update Engine Menu Bar ***
        # Menu Headers
        self.file_menu.setTitle(_translate("MainWindow", "File"))
        self.dialogue_menu.setTitle(_translate("MainWindow", "Dialogue"))

        # 'File Menu' Actions
        self.a_new_project.setText(_translate("MainWindow", "New Project"))
        self.a_open_project.setText(_translate("MainWindow", "Open Project"))
        self.a_save.setText(_translate("MainWindow", "Save"))
        self.a_save.setShortcut(_translate("MainWindow", "Ctrl+S"))

        # 'Dialogue' Actions
        self.a_open_dialogue_editor.setText(_translate("MainWindow", "Open Editor"))
        self.a_open_dialogue_editor.setShortcut(_translate("MainWindow", "Ctrl+Alt+D"))

    def load_settings(self):
        """ Loads the editor settings, and reapplies any changes """
        # Settings
        self.header_font = QtGui.QFont(self.e_core.settings['EditorTextSettings']['header_font'],
                                        self.e_core.settings['EditorTextSettings']['header_text_size'],
                                        QtGui.QFont.Bold
                                     )

        self.paragraph_font = QtGui.QFont(self.e_core.settings['EditorTextSettings']['paragraph_font'],
                                            self.e_core.settings['EditorTextSettings']['paragraph_text_size']
                                        )

        self.button_font = QtGui.QFont(self.e_core.settings['EditorTextSettings']['button_font'],
                                          self.e_core.settings['EditorTextSettings']['button_text_size']
                                      )

#if __name__ == "__main__":
#    import sys
#    app = QtWidgets.QApplication(sys.argv)
#    MainWindow = QtWidgets.QMainWindow()
    #ui = Ui_MainWindow()
#    ui.setupUi(MainWindow)
#    MainWindow.show()
#    sys.exit(app.exec_())
