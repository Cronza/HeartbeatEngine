from PyQt5 import QtGui
from Editor.Utilities.yaml_reader import Reader

class Settings():
    def __init__(self):
        self.settings = None
        self.action_database = None

        # U.I global styling
        self.header_font = None
        self.paragraph_font = None
        self.button_font = None
        self.toolbar_background_color = None
        self.toolbar_button_background_color = None

        self.LoadEditorSettings("Config/Editor.yaml")
        self.LoadStyleSettings()
        self.GetActionDatabase("actions_database.yaml")

    def LoadEditorSettings(self, data_path):
        self.settings = Reader.ReadAll(data_path)

    def GetActionDatabase(self, data_path):
        # @TODO: Hook this up to the engine, so the data it gathers is dynamic
        # @TODO: How does the editor know what actions are available, and the params for each action?

        self.action_database = Reader.ReadAll(data_path)

    def LoadStyleSettings(self):
        """ Loads the editor style settings """
        # Text and Font
        self.header_font = QtGui.QFont(self.settings['EditorTextSettings']['header_font'],
                                        self.settings['EditorTextSettings']['header_text_size'],
                                        QtGui.QFont.Bold
                                     )

        self.paragraph_font = QtGui.QFont(self.settings['EditorTextSettings']['paragraph_font'],
                                            self.settings['EditorTextSettings']['paragraph_text_size']
                                        )

        self.button_font = QtGui.QFont(self.settings['EditorTextSettings']['button_font'],
                                          self.settings['EditorTextSettings']['button_text_size']
                                      )
        # Color and Style
        self.toolbar_background_color = self.settings[
            'EditorInterfaceSettings']['toolbar_background_color']

        self.toolbar_button_background_color = self.settings[
            'EditorInterfaceSettings']['toolbar_button_background_color']