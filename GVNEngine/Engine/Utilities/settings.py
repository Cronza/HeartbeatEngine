import os
from Engine.Utilities.yaml_reader import Reader

class Settings:
    def __init__(self):
        self.root_dir = os.getcwd().replace("\\", "/")

        # Alter the path if the user is opening just the engine project, or the full GVNEngine project
        if "GVNEngine/GVNEngine" not in self.root_dir:
            self.root_dir = os.path.join(self.root_dir, "GVNEngine")

        self.project_settings = None

        # Some params need to be accessed more immediately than through the settings dict. Declare them here
        self.resolution = None
        self.resolution_options = None
        self.active_resolution = None

    def Evaluate(self, data_path):
        self.project_settings = Reader.ReadAll(data_path)

        # *** WINDOWS SETTINGS ***
        self.resolution = self.project_settings['Window']['resolution']
        self.resolution_options = self.project_settings['Window']['resolution_options']
        self.active_resolution = tuple(self.resolution_options[self.resolution])

    def ConvertPartialToAbsolutePath(self, partial_path):
        """ Given a parital path, return a absolute path """
        print(os.path.join(self.root_dir, partial_path))
        return os.path.join(self.root_dir, partial_path)
