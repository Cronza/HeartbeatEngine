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
import pygame
from HBEngine.Core import settings
from HBEngine.Core.Objects.renderable import Renderable
from HBEngine.Core.Objects.interface import Interface


class InterfaceConfirmPrompt(Interface):
    """
    An interface subclass dedicated to confirmation prompts. This class requires renderables with specifc keys
    that it edits to supply text unique to each instance
    """
    def __init__(self, renderable_data: dict, parent: Renderable = None):
        renderable_data["key"] = "!&HBENGINE_INTERNAL_CONFIRM_PROMPT_INTERFACE!&"
        renderable_data["z_order"] = 10000000001
        super().__init__(renderable_data, parent)

        # Confirm that the required renderables are present
        if "Title" not in self.renderable_data or "Body" not in self.renderable_data:
            raise ValueError("Confirmation Prompt Interface does not have the required renderables. Please ensure"
                             "there is a 'Title' renderable and a 'Body' renderable")

    def SetTitleText(self, text: str):
        self.renderable_data['Title'].renderable_data["text"] = text
        self.renderable_data['Title'].WrapText()

    def SetBodyText(self, text: str):
        self.renderable_data['Body'].renderable_data["text"] = text
        self.renderable_data['Body'].WrapText()

