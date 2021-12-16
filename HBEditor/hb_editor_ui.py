"""
    The Heartbeat Engine is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    The Heartbeat Engine is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with the Heartbeat Engine. If not, see <https://www.gnu.org/licenses/>.
"""
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from HBEditor.Core.settings import Settings
from HBEditor.Core.Logger.logger import Logger
from HBEditor.Core.Outliner.outliner import Outliner


class HBEditorUI:
    def __init__(self, e_core):
        super().__init__()

        self.e_core = e_core

    def setupUi(self, MainWindow):
        # Configure the Window
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1024, 720)
        MainWindow.setWindowIcon(
            QtGui.QIcon(Settings.getInstance().ConvertPartialToAbsolutePath("Content/Icons/Engine_Logo.png"))
        )

        # Build the core window widget object
        self.central_widget = QtWidgets.QWidget(MainWindow)
        MainWindow.setCentralWidget(self.central_widget)

        # Build the core window layout object
        self.central_grid_layout = QtWidgets.QGridLayout(self.central_widget)
        self.central_grid_layout.setContentsMargins(0, 0, 0, 0)
        self.central_grid_layout.setSpacing(0)

        # Initialize the Menu Bar
        self.CreateMenuBar(MainWindow)

        # Allow the user to resize each row
        self.main_resize_container = QtWidgets.QSplitter(self.central_widget)
        self.main_resize_container.setContentsMargins(0, 0, 0, 0)
        self.main_resize_container.setOrientation(Qt.Vertical)

        # ****** Add everything to the interface ******
        self.central_grid_layout.addWidget(self.main_resize_container, 0, 0)
        self.CreateGettingStartedDisplay()
        self.CreateBottomTabContainer()
        self.AddTab(Logger.getInstance().GetUI(), "Logger", self.bottom_tab_editor)

        # Adjust the main editor container so it takes up as much space as possible
        self.main_resize_container.setStretchFactor(0, 10)

        # Hook up buttons
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Update the text of all U.I elements using a translation function. That way, we centralize text updates
        # through a common point where localization can take place
        self.retranslateUi(MainWindow)

        Logger.getInstance().Log("Initialized Editor Interface")

    def CreateMenuBar(self, main_window):
        # *** Build the Menu Bar ***
        self.menu_bar = QtWidgets.QMenuBar(main_window)
        self.menu_bar.setGeometry(QtCore.QRect(0, 0, 1024, 21))
        self.menu_bar.setFont(Settings.getInstance().button_font)

        # File Menu
        self.file_menu = QtWidgets.QMenu(self.menu_bar)
        self.file_menu.setWindowFlags(self.file_menu.windowFlags() | QtCore.Qt.NoDropShadowWindowHint)
        self.a_new_file = QtWidgets.QAction(main_window)
        self.a_new_file.triggered.connect(self.e_core.NewFile)
        self.a_open_file = QtWidgets.QAction(main_window)
        self.a_open_file.triggered.connect(self.e_core.OpenFile)
        self.a_save_file = QtWidgets.QAction(main_window)
        self.a_save_file.triggered.connect(self.e_core.Save)
        self.a_save_file_as = QtWidgets.QAction(main_window)
        self.a_save_file_as.triggered.connect(self.e_core.SaveAs)
        self.a_new_project = QtWidgets.QAction(main_window)
        self.a_new_project.triggered.connect(self.e_core.NewProject)
        self.a_open_project = QtWidgets.QAction(main_window)
        self.a_open_project.triggered.connect(self.e_core.OpenProject)
        self.file_menu.addAction(self.a_new_file)
        self.file_menu.addAction(self.a_open_file)
        self.file_menu.addAction(self.a_save_file)
        self.file_menu.addAction(self.a_save_file_as)
        self.file_menu.addAction(self.a_new_project)
        self.file_menu.addAction(self.a_open_project)

        # Settings Menu
        self.settings_menu = QtWidgets.QMenu(self.menu_bar)
        self.settings_menu.setWindowFlags(self.settings_menu.windowFlags() | QtCore.Qt.NoDropShadowWindowHint)
        self.a_open_project_settings = QtWidgets.QAction(main_window)
        self.a_open_project_settings.triggered.connect(self.e_core.OpenProjectSettings)
        self.settings_menu.addAction(self.a_open_project_settings)

        # Play Menu
        self.play_menu = QtWidgets.QMenu(self.menu_bar)
        self.play_menu.setWindowFlags(self.play_menu.windowFlags() | QtCore.Qt.NoDropShadowWindowHint)
        self.a_play_game = QtWidgets.QAction(main_window)
        self.a_play_game.triggered.connect(self.e_core.Play)
        self.play_menu.addAction(self.a_play_game)

        # Build Menu
        self.build_menu = QtWidgets.QMenu(self.menu_bar)
        self.build_menu.setWindowFlags(self.build_menu.windowFlags() | QtCore.Qt.NoDropShadowWindowHint)
        self.a_build = QtWidgets.QAction(main_window)
        self.a_build.triggered.connect(self.e_core.Build)
        self.a_build_clean = QtWidgets.QAction(main_window)
        self.a_build_clean.triggered.connect(self.e_core.Clean)
        self.build_menu.addAction(self.a_build)
        self.build_menu.addAction(self.a_build_clean)

        # Add each menu to the menu bar
        self.menu_bar.addAction(self.file_menu.menuAction())
        self.menu_bar.addAction(self.settings_menu.menuAction())
        self.menu_bar.addAction(self.play_menu.menuAction())
        self.menu_bar.addAction(self.build_menu.menuAction())

        # Initialize the Menu Bar
        main_window.setMenuBar(self.menu_bar)

    def retranslateUi(self, MainWindow):
        """ Sets the text of all UI components using available translation """
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", f"Heartbeat Editor - {Settings.getInstance().user_project_name}"))

        # 'File Menu' Actions
        self.file_menu.setTitle(_translate("MainWindow", "File"))
        self.a_new_file.setText(_translate("MainWindow", "New File"))
        self.a_new_file.setShortcut(_translate("MainWindow", "Ctrl+N"))
        self.a_open_file.setText(_translate("MainWindow", "Open File"))
        self.a_open_file.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.a_save_file.setText(_translate("MainWindow", "Save"))
        self.a_save_file.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.a_save_file_as.setText(_translate("MainWindow", "Save As"))
        self.a_save_file_as.setShortcut(_translate("MainWindow", "Ctrl+Alt+S"))
        self.a_new_project.setText(_translate("MainWindow", "New Project"))
        self.a_new_project.setShortcut(_translate("MainWindow", "Ctrl+Alt+Shift+N"))
        self.a_open_project.setText(_translate("MainWindow", "Open Project"))
        self.a_open_project.setShortcut(_translate("MainWindow", "Ctrl+Alt+Shift+O"))

        # 'Play Menu' Actions
        self.play_menu.setTitle(_translate("MainWindow", "Play"))
        self.a_play_game.setText(_translate("MainWindow", "Play"))
        self.a_play_game.setShortcut(_translate("MainWindow", "Ctrl+Alt+P"))

        # 'Build Menu' Actions
        self.build_menu.setTitle(_translate("MainWindow", "Build"))
        self.a_build.setText(_translate("MainWindow", "Build"))
        self.a_build.setShortcut(_translate("MainWindow", "Ctrl+Alt+B"))
        self.a_build_clean.setText(_translate("MainWindow", "Clean"))

        # 'Settings Menu' Actions
        self.settings_menu.setTitle(_translate("MainWindow", "Settings"))
        self.a_open_project_settings.setText(_translate("MainWindow", "Open Project Settings"))
        self.a_open_project_settings.setShortcut(_translate("MainWindow", "Ctrl+Shift+P"))

    def CreateMainTabContainer(self):
        """ Creates the main tab editor window, allowing specific editors to be added to it """
        self.main_editor_container = QtWidgets.QWidget()
        self.main_editor_layout = QtWidgets.QVBoxLayout(self.main_editor_container)
        self.main_editor_layout.setContentsMargins(0, 0, 0, 0)
        self.main_editor_layout.setSpacing(0)
        self.main_tab_editor = QtWidgets.QTabWidget(self.main_editor_container)
        self.main_tab_editor.setVisible(False)
        self.main_tab_editor.setElideMode(0)
        self.main_tab_editor.setTabsClosable(True)
        self.main_tab_editor.tabCloseRequested.connect(self.RemoveEditorTab)
        self.main_tab_editor.currentChanged.connect(self.ChangeTab)

        self.main_editor_layout.addWidget(self.main_tab_editor)
        self.main_resize_container.insertWidget(0, self.main_editor_container)

        # QSplitter's use a more verbose method of auto-scaling it's children. We need to ensure that it's going to
        # scale our tab editor accordingly, so set it to take priority here
        self.main_resize_container.setStretchFactor(0, 1)

    def ChangeTab(self, index):
        """ Updates the active editor when the tab selection changes """
        if index != -1:
            self.e_core.active_editor = self.main_tab_editor.widget(index).core
            if not self.main_tab_editor.isVisible():
                self.main_tab_editor.setVisible(True)
        else:
            self.e_core.active_editor = None
            self.main_tab_editor.setVisible(False)

    def CreateBottomTabContainer(self):
        """ Creates the bottom tab editor window, allowing sub editors such as the logger to be added to it """
        self.bottom_tab_editor = QtWidgets.QTabWidget(self.main_resize_container)
        self.bottom_tab_editor.setContentsMargins(0, 0, 0, 0)
        self.main_resize_container.insertWidget(1, self.bottom_tab_editor)

    def CreateGettingStartedDisplay(self):
        """ Creates some temporary UI elements that inform the user how to prepare the editor """
        self.getting_started_container = QtWidgets.QWidget()
        self.getting_started_layout = QtWidgets.QVBoxLayout(self.getting_started_container)

        getting_started_title = QtWidgets.QLabel("Getting Started")
        getting_started_title.setObjectName("text-soft-h1")

        getting_started_message = QtWidgets.QLabel()
        getting_started_message.setObjectName("text-soft")
        getting_started_message.setText(
            "To access editor features, please open a Heartbeat project: \n\n"
            "1) Go to 'File' -> 'New Project' to Create a new Heartbeat project\n"
            "2) Go to 'File' -> 'Open Project' to Open an existing Heartbeat project"
        )

        self.getting_started_layout.setAlignment(Qt.AlignCenter)
        self.getting_started_layout.addWidget(getting_started_title)
        self.getting_started_layout.addWidget(getting_started_message)

        self.main_resize_container.addWidget(self.getting_started_container)

    def CreateOutliner(self):
        """ Creates the outliner window, and adds it to the bottom tab menu """
        self.outliner = Outliner(self.e_core)
        self.e_core.outliner = self.outliner
        self.AddTab(self.outliner.GetUI(), "Outliner", self.bottom_tab_editor)

    def AddTab(self, widget, tab_name, target_tab_widget):
        """ Adds a tab to the given tab widget before selecting that new tab """
        tab_index = target_tab_widget.addTab(widget, tab_name)
        target_tab_widget.setCurrentIndex(tab_index)

    def RemoveEditorTab(self, index):
        """ Remove the tab for the given index (Value is automatically provided by the tab system as an arg) """
        #@TODO: Review if a memory leak is created here due to not going down the editor reference tree and deleting things
        Logger.getInstance().Log("Closing editor...")

        editor_widget = self.main_tab_editor.widget(index)
        del editor_widget
        self.main_tab_editor.removeTab(index)

        Logger.getInstance().Log("Editor closed")

#if __name__ == "__main__":
#    import sys
#    app = QtWidgets.QApplication(sys.argv)
#    MainWindow = QtWidgets.QMainWindow()
    #ui = Ui_MainWindow()
#    ui.setupUi(MainWindow)
#    MainWindow.show()
#    sys.exit(app.exec_())
