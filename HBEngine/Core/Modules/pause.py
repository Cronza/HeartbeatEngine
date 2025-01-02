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
from HBEngine.Core.Modules.base import BaseModule


class Pause(BaseModule):
    MODULE_NAME = "Pause"
    RESERVE_THREAD = True  # Disable updates for everything but this module (IE. Scene, other modules)
    CLOSE_ON_SCENE_CHANGE = True  # Prevent this module from persisting between scenes

    def __init__(self, file_path: str):
        super().__init__(file_path)

        # Keep track of all spawned renderables by adding them as children to a root object. When removing this module,
        # instead of tracking each instance down, we can just delete the root and all children will go with it
        self.root_renderable = Renderable({'key': '!&MODULE_PAUSE_ROOT&!', 'z_order': 10000000000})
        self.root_renderable.visible = False
        settings.scene.active_renderables.Add(self.root_renderable)

        # Enable the global 'Pause' state
        settings.paused = True

    def Start(self):
        pause_interface = settings.GetProjectSetting('Default Variables - UI', 'pause_menu_interface')
        if pause_interface == "None" or not pause_interface:
            # Use fallback interface
            # @TODO: Replace this with a generic empty pause menu with the word "Pause" written on it. Maybe a 'quit' button
            # @TODO: That, or update this when we have a starting project where 'Play' doesn't lead to a FileNotFound error
            pause_interface = "HBEngine/Content/Interfaces/pause_menu_01.interface"

        self.LoadInterface(pause_interface)
        settings.scene.Draw()

    def Shutdown(self):
        """" Shut down the module, cleaning up spawned renderables and objects"""
        super().Shutdown()

        # Disable the global 'Pause' state
        settings.paused = False

    def Update(self, events):
        for event in events:
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    # Skip the running action if it's able to be skipped
                    if action_manager.active_actions:
                        for action in action_manager.active_actions:
                            if action.skippable:
                                action.Skip()

        # Update the AM and all child renderables (if applicable) since we reserve input with this module
        action_manager.Update(events)
        if self.root_renderable:
            self.UpdateRenderables([self.root_renderable])

