from Engine.BaseClasses.scene import Scene
from Engine.BaseClasses.interactable import Interactable

class PointAndClickScene(Scene):
    def __init__(self, scene_data_file, window, pygame_lib, settings, scene_manager):
        super().__init__(scene_data_file, window, pygame_lib, settings, scene_manager)

    def LoadSceneData(self):
        super().LoadSceneData()

        # Load any specified objects (Non-interactables)
        if 'objects' in self.scene_data:
            f_objects = self.scene_data['objects']

            for f_object in f_objects:
                self.a_manager.PerformAction(f_object, 'create_sprite')
        else:
            print('Scene file does not specify any objects')

        # Load any specified interactables
        if 'interactables' in self.scene_data:
            f_interactables = self.scene_data['interactables']

            for f_interactable in f_interactables:
                self.a_manager.PerformAction(f_interactable, 'create_interactable')
        else:
            print('Scene file does not specify any interactables')

        # Load any specified buttons
        if 'buttons' in self.scene_data:
            f_buttons = self.scene_data['buttons']

            for f_button in f_buttons:
                self.a_manager.PerformAction(f_button, 'create_button')
        else:
            print('Scene file does not specify any buttons')

        # Load any specified text
        if 'text' in self.scene_data:
            f_texts = self.scene_data['text']

            for f_text in f_texts:
                self.a_manager.PerformAction(f_text, 'create_text')
        else:
            print('Scene file does not specify any text')
