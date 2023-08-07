from HBEngine.Core.Objects.renderable import Renderable
from HBEngine.Core.Objects.renderable_sprite import SpriteRenderable
from HBEngine.Core.Objects.interactable import Interactable
from HBEngine.Core import settings


class Checkbox(Interactable):
    def __init__(self, scene, renderable_data: dict, parent: Renderable = None):
        super().__init__(scene, renderable_data, parent)

        self.check_icon_renderable = SpriteRenderable(
            scene=self.scene,
            renderable_data={
                "key": f"{self.renderable_data['key']}_Text",
                "position": [0.5, 0.5],
                "sprite": self.renderable_data["sprite_icon"],
                "z_order": self.renderable_data["z_order"] + 1
            },
            parent=self
        )
        self.children.append(self.check_icon_renderable)
        self.check_icon_renderable.visible = False

        # Setup Connections
        if "connect" in self.renderable_data:
            if not self.Connect(self.renderable_data["connect"]):
                print(f"Unable to setup connection for '{self.key}'. Please review the connection settings")

    def Interact(self):
        # If a connection has been established, then the check state is determined by the connected value. If no
        # connection is active, then the check state is set by the interaction
        if not self.connected:
            if self.check_icon_renderable.visible:
                self.check_icon_renderable.visible = False
            else:
                self.check_icon_renderable.visible = True

        super().Interact()
        self.scene.Draw()  # Draw to apply the icon changes

    def ConnectionUpdate(self, new_value):
        print("New Value", new_value)
        self.check_icon_renderable.visible = new_value
