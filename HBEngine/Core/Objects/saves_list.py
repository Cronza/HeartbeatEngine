from HBEngine.Core import settings
from HBEngine.Core.Objects.renderable import Renderable
from HBEngine.Core.Objects.renderable_sprite import SpriteRenderable


class SavesList(Renderable):
    def __init__(self, renderable_data: dict, parent: Renderable = None, process_data: bool = True):
        # Create a unique key as nothing should attempt to reference it
        renderable_data['key'] = '!&SAVES_LIST&!'

        super().__init__(renderable_data, parent, process_data)

        # Create the Thumbnail Renderable
        self.thumbnail_renderable = SpriteRenderable(
            {
                'key': '!&SAVE_SLOT_THUMBNAIL&!',
                'sprite': 'HBEngine/Content/Sprites/Interface/Saves/Save_Slot_Thumbnail_Empty.png',
                'position': [0.07, 0.1],
                'center_align': False
            },
            parent=self
        )
        self.children.append(self.thumbnail_renderable)
        settings.scene.active_renderables.Add(self.thumbnail_renderable)

    def Destroy(self):
        self.thumbnail_renderable.Destroy()
        self.thumbnail_renderable = None
        
    