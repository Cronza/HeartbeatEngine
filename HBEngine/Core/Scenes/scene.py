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
from HBEngine.Core.settings import Settings
from HBEngine.Core.Objects.renderable_group import RenderableGroup
from HBEngine.Core.Actions.action_manager import ActionManager
from Tools.HBYaml.hb_yaml import Reader


class Scene:
    def __init__(self, scene_data_file, window, scene_manager):

        self.window = window
        self.scene_manager = scene_manager
        self.active_renderables = RenderableGroup()
        self.active_sounds = {}
        self.active_music = None  # Only one music stream is supported. Stores a 'SoundAction'
        self.a_manager = ActionManager(self)

        self.pause_menu = None

        # Keep track of delta time so time-based actions can be more accurate across systems
        self.delta_time = 0

        # Read in the active scene data
        self.scene_data = Reader.ReadAll(Settings.getInstance().ConvertPartialToAbsolutePath(scene_data_file))

        # Load any cached data on the scene manager
        if not self.scene_manager.resolution_multiplier:
            self.resolution_multiplier = 1
        else:
            self.resolution_multiplier = self.scene_manager.resolution_multiplier

        self.LoadSceneData()

    def Update(self, events):
        print(self.active_renderables.Get())
        self.active_renderables.Update()
        self.a_manager.Update(events)

        # Pause Menu
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    #@TODO: TEMP HACK
                    if self.active_renderables.Exists('Pause_Menu'):
                        print("Pause Menu Open")
                    else:
                        self.pause_menu = self.a_manager.PerformAction(self.scene_manager.pause_menu_data,
                                                                       "create_container")

    def Draw(self):
        # Sort the renderable elements by their z-order (Lowest to Highest)
        renderables = sorted(self.active_renderables.renderables.values(), key=lambda renderable: renderable.z_order)

        # Draw any renderables using the screen space multiplier to fit the new resolution
        for renderable in renderables:
            if renderable.visible:
                self.window.blit(renderable.GetSurface(), (renderable.rect.x, renderable.rect.y))

            #@TODO: Review if this causes redundant drawing
            # Draw any child renderables after drawing the parent
            if renderable.children:
                for child in renderable.children:
                    if child.visible:
                        self.window.blit(child.GetSurface(), (child.rect.x, child.rect.y))

    def SwitchScene(self, scene_file):
        """ Clears all renderables, and requests a scene change from the scene_manager"""
        self.active_renderables.Clear()
        self.scene_manager.LoadScene(scene_file)

    def Resize(self):
        """ Determines a new sprite size based on the difference between the main resolution and the new resolution """

        # Generate the new screen size scale multiplier, then cache it in the scene manager in case scenes change
        new_resolution = Settings.getInstance().resolution_options[Settings.getInstance().resolution]
        self.resolution_multiplier = self.CalculateScreenSizeMultiplier(Settings.getInstance().main_resolution, new_resolution)
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
