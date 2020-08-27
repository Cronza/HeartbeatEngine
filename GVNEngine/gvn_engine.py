import pygame
from pygame.locals import VIDEORESIZE
from Engine.Core.scene_manager import SceneManager

from Engine.Utilities.yaml_reader import Reader
from Engine.Utilities.settings import Settings

class GVNEngine():
    def __init__(self):
        self.yaml_reader = Reader()

        # Build a settings object to house engine settings
        self.settings = Settings(self.yaml_reader)
        self.settings.EvaluateGameINI("Engine/Game.ini")

        self.scene_manager = None

        self.delta_time = 0

    def Main(self):
        pygame.init()

        window = pygame.display.set_mode(self.settings.resolution_options[self.settings.resolution])
        clock = pygame.time.Clock()

        # Initialize the scene manager
        self.scene_manager = SceneManager(window, pygame, self.settings)

        # Start the game loop
        is_running = True
        while is_running is True:
            input_events = pygame.event.get()

            self.scene_manager.active_scene.Update(input_events)

            #print(clock.get_fps())
            for event in input_events:
                if event.type == pygame.QUIT:
                    is_running = False
                if event.type == VIDEORESIZE:  # Resolution Change
                    print("New Size")
                    print(event.dict['size'])
                    #self.scene_manager.active_scene.Draw(self.settings.main_resolution, event.dict['size'])
                    #self.scene_manager.ResizeScene()
                    print("Resize Triggered")
                if event.type == pygame.KEYDOWN:
                    # Maximize
                    if event.key == pygame.K_1:
                        window = self.UpdateResolution(1, pygame.FULLSCREEN)
                        print("AWWWWWWWWWWWWWWWWWWWWWWW SHIT")
                        self.scene_manager.ResizeScene()
                    # Minimize
                    if event.key == pygame.K_2:
                        window = self.UpdateResolution(0)
                        print("AWWWWWWWWWWWWWWWWWWWWWWW SHIT")
                        self.scene_manager.ResizeScene()
                    # Exit
                    if event.key == pygame.K_ESCAPE:
                        is_running = False

            # Refresh any changes
            pygame.display.update()

            # Ge the time in miliseconds converted to seconds since the last frame. Used to avoid frame dependency
            # on actions
            self.scene_manager.active_scene.delta_time = clock.tick(60) / 1000

    def UpdateResolution(self, new_size_index, flag=0):
        #Use the given, but always add HWSURFACE and DOUBLEBUF
        self.settings.resolution = new_size_index
        pygame.display.set_mode(self.settings.resolution_options[new_size_index], flag)

        self.scene_manager.active_scene.Draw()

if __name__ == "__main__":
    engine = GVNEngine()
    engine.Main()