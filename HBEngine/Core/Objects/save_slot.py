import pygame

from HBEngine.Core import settings
from HBEngine.Core.Objects.renderable import Renderable
from HBEngine.Core.Objects.renderable_sprite import SpriteRenderable
from HBEngine.Core.Objects.renderable_text import TextRenderable
from HBEngine.Core.Objects.interactable_text import InteractableText


class SaveSlot(Renderable):
    def __init__(self, renderable_data: dict, slot_id: int = 0, parent: Renderable = None, process_data: bool = True):
        self.bounds = [0, 0]

        super().__init__(renderable_data, parent, process_data)
        self.visible = False

        # Create the Slot Background Renderable
        self.background_renderable = SpriteRenderable(
            {
                'key': f"!&SAVE_SLOT_{slot_id}_BACKGROUND&!",
                'sprite': 'HBEngine/Content/Sprites/Interface/Saves/Save_Slot_Background.png',
                'position': [0, 0],
                'center_align': False,
                'z_order': self.renderable_data['z_order'] + 2
            },
            parent=self
        )

        # Create the Thumbnail Renderable
        self.thumbnail_renderable = SpriteRenderable(
            {
                'key': f"!&SAVE_SLOT_{slot_id}_THUMBNAIL&!",
                'sprite': 'HBEngine/Content/Sprites/Interface/Saves/Save_Slot_Thumbnail_Empty.png',
                'position': [0.0065, 0.0075],
                'center_align': False,
                'z_order': self.renderable_data['z_order'] + 2
            },
            parent=self
        )

        # Create the Save Name Renderable
        self.name_renderable = TextRenderable(
            {
                'key': f"!&SAVE_SLOT_{slot_id}_NAME&!",
                'text': 'Empty Save this is a silly and long name but it is a great way to test bounds and wrapping',
                'text_size': 18,
                'text_color': [255, 255, 255],
                'position': [0.155, 0.02],
                'center_align': False,
                'z_order': self.renderable_data['z_order'] + 2,
                'wrap_bounds': [0.45, 0.05]
            },
            parent=self
        )

        # Create the Save Date Renderable
        self.date_renderable = TextRenderable(
            {
                'key': f"!&SAVE_SLOT_{slot_id}_DATE&!",
                'text': '2/19/2025',
                'text_size': 18,
                'text_color': [255, 255, 255],
                'position': [0.155, 0.08],
                'center_align': False,
                'z_order': self.renderable_data['z_order'] + 2,
                'wrap_bounds': [0.8, 0.4]
            },
            parent=self
        )

        # Create the Save Button Renderable
        self.save_button_renderable = InteractableText(
            {
                'key': f"!&SAVE_SLOT_{slot_id}_SAVE_BUTTON&!",
                'text': 'Save',
                'text_size': 18,
                'text_color': [255, 255, 255],
                'position': [0.41, 0.135],
                'center_align': False,
                'z_order': self.renderable_data['z_order'] + 2,
                'wrap_bounds': [0.8, 0.4],
                'events': {
                    'event_0': {
                        'action': {
                            'action': 'save',
                            'slot_id': slot_id
                        }
                    }
                }
            },
            parent=self
        )

        # Create the Load Button Renderable
        self.load_button_renderable = InteractableText(
            {
                'key': f"!&SAVE_SLOT_{slot_id}_LOAD_BUTTON&!",
                'text': 'Load',
                'text_size': 18,
                'text_color': [255, 255, 255],
                'position': [0.47, 0.135],
                'center_align': False,
                'z_order': self.renderable_data['z_order'] + 2,
                'wrap_bounds': [0.8, 0.4]
            },
            parent=self
        )

        # Create the Load Button Renderable
        self.delete_button_renderable = InteractableText(
            {
                'key': f"!&SAVE_SLOT_{slot_id}_DELETE_BUTTON&!",
                'text':      'Delete',
                'text_size': 18,
                'text_color': [255, 255, 255],
                'position': [0.53, 0.135],
                'center_align': False,
                'z_order': self.renderable_data['z_order'] + 2,
                'wrap_bounds': [0.8, 0.4]
            },
            parent=self
        )

        self.children.append(self.background_renderable)
        self.children.append(self.thumbnail_renderable)
        self.children.append(self.name_renderable)
        self.children.append(self.date_renderable)
        self.children.append(self.save_button_renderable)
        self.children.append(self.load_button_renderable)
        self.children.append(self.delete_button_renderable)

        settings.scene.active_renderables.Add(self.background_renderable)
        settings.scene.active_renderables.Add(self.thumbnail_renderable)
        settings.scene.active_renderables.Add(self.name_renderable)
        settings.scene.active_renderables.Add(self.date_renderable)
        settings.scene.active_renderables.Add(self.save_button_renderable)
        settings.scene.active_renderables.Add(self.load_button_renderable)
        settings.scene.active_renderables.Add(self.delete_button_renderable)

    def ApplyRenderableData(self):
        if 'bounds' in self.renderable_data:
            self.bounds = self.renderable_data['bounds']
            self.surface = pygame.Surface(self.ConvertNormToScreen(self.bounds))

        # Run the parent implementation to ensure all changes are considered, and the surfaces are recalculated
        super().ApplyRenderableData()

    def Destroy(self):
        self.thumbnail_renderable.Destroy()
        self.thumbnail_renderable = None
        self.name_renderable.Destroy()
        self.name_renderable = None

        super().Destroy()

