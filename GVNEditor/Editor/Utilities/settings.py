import os
from PyQt5 import QtGui
from Editor.Utilities.yaml_reader import Reader


class Settings:
    # Where is the base GVNEngine distro that comes with the editor?
    BASE_ENGINE_DIR = "../GVNEngine"

    # Where does the editor store data needed to track and handle project directories?
    PROJECT_ADMIN_DIR = ".gvn"
    PROJECT_FOLDER_STRUCTURE = {
        "Content": [
            "Audio",
            "Characters",
            "Dialogue",
            "Fonts",
            "Objects",
            "Scenes",
            "Sprites",
            "Styles",
            "Values"
        ],
        "Config":
            None
    }
    # A dict of files that are provided in new projects. Format: <target_folder>: <source_file>
    PROJECT_DEFAULT_FILES = {
        "Config": "Config/Game.yaml"
    }

    # A dict of types of files, and the individual formats which are supported in the engine / editor
    SUPPORTED_CONTENT_TYPES = {
        "Image": "Image Files (*.png *.jpg)",
        "Data": "YAML Files (*.yaml)"
    }

    def __init__(self):
        self.settings = None
        self.action_database = None

        # User Project Data
        self.user_project_name = None
        self.user_project_dir = None
        self.user_project_data = None

        # U.I global styling
        self.header_1_font = None
        self.header_2_font = None
        self.paragraph_font = None
        self.subtext_font = None
        self.button_font = None
        self.toolbar_background_color = None
        self.toolbar_button_background_color = None

        self.LoadEditorSettings("Config/Editor.yaml")
        self.LoadStyleSettings()
        self.LoadActionDatabase("Config/ActionsDatabase.yaml")

    def LoadEditorSettings(self, data_path):
        """ Loads the 'Editor.yaml' file for the editor """
        self.settings = Reader.ReadAll(data_path)

    def LoadProjectSettings(self):
        """ Reads the 'Game.yaml' file for the active project """
        self.user_project_data = Reader.ReadAll(
            os.path.join(
                self.user_project_dir,
                self.PROJECT_DEFAULT_FILES['Config']
            )
        )

    def LoadActionDatabase(self, data_path):
        """ Reads in the 'ActionsDatabase.yaml' file """
        self.action_database = Reader.ReadAll(data_path)

    def GetProjectContentDirectory(self):
        """ Returns the 'Content' folder for the active project """
        return os.path.join(self.user_project_dir, "Content")

    def GetGlobalSetting(self, category, name):
        """ Returns a value from the open project file given a category and parameter name """
        return self.user_project_data[category][name]

    def LoadStyleSettings(self):
        #@TODO: Switch to using QPalette

        """ Loads the editor style settings """
        # Text and Font
        self.header_1_font = QtGui.QFont(self.settings['EditorTextSettings']['header_1_font'],
                                         self.settings['EditorTextSettings']['header_1_text_size'],
                                         )
        self.header_1_color = f"color: rgb({self.settings['EditorTextSettings']['header_1_color']})"
        self.header_1_font.setBold(self.settings['EditorTextSettings']['header_1_is_bold'])
        self.header_1_font.setItalic(self.settings['EditorTextSettings']['header_1_is_italicized'])

        # --

        self.header_2_font = QtGui.QFont(self.settings['EditorTextSettings']['header_2_font'],
                                         self.settings['EditorTextSettings']['header_2_text_size']
                                         )
        self.header_2_color = f"color: rgb({self.settings['EditorTextSettings']['header_2_color']})"
        self.header_2_font.setBold(self.settings['EditorTextSettings']['header_2_is_bold'])
        self.header_2_font.setItalic(self.settings['EditorTextSettings']['header_2_is_italicized'])

        # --

        self.header_3_font = QtGui.QFont(self.settings['EditorTextSettings']['header_3_font'],
                                         self.settings['EditorTextSettings']['header_3_text_size']
                                         )
        self.header_3_color = f"color: rgb({self.settings['EditorTextSettings']['header_3_color']})"

        self.header_3_font.setBold(self.settings['EditorTextSettings']['header_3_is_bold'])
        self.header_3_font.setItalic(self.settings['EditorTextSettings']['header_3_is_italicized'])

        # --

        self.paragraph_font = QtGui.QFont(self.settings['EditorTextSettings']['paragraph_font'],
                                          self.settings['EditorTextSettings']['paragraph_text_size']
                                          )
        self.paragraph_color = f"color: rgb({self.settings['EditorTextSettings']['paragraph_color']})"
        self.paragraph_font.setBold(self.settings['EditorTextSettings']['paragraph_is_bold'])
        self.paragraph_font.setItalic(self.settings['EditorTextSettings']['paragraph_is_italicized'])

        # --

        self.paragraph_2_font = QtGui.QFont(self.settings['EditorTextSettings']['paragraph_2_font'],
                                          self.settings['EditorTextSettings']['paragraph_2_text_size']
                                          )
        self.paragraph_2_color = f"color: rgb({self.settings['EditorTextSettings']['paragraph_2_color']})"
        self.paragraph_2_font.setBold(self.settings['EditorTextSettings']['paragraph_2_is_bold'])
        self.paragraph_2_font.setItalic(self.settings['EditorTextSettings']['paragraph_2_is_italicized'])

        # --

        self.subtext_font = QtGui.QFont(self.settings['EditorTextSettings']['subtext_font'],
                                        self.settings['EditorTextSettings']['subtext_text_size'],
                                        QtGui.QFont.Bold
                                        )
        self.subtext_color = f"color: rgb({self.settings['EditorTextSettings']['subtext_color']})"
        self.subtext_font.setBold(self.settings['EditorTextSettings']['subtext_is_bold'])
        self.subtext_font.setItalic(self.settings['EditorTextSettings']['subtext_is_italicized'])

        # --

        self.button_font = QtGui.QFont(self.settings['EditorTextSettings']['button_font'],
                                       self.settings['EditorTextSettings']['button_text_size']
                                       )
        self.button_color = f"color: rgb({self.settings['EditorTextSettings']['button_color']})"
        self.button_font.setBold(self.settings['EditorTextSettings']['button_is_bold'])
        self.button_font.setItalic(self.settings['EditorTextSettings']['button_is_italicized'])

        # Color and Style
        self.toolbar_background_color = self.settings[
            'EditorInterfaceSettings']['toolbar_background_color']

        self.toolbar_button_background_color = self.settings[
            'EditorInterfaceSettings']['toolbar_button_background_color']

        self.details_button_style = f"""
            background-color: rgb({self.settings['EditorInterfaceSettings']['details_button_background_color']});
            border: 8px
        """

        # State
        self.read_only_background_color = f"background-color: rgb(" \
                                          f"{self.settings['EditorStateSettings']['read_only_background_color']})"

        self.selection_color = f"""
            selection-background-color: rgb({self.settings['EditorStateSettings']['selection_color']})
        """
