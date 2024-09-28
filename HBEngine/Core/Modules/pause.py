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


class Pause:
    MODULE_NAME = "Pause"
    RESERVE_INPUT = True  # Disable updates for everything but this module (IE. Scene, other modules)
    CLOSE_ON_SCENE_CHANGE = True  # Prevent this module from persisting between scenes

    def __init__(self, file_path: str):
        self.active_renderables = {}

        # Keep track of all spawned renderables by adding them as children to a root object. When removing this module,
        # instead of tracking each instance down, we can just delete the root and all children will go with it
        self.root_renderable = Renderable({'key': '!&MODULE_PAUSE_ROOT&!', 'z_order': 10000000000})
        self.root_renderable.visible = False
        settings.scene.active_renderables.Add(self.root_renderable)
        self.interface = None

    def Start(self):
        self.LoadInterface()

    def Shutdown(self):
        """" Shut down the module, cleaning up spawned renderables and objects"""
        settings.scene.active_renderables.Remove(self.root_renderable.key)
        if self.interface:
            settings.scene.active_renderables.Remove(self.interface.key)
            del settings.scene.active_interfaces[self.interface.key]
        self.root_renderable = None
        self.interface = None

    """
    def Update(self, events):
        for event in events:
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    # Skip the running action if it's able to be skipped
                    if action_manager.active_actions:
                        for action in action_manager.active_actions:
                            if action.skippable:
                                action.Skip()

                    # No actions active. Go to next
                    else:
                        self.LoadAction()

        # Update the AM and all child renderables (if applicable) since we reserve input with this module
        action_manager.Update(events)
        if self.root_renderable:
            self.UpdateRenderables([self.root_renderable])
    """

    def UpdateRenderables(self, target: list = None):
        for renderable in target:
            renderable.update()
            if renderable.children:
                self.UpdateRenderables(renderable.children)

    def LoadInterface(self):
        """ Load the module interface, adding it as a child to the root renderable and registering it with the scene """
        interface = settings.GetProjectSetting("Default Variables - UI", "pause_menu_interface")
        self.interface = Interface(Reader.ReadAll(settings.ConvertPartialToAbsolutePath(interface)))
        self.root_renderable.children.append(self.interface)

        # Add the interface to the scene so actions can still target it, but leave it out of the renderables list so
        # it's drawn as a group with other module-specific renderables
        settings.scene.active_interfaces[self.interface.key] = self.interface
