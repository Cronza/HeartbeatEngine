import argparse
import pygame
from Engine.Core.scene_manager import SceneManager
from Engine.Core.settings import Settings
from pygame import mixer

class GVNEngine:
    def __init__(self, project_path):
        #@TODO: What is the right way to handle this?
        if not project_path:
            raise ValueError("No project path provided - Unable to launch GVNEngine")
            quit(1)

        self.settings = Settings(project_path)
        self.settings.Evaluate(self.settings.project_dir + "/Config/Game.yaml")
        pygame.display.set_caption(self.settings.project_settings['Game']['title'])

        # Declare the scene manager, but we'll initialize it during the game loop
        self.scene_manager = None

        # DEBUG TRIGGERS
        self.show_fps = False

    def Main(self):

        pygame.init()
        mixer.init()
        clock = pygame.time.Clock()
        window = pygame.display.set_mode(self.settings.active_resolution)

        self.scene_manager = SceneManager(window, pygame, self.settings)

        # Start the game loop
        is_running = True
        while is_running is True:
            input_events = pygame.event.get()

            # Handle all system actions
            for event in input_events:
                if event.type == pygame.QUIT:
                    is_running = False
                if event.type == pygame.KEYDOWN:
                    # Maximize
                    if event.key == pygame.K_1:
                        self.UpdateResolution(1, pygame.FULLSCREEN)
                        self.scene_manager.ResizeScene()
                    # Minimize
                    if event.key == pygame.K_2:
                        self.UpdateResolution(0)
                        self.scene_manager.ResizeScene()
                    # Exit
                    if event.key == pygame.K_ESCAPE:
                        is_running = False
                    if event.type == pygame.QUIT:
                        is_running = False
                    # Debug - FPS
                    if event.key == pygame.K_F3:
                        self.show_fps = not self.show_fps

            # Update scene logic. This drives the core game functionality
            self.scene_manager.active_scene.Update(input_events)

            # Debug Logging
            if self.show_fps:
                print(clock.get_fps())

            # Refresh any changes
            pygame.display.update()

            # Get the time in miliseconds converted to seconds since the last frame. Used to avoid frame dependency
            # on actions
            self.scene_manager.active_scene.delta_time = clock.tick(60) / 1000

    def UpdateResolution(self, new_size_index, flag=0):
        # Use the given, but always add HWSURFACE and DOUBLEBUF
        if not self.settings.resolution == new_size_index:
            self.settings.resolution = new_size_index
            pygame.display.set_mode(self.settings.resolution_options[new_size_index], flag)

            self.scene_manager.active_scene.Draw()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('project_path', type=str, help="A file path for a GVNEngine Project")
    args = parser.parse_args()

    engine = GVNEngine(args.project_path)
    engine.Main()
