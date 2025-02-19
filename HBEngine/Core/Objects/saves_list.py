import pygame

from HBEngine.Core import settings
from HBEngine.Core.Objects.renderable import Renderable
from HBEngine.Core.Objects.renderable_sprite import SpriteRenderable
from HBEngine.Core.Objects.renderable_text import TextRenderable


class SavesList(Renderable):
    def __init__(self, renderable_data: dict, parent: Renderable = None, process_data: bool = True):
        self.bounds = [0, 0]

        # Override certain keys
        renderable_data['center_align'] = False
        renderable_data['key'] = '!&SAVES_LIST&!'  # Create a unique key as nothing should attempt to reference it

        # Run parent implementation which will perform recalculations with the aforementioned parameters
        super().__init__(renderable_data, parent, process_data)
        self.visible = False

        # Create the Thumbnail Renderable
        self.thumbnail_renderable = SpriteRenderable(
            {
                'key': '!&SAVE_SLOT_THUMBNAIL&!',
                'sprite': 'HBEngine/Content/Sprites/Interface/Saves/Save_Slot_Thumbnail_Empty.png',
                'position': [0.07, 0.1],
                'center_align': False,
                'z_order': self.renderable_data['z_order'] + 1
            },
            parent=self
        )

        # Create the save name text renderable
        self.name_renderable = TextRenderable(
            {
                'key': '!&SAVE_SLOT_NAME&!',
                'text': 'Default Save Name',
                'text_size': 24,
                'text_color': [255, 255, 255],
                'position': [0, 0],
                'center_align': False,
                'z_order': self.renderable_data['z_order'] + 2,
                'wrap_bounds': [0.8, 0.4]
            },
            parent=self
        )

        self.children.append(self.thumbnail_renderable)
        self.children.append(self.name_renderable)

        settings.scene.active_renderables.Add(self.thumbnail_renderable)
        settings.scene.active_renderables.Add(self.name_renderable)

    def ApplyRenderableData(self):
        if 'bounds' in self.renderable_data:
            self.bounds = self.renderable_data['bounds']
            self.surface = pygame.Surface(self.ConvertNormToScreen(self.bounds))

        # Run the parent implementation to ensure all changes are considered, and the surfaces are recalculated
        super().ApplyRenderableData()

        print("Saves List ***")
        print(self.rect)
        print(self.position)
        #print(self.parent.rect) #@TODO: Due to the way we create reenderables in the actions file, 'parent' isn't available
        #@TODO: during initial position and size calculations since we initialize objects, then call 'AddToScene'

        print("*********")

    def Destroy(self):
        self.thumbnail_renderable.Destroy()
        self.thumbnail_renderable = None

        self.name_renderable.Destroy()
        self.name_renderable = None
        
    