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


class InterfacePrompt(Interface):
    """
    An interface subclass dedicated to prompts which function as temporary interfaces meant to return information.
    To ensure the invoking party is informed correctly, a callback is expected that accepts an 'any' type argument
    """
    def __init__(self, renderable_data: dict, parent: Renderable = None, close_callback: callable = None):

        self.result = None

        # The structure is: <key>: <callback>
        self.close_callback = close_callback

        #renderable_data["key"] = "!&HBENGINE_INTERNAL_CONFIRM_PROMPT_INTERFACE!&"
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

    def Destroy(self):
        super().Destroy()

        # If applicable, pass the result of the prompt to whomever created the prompt
        self.close_callback(self.result)
