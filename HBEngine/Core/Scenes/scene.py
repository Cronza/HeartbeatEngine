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
from HBEngine.Core.Objects.renderable_group import RenderableGroup
from HBEngine.Core.Objects.interface import Interface
from HBEngine.Core.Objects.interface_pause import InterfacePause
from HBEngine.Core.Actions.action_manager import ActionManager
from Tools.HBYaml.hb_yaml import Reader


class Scene:
    def __init__(self, scene_data_file, window, scene_manager):

        self.window = window
        self.scene_manager = scene_manager
        self.a_manager = ActionManager(self)
        self.active_renderables = RenderableGroup()
        self.active_interfaces = RenderableGroup()
        self.active_sounds = {}  # Stores a dict of 'Sound' objects
        self.active_music = None  # Only one music stream is supported. Stores a 'SoundAction'

        self.stop_interactions = False  # Flag for whether user control should be disabled for interactables
        self.paused = False

        # Keep track of delta time so time-based actions can be more accurate across systems
        self.delta_time = 0

        # Read in the active scene data
        self.scene_data = Reader.ReadAll(settings.ConvertPartialToAbsolutePath(scene_data_file))

        # Load any cached data on the scene manager
        if not self.scene_manager.resolution_multiplier:
            self.resolution_multiplier = 1
        else:
            self.resolution_multiplier = self.scene_manager.resolution_multiplier

        self.LoadSceneData()

    def Update(self, events):
        if not self.paused:
            self.active_interfaces.Update()  # @TODO: Disable updates from all interfaces besides the pause interface
            self.active_renderables.Update()
            self.a_manager.Update(events)
        else:
            self.active_interfaces.Update([self.active_interfaces.GetFromKey("!&HBENGINE_INTERNAL_PAUSE_INTERFACE!&")])

    def Draw(self, renderables: list = None, recurse: bool = False):
        if not renderables and recurse is False:
            renderables = self.active_renderables.Get() + self.active_interfaces.Get()
        # Don't redraw unless we have items to actually draw. This also prevents last minute draw requests during
        # scene changes while cleanup is happening
        if renderables:
            # Sort the renderable elements by their z-order (Lowest to Highest).
            renderables = sorted(renderables, key=lambda renderable: renderable.z_order)

            # Draw any renderables using the screen space multiplier to fit the new resolution
            for item in renderables:
                if item.visible:
                    self.window.blit(item.GetSurface(), (item.rect.x, item.rect.y))

                #@TODO: Review if this causes redundant drawing
                #@TODO: This doesn't handle nested children
                # Draw any child renderables after drawing the parent
                if item.children:
                    for child in item.children:
                        if child.visible:
                            self.window.blit(child.GetSurface(), (child.rect.x, child.rect.y))

                            # Recurse if this child has children
                            if child.children:
                                self.Draw(child.children, True)

    def SwitchScene(self, scene_file):
        """ Clears all renderables, and requests a scene change from the scene_manager"""
        if scene_file:
            self.active_renderables.Clear()  # Clear graphics
            print("Active Sounds", self.active_sounds)
            for sound in self.active_sounds.values():  # Clear SFX
                print("SOUND", sound)
                sound.Stop()
            if self.active_music:  # Clear music
                self.active_music.Stop()

            self.scene_manager.LoadScene(scene_file)
        else:
            raise ValueError("Load Scene Failed - No scene file provided, or a scene type was not provided")

    def Resize(self):
        """ Determines a new sprite size based on the difference between the main resolution and the new resolution """

        # Generate the new screen size scale multiplier, then cache it in the scene manager in case scenes change
        new_resolution = settings.resolution_options[settings.resolution]
        self.resolution_multiplier = self.CalculateScreenSizeMultiplier(settings.main_resolution, new_resolution)
        self.scene_manager.resolution_multiplier = self.resolution_multiplier

        # Inform each renderable of the resolution change so they can update their respective elements
        for renderable in self.active_renderables.Get():
            renderable.RecalculateSize(self.resolution_multiplier)
            # Resize any child renderables after resizing the parent
            if renderable.children:
                for child in renderable.children:
                    child.RecalculateSize(self.resolution_multiplier)

        # Redraw the scaled sprites
        self.Draw()

    def LoadSceneData(self):
        """ Read the scene yaml file, and prepare the scene by spawning object classes, storing scene values, etc """
        raise NotImplementedError("'LoadSceneData' not implemented")

    def LoadInterface(self, interface_file: str, interface_class: type = Interface):
        interface = interface_class(
            self,
            Reader.ReadAll(settings.ConvertPartialToAbsolutePath(interface_file))
        )
        self.active_interfaces.Add(interface)

    def CalculateScreenSizeMultiplier(self, old_resolution, new_resolution):
        """
        Based on a source and target resolution,
        return a tuple of multipliers for the difference (Width & height)
        """
        final_resolution = []

        # Determine if the new resolution height is smaller or larger
        if old_resolution[0] < new_resolution[0]:
            final_resolution.append(new_resolution[0] / old_resolution[0])
        else:
            final_resolution.append(old_resolution[0] / new_resolution[0])

        if old_resolution[1] < new_resolution[1]:
            final_resolution.append(new_resolution[1] / old_resolution[1])
        else:
            final_resolution.append(old_resolution[1] / new_resolution[1])

        return tuple(final_resolution)

    def Pause(self):
        # @TODO: Implement a per-scene flag that controls whether pausing is allowed
        self.LoadInterface("HBEngine/Content/Interfaces/pause_menu_01.yaml", InterfacePause)
        self.Draw()
        self.paused = True

    def Unpause(self):
        # @TODO: Implement a per-scene flag that controls whether pausing is allowed
        self.active_interfaces.Remove("!&HBENGINE_INTERNAL_PAUSE_INTERFACE!&")
        self.Draw()
        self.paused = False
