"""
    The Heartbeat Engine is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    The Heartbeat Engine is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with the Heartbeat Engine. If not, see <https://www.gnu.org/licenses/>.
"""
from HBEngine.Core.DataTypes.input_states import State
from HBEngine.Core.Objects.renderable import Renderable
from HBEngine.Core.Objects.interactable import Interactable
from HBEngine.Core.Objects.renderable_text import TextRenderable


class Button(Interactable):
    """
    The Button class extends the 'Interactable' class, and adds an additional child 'TextRenderable'
    """
    def __init__(self, scene, renderable_data: dict, parent: Renderable = None):
        super().__init__(scene, renderable_data, parent)
        # # Buttons use a container called 'button_text' to store their button text action data. To the user, this is
        # a simplified text renderable as a number of the settings are handled behind-the-scenes here
        self.renderable_data["button_text"]["key"] = f"{self.renderable_data['key']}_Text"

        self.button_text_renderable = TextRenderable(
            self.scene,
            self.renderable_data["button_text"],
            self
        )
        self.children.append(self.button_text_renderable)

        # If the button doesn't make use of a sprite surface, then use the button text surface instead (This allows for
        # text-only buttons)
        if self.surface.get_width() == 0 and self.surface.get_height() == 0:
            self.rect = self.button_text_renderable.rect
            self.surface = self.button_text_renderable.surface

    def GetText(self):
        pass

    def SetText(self):
        pass

    def ChangeState(self, new_state: State):
        # We need to intercept the state change in order to update the button_text state as well
        if new_state != self.state:
            if new_state == State.normal:
                self.button_text_renderable.text_color = self.button_text_renderable.renderable_data["text_color"]
            elif new_state == State.hover:
                self.button_text_renderable.text_color = self.button_text_renderable.renderable_data["text_color_hover"]
            elif new_state == State.pressed:
                self.button_text_renderable.text_color = self.button_text_renderable.renderable_data["text_color_clicked"]

        self.button_text_renderable.WrapText()

        super().ChangeState(new_state)

