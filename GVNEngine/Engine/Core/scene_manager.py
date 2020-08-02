from Engine.BaseClasses.scene import Scene
from Engine.BaseClasses.scene_pointandclick import PointAndClickScene
from Engine.BaseClasses.scene_dialogue import DialogueScene

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

        self.LoadScene(self.settings.starting_scene, 'Dialogue')

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

            self.active_scene.Draw(
                self.settings.main_resolution,
                self.settings.resolution_options[self.settings.resolution]
            )
        else:
            print(f"Failed to Load Scene - Specified scene type does not exist: {scene_type}")



