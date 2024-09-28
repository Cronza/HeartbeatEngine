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
from HBEngine.Core import settings, action_manager
from Tools.HBYaml.hb_yaml import Reader
from HBEngine.Core.Objects.renderable import Renderable
from HBEngine.Core.Objects.interface import Interface


class BaseModule:
    MODULE_NAME = "Default"
    RESERVE_INPUT = True  # Disable updates for everything but this module (IE. Scene, other modules)
    CLOSE_ON_SCENE_CHANGE = True  # Prevent this module from persisting between scenes

    def __init__(self, file_path: str):
        self.active_renderables = {}

        # Keep track of all spawned renderables by adding them as children to a root object. When removing this module,
        # instead of tracking each instance down, we can just delete the root and all children will go with it
        self.root_renderable = None
        self.interface = None

    def Start(self):
        pass

    def Shutdown(self):
        """" Shut down the module, cleaning up spawned renderables and objects"""
        if self.root_renderable:
            settings.scene.active_renderables.Remove(self.root_renderable.key)
            self.root_renderable = None
        if self.interface:
            settings.scene.active_renderables.Remove(self.interface.key)
            del settings.scene.active_interfaces[self.interface.key]
            self.interface = None

    def Update(self, events):
        # Update the AM and all child renderables (if applicable) since we reserve input with this module
        action_manager.Update(events)
        if self.root_renderable:
            self.UpdateRenderables([self.root_renderable])

    def UpdateRenderables(self, target: list = None):
        """ Recursively update all renderable objects attached to this module """
        for renderable in target:
            renderable.update()
            if renderable.children:
                self.UpdateRenderables(renderable.children)

    def LoadInterface(self):
        pass

