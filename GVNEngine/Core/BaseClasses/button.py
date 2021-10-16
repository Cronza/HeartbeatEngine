from Core.BaseClasses.interactable import Interactable
from Core.BaseClasses.renderable_text import TextRenderable

class Button(Interactable):
    """
    The Button class extends the 'Interactable' class, and adds an additional child 'TextRenderable'
    """
    def __init__(self, scene, renderable_data):
        super().__init__(scene, renderable_data)

        # Initialize text renderable
        button_text_renderable = TextRenderable(
            self.scene,
            self.renderable_data
        )
        self.children.append(button_text_renderable)
        self.scene.active_renderables.Add(button_text_renderable)

    def GetText(self):
        pass

    def SetText(self):
        pass

