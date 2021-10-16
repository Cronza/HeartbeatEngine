import os
from GVNEngine.Utilities.yaml_reader import Reader

class Settings:
    def __init__(self, project_dir):
        self.root_dir = os.getcwd().replace("\\", "/")

        # Acquire the engine root independent of the project root
        if "GVNEngine/GVNEngine" not in self.root_dir:
            self.root_dir = self.root_dir + "/" + "GVNEngine"

        self.project_dir = project_dir
        self.project_settings = None

        # Some params need to be accessed more immediately than through the settings dict. Declare them here
        self.resolution = None
        self.resolution_options = None
        self.active_resolution = None

    def Evaluate(self, data_path):
        """ Reads in the provided project settings file path """
        self.project_settings = Reader.ReadAll(data_path)

        self.resolution = self.project_settings['Window']['resolution']
        self.resolution_options = self.project_settings['Window']['resolution_options']
        self.active_resolution = tuple(self.resolution_options[self.resolution])

    def ConvertPartialToAbsolutePath(self, partial_path):
        """
        Given a partial path, return a absolute path

        If the provided path has 'ENGINE_FILES' at the beginning, then the returned path will be relative
        to the engine, not the project. This is to allow references to engine default files that are not
        a part of GVN projects
        """
        #@TODO: Figure out how to solve this path reference with packaged builds
        # Context: If using the "main" script to launch the engine from the editor, then the root
        # will be "<root>/GVNEngine", which means to access engine files, you'll need to append another
        # "GVNEngine". This doesn't quite make sense, as this directory struture would likely change for builds
        # where we won't need the editor, so "main" would be non-existent. At that point, we'd likely start
        # in the deeper "GVNEngine", which doesn't require that additional concatenation

        # Idea 1: We still use main, but we don't package the editor, and in main, we have a flag to skip
        # the editor (Likely ill-advised)
        print(os.getcwd())
        # Idea 2: We modify this code for the build
        if partial_path.startswith("ENGINE_FILES"):
            return partial_path.replace("ENGINE_FILES", "GVNEngine") #TEMP HACK (ごめねさい anyone who sees this)
        else:
            return self.project_dir + "/" + partial_path

