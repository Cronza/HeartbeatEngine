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
                f_object['action'] = 'create_sprite'
                self.a_manager.PerformAction(f_object)
        else:
            print('Scene file does not specify any objects')

        # Load any specified interactables
        if 'interactables' in self.scene_data:
            f_interactables = self.scene_data['interactables']

            for f_interactable in f_interactables:
                f_interactable['action'] = 'create_interactable'
                self.a_manager.PerformAction(f_interactable)
        else:
            print('Scene file does not specify any interactables')

        # Load any specified buttons
        if 'buttons' in self.scene_data:
            f_buttons = self.scene_data['buttons']

            for f_button in f_buttons:
                f_button['action'] = 'create_button'
                self.a_manager.PerformAction(f_button)
        else:
            print('Scene file does not specify any buttons')

        # Load any specified text
        if 'text' in self.scene_data:
            f_texts = self.scene_data['text']

            for f_text in f_texts:
                f_text['action'] = 'create_text'
                self.a_manager.PerformAction(f_text)
        else:
            print('Scene file does not specify any text')
