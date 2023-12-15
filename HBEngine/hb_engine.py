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
from HBEngine.Core import settings
from HBEngine.Core.scene import Scene
from HBEngine.Core.Objects.interface_pause import InterfacePause

from pygame import mixer


clock = None
window = None


# DEBUG TRIGGERS
show_fps = False


def Initialize(project_path: str):
    """ Loads project information and paths, and updates the pygame module with project-specific settings """
    # @TODO: What is the right way to handle this?
    if not project_path:
        print("Warning: No project path provided - Defaulting to the engine root")

    settings.SetProjectRoot(project_path)
    settings.LoadProjectSettings()
    pygame.display.set_caption(settings.project_settings['Game']['title'])


def Main():
    global clock
    global window
    global show_fps
    #global modules

    pygame.init()
    mixer.init()
    clock = pygame.time.Clock()
    window = pygame.display.set_mode(settings.active_resolution)
    pause_interface = None  # Instatiated and set during runtime

    # Load the starting scene
    if not settings.project_settings["Game"]["starting_scene"]:
        raise ValueError("No starting scene was provided in the project settings")
    LoadScene(settings.project_settings["Game"]["starting_scene"])

    # Start the game loop
    is_running = True
    while is_running is True:
        events = pygame.event.get()

        # Handle all system actions
        for event in events:
            if event.type == pygame.QUIT:
                is_running = False
            if event.type == pygame.KEYDOWN:
                # Exit
                if event.key == pygame.K_ESCAPE:
                    if settings.scene:
                        if settings.paused:
                            Unpause()
                            pause_interface = None
                        else:
                            pause_interface = Pause()

                if event.type == pygame.QUIT:
                    is_running = False
                # Debug - FPS
                if event.key == pygame.K_F3:
                    show_fps = not show_fps

        if settings.paused:
            settings.scene.active_renderables.Update([pause_interface])
        elif settings.input_owner:
            # Input owners lock out updates for everything but themselves. If one is active, only update it
            settings.input_owner.Update(events)
        else:
            # Update scene logic. This drives the core game functionality
            settings.scene.Update(events)

            # Update active modules. These provide supplementary features
            for module_name, module_obj in settings.modules.items():
                module_obj.Update(events)

        # Debug Logging
        if show_fps:
            print(clock.get_fps())

        # Refresh any changes
        pygame.display.update()

        # Get the time in miliseconds converted to seconds since the last frame. Used to avoid frame dependency
        # on actions
        settings.scene.delta_time = clock.tick(60) / 1000


def Pause() -> InterfacePause:
    interface = settings.scene.LoadInterface("HBEngine/Content/Interfaces/pause_menu_01.interface", InterfacePause)
    settings.scene.Draw()
    settings.paused = True

    return interface


def Unpause():
    settings.scene.UnloadInterface("!&HBENGINE_INTERNAL_PAUSE_INTERFACE!&")
    settings.scene.Draw()
    settings.paused = False


def LoadScene(partial_file_path: str):
    """ Deletes the active scene if applicable, and creates a new one using the provided scene file """
    global window

    # Shutdown any modules that shouldn't persist between scenes
    active_modules = list(settings.modules.items())
    for module_name, module_obj in active_modules:
        if module_obj.CLOSE_ON_SCENE_CHANGE:
            UnloadModule(module_name)

    # Clear any existing scene, and create a new scene with the provided info
    settings.scene = None
    settings.scene = Scene(
        scene_data_file=partial_file_path,
        window=window,
        load_scene_func=LoadScene
    )
    settings.scene.LoadSceneData()


def LoadModule(module_obj: callable, module_file_path: str) -> bool:
    """
    Creates the provided module, and adds it to the active module dict. Returns whether the module was
    successfully created
    """
    # Confirm we haven't already loaded this module
    if module_obj.MODULE_NAME in settings.modules:
        print(f"Warning: Module '{module_obj.MODULE_NAME}' has already been loaded - Unable to load a second time!")
        return False
    else:
        # Instantiate the module
        module = module_obj(module_file_path)

        if module_obj.RESERVE_INPUT:
            if settings.input_owner:
                print(f"Warning: Module '{settings.input_owner.MODULE_NAME}' has already reserved input - Unable to load a second module that reserves input!")
                return False
            settings.input_owner = module

        # Assign and start the module
        settings.modules[module_obj.MODULE_NAME] = module
        module.Start()

    return True


def UnloadModule(module_name: str) -> bool:
    """
    Shuts down the module of the provided name and then deletes it. Returns whether the module was successfully shut
    down and deleted
    """
    if module_name in settings.modules:
        settings.modules[module_name].Shutdown()

        # Clear the input reservation if applicable
        if settings.modules[module_name] is settings.input_owner:
            settings.input_owner = None

        del settings.modules[module_name]
        return True
    else:
        print(f"Warning: Module '{module_name}' is not currently loaded")

    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--project_path", type=str, nargs="?", const="", help="A file path for a HBEngine Project")
    args = parser.parse_args()
    print(args)
    Initialize(args.project_path)
    Main()
