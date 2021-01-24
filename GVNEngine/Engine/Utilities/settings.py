from Engine.Utilities.yaml_reader import Reader

class Settings:
    def __init__(self):
        self.projectSettings = None

        # Some params need to be accessed more immediately than through the settings dict. Declare them here
        self.resolution = None
        self.resolution_options = None
        self.active_resolution = None

    def EvaluateProjectSettings(self, data_path):
        self.projectSettings = Reader.ReadAll(data_path)

        # *** WINDOWS SETTINGS ***
        self.resolution = self.projectSettings['WindowSettings']['resolution']
        self.resolution_options = self.projectSettings['WindowSettings']['resolution_options']
        self.active_resolution = tuple(self.resolution_options[self.resolution])
