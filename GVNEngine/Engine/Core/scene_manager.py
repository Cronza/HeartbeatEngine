from Engine.Core.BaseClasses.scene_pointandclick import PointAndClickScene
from Engine.Core.BaseClasses.scene_dialogue import DialogueScene
from Engine.Utilities.yaml_reader import Reader
from Engine.Utilities.DataTypes.file_types import FileType

class SceneManager():
    def __init__(self, window, pygame_lib, settings):

        # Objects
        self.settings = settings
        self.pygame_lib = pygame_lib
        self.window = window
        self.active_scene = None

        # Cached Values (Scene agnostic)
        self.resolution_multiplier = None  # Null by default to allow the starting scene to generate a starting value
        self.pause_menu_data = None  # Menu data is stored in the manager, but the menu is owned by a scene

        self.scene_types = {
            FileType.Scene_Dialogue: DialogueScene,
            FileType.Scene_Point_And_Click: PointAndClickScene
        }

        #@TODO: Review starting scene load implementation
        # Do a special read and load for the initial scene
        starting_scene_partial_path = self.settings.project_settings['Game']['starting_scene']
        scene_data = Reader.ReadAll(self.settings.ConvertPartialToAbsolutePath(starting_scene_partial_path))

        if 'type' in scene_data:
            self.LoadScene(starting_scene_partial_path, FileType[scene_data['type']])
        else:
            assert "'type' was not specified in the starting file .yaml. Unable to initialize first scene"

        # Read in the yaml data for the pause menu
        #@TODO: Re-enable after review
        #self.pause_menu_data = Reader.ReadAll(self.settings.project_dir + "/" + self.settings.project_settings['Pause Menu']['data_file'])
        #self.pause_menu_data['action'] = "create_container"

    def LoadScene(self, scene_file, scene_type):
        print(" *** LOADING NEW SCENE ***")
        if scene_type in self.scene_types:
            del self.active_scene
            self.active_scene = self.scene_types[scene_type](
                scene_file,
                self.window,
                self.pygame_lib,
                self.settings,
                self
            )
        else:
            print(f"Failed to Load Scene - Specified scene type does not exist: {scene_type}")

    def ResizeScene(self):
        """ Inform the scene object o resize to support a resolution change """
        self.active_scene.Resize()

    def ShowPauseMenu(self):
        pass
