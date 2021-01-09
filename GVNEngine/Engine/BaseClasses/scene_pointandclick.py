from Engine.BaseClasses.scene import Scene
from Engine.BaseClasses.interactable import Interactable

class PointAndClickScene(Scene):
    def __init__(self, scene_data_file, window, pygame_lib, settings, scene_manager):
        super().__init__(scene_data_file, window, pygame_lib, settings, scene_manager)

    def Draw(self):
        # Draw both generics and interactive specifics using the parent's method
        super().Draw()

    def LoadSceneData(self):
        super().LoadSceneData()

        # Load any specified objects (Non-interactables)
        if 'objects' in self.scene_data:
            f_objects = self.scene_data['objects']

            for f_object in f_objects:
                f_object['action'] = 'load_sprite'
                self.a_manager.PerformAction(f_object)
        else:
            print('Scene file does not specify any objects')

        # Load any specified interactables
        if 'interactables' in self.scene_data:
            f_interactables = self.scene_data['interactables']

            # Interactables can come in many types, so allow the user to specify a unique type. If they don't,
            # use the generic interactable renderable
            for f_interactable in f_interactables:
                if "type" in f_interactable:
                    f_interactable['action'] = f"create_{f_interactable['type'].lower()}"
                else:
                    f_interactable['action'] = 'create_interactable'

                self.a_manager.PerformAction(f_interactable)
        else:
            print('Scene file does not specify any objects')

        # Load any specified text
        if 'text' in self.scene_data:
            f_texts = self.scene_data['text']

            for f_text in f_texts:
                f_text['action'] = 'create_text'
                self.a_manager.PerformAction(f_text)
        else:
            print('Scene file does not specify any text')