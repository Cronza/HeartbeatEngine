from HBEngine.Core.Objects.renderable import Renderable
from HBEngine.Core.Objects.renderable_sprite import SpriteRenderable
from HBEngine.Core.Objects.interactable import Interactable
from Tools.HBYaml.CustomTags.connection import Connection
from HBEngine.Core import settings


class Checkbox(Interactable):
    """
    A subclass of Interactable that functions as a toggleable checkbox

    This class has the following (additional) Renderable Data requirements:
    - sprite_icon (String)
    - is_checked (Bool)
    """
    def __init__(self, renderable_data: dict, parent: Renderable = None):
        # Parameters
        self.sprite_icon = ""
        self.is_checked = False

        # Create a child sprite renderable representing the check mark, but don't populate it with renderable data
        # yet. It'll be handled later when this object's renderable data is applied
        self.check_icon_renderable = SpriteRenderable(
            {},
            parent=self,
            process_data=False
        )

        # Run parent implementation which will perform recalculations with the aforementioned parameters
        super().__init__(renderable_data, parent)

        # Now that this object and the icon renderable have been setup, add it as a proper child
        self.children.append(self.check_icon_renderable)
    
    def ApplyRenderableData(self):
        super().ApplyRenderableData()

        if "sprite_icon" in self.renderable_data:
            if isinstance(self.renderable_data['sprite_icon'], Connection):
                self.sprite_icon = settings.GetConnectionData(self.renderable_data['sprite_icon'])
                self.RegisterConnectionListener(self.renderable_data['sprite_icon'])
            else:
                self.sprite_icon = self.renderable_data['sprite_icon']

            self.check_icon_renderable.sprite = self.sprite_icon

        if "is_checked" in self.renderable_data:
            if isinstance(self.renderable_data['is_checked'], Connection):
                self.is_checked = settings.GetConnectionData(self.renderable_data['is_checked'])
                self.RegisterConnectionListener(self.renderable_data['is_checked'])
            else:
                self.is_checked = self.renderable_data['is_checked']

            self.check_icon_renderable.visible = self.is_checked

        # Prepare the icon renderable data and apply it
        self.check_icon_renderable.renderable_data = {
            "key": f"{self.renderable_data['key']}_Icon",
            "position": [0.5, 0.5],
            "sprite": self.renderable_data["sprite_icon"],
            "z_order": self.renderable_data["z_order"] + 1
        }
        self.check_icon_renderable.ApplyRenderableData()
        if not settings.scene.active_renderables.Exists(self.check_icon_renderable.key):
            settings.scene.active_renderables.Add(self.check_icon_renderable)

    def Interact(self):
        if self.check_icon_renderable.visible:
            self.check_icon_renderable.visible = False
            self.is_checked = False
        else:
            self.check_icon_renderable.visible = True
            self.is_checked = True

        super().Interact()
        settings.scene.Draw()  # Draw to apply the icon changes

    def Destroy(self):
        super().Destroy()
        self.check_icon_renderable = None
