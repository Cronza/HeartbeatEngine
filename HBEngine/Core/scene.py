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

from HBEngine.Core.Objects.renderable_group import RenderableGroup
from HBEngine.Core.Objects.interface import Interface
from Tools.HBYaml.hb_yaml import Reader


class Scene:
    def __init__(self, scene_data_file: str, window: pygame.Surface, load_scene_func: callable):

        # Read in the active scene data
        self.scene_data = Reader.ReadAll(settings.ConvertPartialToAbsolutePath(scene_data_file))

        self.window = window

        # All renderable elements, including module and interface items. Only top-most parents objects will be present
        # here, as children are recursively drawn
        self.active_renderables = RenderableGroup()

        # All interface objects. This dict is only for access, not for updating or drawing. References are kept separate
        # here as some interfaces may be nested, which would prevent them from being accessible in 'active_renderables'
        self.active_interfaces = {}

        self.active_sounds = {}  # Stores a dict of 'Sound' objects
        self.active_music = None  # Only one music stream is supported. Stores a 'SoundAction'

        self.input_owner = None  # Reserves input for strictly one object and its children
        self.stop_interactions = False  # Flag for whether user control should be disabled for interactables
        self.allow_pausing = self.scene_data["settings"][
            "allow_pausing"]  # Allow disabling pause functionality (Valid for menu scenes or special sequences)

        # Callbacks
        self.load_scene_func = load_scene_func

        # Keep track of delta time so time-based actions can be more accurate across systems
        self.delta_time = 0

    def Update(self, events):
        self.active_renderables.Update()
        action_manager.Update(events)

    def Draw(self, renderables: list = None, is_recursing: bool = False):
        """
        Draw all active renderables and interfaces to the screen. If a list of renderables are provided, only those
        are drawn.
        """
        if not renderables and is_recursing is False:
            renderables = self.active_renderables.Get()

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
                # Draw any child renderables after drawing the parent
                if item.children:
                    children = sorted(item.children, key=lambda child_item: child_item.z_order)
                    for child in children:
                        if child.visible:
                            self.window.blit(child.GetSurface(), (child.rect.x, child.rect.y))

                            # Recurse if this child has children
                            if child.children:
                                self.Draw(child.children, True)

    def SwitchScene(self, scene_file):
        """ Clears all renderables, and requests a scene change """
        if scene_file:
            action_manager.Clear()  # Clear actions

            self.active_renderables.Clear()  # Clear graphics
            for sound in self.active_sounds.values():  # Clear SFX
                sound.Stop()
            if self.active_music:  # Clear music
                self.active_music.Stop()

            self.load_scene_func(scene_file)
        else:
            raise ValueError("Load Scene Failed - No scene file provided, or a scene type was not provided")

    def LoadSceneData(self):
        """ Read the scene yaml file, and prepare the scene by spawning object classes, storing scene values, etc """
        # Load any applicable interfaces
        if self.scene_data["settings"]["interface"] and self.scene_data["settings"]["interface"] != "None":
            self.LoadInterface(self.scene_data["settings"]["interface"])

        # Render scene items
        if "scene_items" in self.scene_data:
            for item in self.scene_data["scene_items"]:
                action_name, action_data = next(iter(item.items()))
                action_manager.PerformAction(action_data, action_name)
        else:
            raise ValueError("'scene_items' missing from the scene file")

        self.Draw()

    def LoadInterface(self, interface_file: str, interface_class: type = Interface) -> Interface:
        interface = interface_class(Reader.ReadAll(settings.ConvertPartialToAbsolutePath(interface_file)))
        self.active_renderables.Add(interface)
        self.active_interfaces[interface.key] = interface

        return interface

    def UnloadInterface(self, key_to_remove: str) -> bool:
        try:
            self.active_renderables.Remove(key_to_remove)
            del self.active_interfaces[key_to_remove]
            return True
        except KeyError as exc:
            print(f"Interface key not found: {exc}")
        except Exception as rexc:
            print(f"Unknown error while removing interface: {rexc}")

        return False
