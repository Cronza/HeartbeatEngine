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
import argparse
import pygame
from HBEngine.Core.Scenes.scene_manager import SceneManager
from HBEngine.Core import settings
from pygame import mixer


clock = None
window = None
scene_manager = None  # Declare the scene manager, but we'll initialize it during the game loop

# DEBUG TRIGGERS
show_fps = False


def Initialize(project_path):
    # @TODO: What is the right way to handle this?
    if not project_path:
        print("Warning: No project path provided - Defaulting to the engine root")

    settings.SetProjectRoot(project_path)
    settings.LoadProjectSettings()

    pygame.display.set_caption(settings.project_settings['Game']['title'])


def Main():
    global clock
    global window
    global scene_manager
    global show_fps

    pygame.init()
    mixer.init()
    clock = pygame.time.Clock()
    window = pygame.display.set_mode(settings.active_resolution)

    scene_manager = SceneManager(window)

    # Start the game loop
    is_running = True
    while is_running is True:
        events = pygame.event.get()

        # Handle all system actions
        for event in events:
            if event.type == pygame.QUIT:
                is_running = False
            if event.type == pygame.KEYDOWN:
                # Maximize
                if event.key == pygame.K_1:
                    UpdateResolution(1, pygame.FULLSCREEN)
                    scene_manager.ResizeScene()
                # Minimize
                if event.key == pygame.K_2:
                    UpdateResolution(0)
                    scene_manager.ResizeScene()
                # Exit
                if event.key == pygame.K_ESCAPE:
                    if settings.active_scene:
                        if settings.active_scene.paused:
                            settings.active_scene.Unpause()
                        else:
                            settings.active_scene.Pause()

                if event.type == pygame.QUIT:
                    is_running = False
                # Debug - FPS
                if event.key == pygame.K_F3:
                    show_fps = not show_fps

        # Update scene logic. This drives the core game functionality
        settings.active_scene.Update(events)

        # Debug Logging
        if show_fps:
            print(clock.get_fps())

        # Refresh any changes
        pygame.display.update()

        # Get the time in miliseconds converted to seconds since the last frame. Used to avoid frame dependency
        # on actions
        settings.active_scene.delta_time = clock.tick(60) / 1000


def UpdateResolution(self, new_size_index, flag=0):
    # Use the given, but always add HWSURFACE and DOUBLEBUF
    if not settings.resolution == new_size_index:
        settings.resolution = new_size_index
        pygame.display.set_mode(settings.resolution_options[new_size_index], flag)

        settings.active_scene.Draw()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--project_path", type=str, nargs="?", const="", help="A file path for a HBEngine Project")
    args = parser.parse_args()
    print(args)
    Initialize(args.project_path)
    Main()
