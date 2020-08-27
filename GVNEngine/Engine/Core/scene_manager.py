from Engine.BaseClasses.scene import Scene
from Engine.BaseClasses.scene_pointandclick import PointAndClickScene
from Engine.BaseClasses.scene_dialogue import DialogueScene
from Engine.Utilities.yaml_reader import Reader

class SceneManager():
    def __init__(self, window, pygame_lib, settings):

        self.settings = settings
        self.pygame_lib = pygame_lib
        self.window = window
        self.active_scene = None

        self.scene_types = {
            'Dialogue': DialogueScene,
            'PointAndClick': PointAndClickScene,
            'Base': Scene
        }

        # Do a special read and load for the initial scene
        scene_data = Reader.ReadAll(self.settings.starting_scene)
        if 'type' in scene_data:
            self.LoadScene(self.settings.starting_scene, scene_data['type'])
        else:
            print("'type' was not specified in the starting file .yaml. Unable to initialize first scene")

    def LoadScene(self, scene_file, scene_type):
        print(" *** LOADING NEW SCENE ***")
        print(scene_type)
        if scene_type in self.scene_types:
            del self.active_scene
            self.active_scene = self.scene_types[scene_type](
                scene_file,
                self.window,
                self.pygame_lib,
                self.settings,
                self
            )

            self.active_scene.Draw()
        else:
            print(f"Failed to Load Scene - Specified scene type does not exist: {scene_type}")

    def ResizeScene(self):
        """ Inform the scene object o resize to support a resolution change """
        self.active_scene.Resize()
