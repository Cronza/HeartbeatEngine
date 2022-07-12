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
from HBEngine.Core.Actions.action_manager import ActionManager
from HBEngine.Core.Rendering.renderer import Renderer
from Tools.HBYaml.hb_yaml import Reader


class Scene:
    def __init__(self, scene_data_file, window, scene_manager):

        self.window = window
        self.scene_manager = scene_manager
        self.renderer = Renderer(self.window)

        # The renderer doesn't handle audio, so track music and SFX here
        self.active_sounds = {}
        self.active_music = None  # Only one music stream is supported. Stores a 'SoundAction'

        self.a_manager = ActionManager(self)
        self.pause_menu = None

        # Keep track of delta time so time-based actions can be more accurate across systems
        self.delta_time = 0

        self.scene_data = Reader.ReadAll(Settings.getInstance().ConvertPartialToAbsolutePath(scene_data_file))
        self.LoadSceneData()

    def Update(self, events):
        self.renderer.active_renderables.Update()
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

    def SwitchScene(self, scene_file):
        """ Clears all renderables, and requests a scene change from the scene_manager"""
        self.renderer.active_renderables.Clear()
        self.scene_manager.LoadScene(scene_file)

    def LoadSceneData(self):
        """ Read the scene yaml file, and prepare the scene by spawning object classes, storing scene values, etc """
        raise NotImplementedError("'LoadSceneData' not implemented")

    def Draw(self):
        """ Requests that the renderer redraw the scene """
        self.renderer.Draw()

    def AddToScreen(self, renderable: object):
        """ Adds the provided renderable to the renderer's active renderable stack """
        self.renderer.active_renderables.Add(renderable)

    def GetIsInScene(self, key: str):
        """ Checks if a renderable with the provided key exists in the renderer's active renderable stack """
        return self.renderer.active_renderables.Exists(key)
