from Engine.Utilities.yaml_reader import Reader
from Engine.BaseClasses.renderable_group import RenderableGroup
from Engine.Core.action_manager import ActionManager

class Scene:
    def __init__(self, scene_data_file, window, pygame_lib, settings, scene_manager):

        self.window = window
        self.pygame_lib = pygame_lib
        self.settings = settings
        self.scene_manager = scene_manager
        self.renderables_group = RenderableGroup()
        self.a_manager = ActionManager(self, settings)

        self.pause_menu = None

        # Keep track of delta time so time-based actions can be more accurate across systems
        self.delta_time = 0

        # Read in the active scene data
        self.scene_data = Reader.ReadAll(scene_data_file)

        # Load any cached data on the scene manager
        if not self.scene_manager.resolution_multiplier:
            self.resolution_multiplier = 1
        else:
            self.resolution_multiplier = self.scene_manager.resolution_multiplier

        self.LoadSceneData()

    def Update(self, input_events):
        self.renderables_group.Update()
        self.a_manager.Update()

        # Pause Menu
        for event in input_events:
            if event.type == self.pygame_lib.KEYDOWN:
                if event.key == self.pygame_lib.K_p:
                    #@TODO: TEMP HACK
                    if self.renderables_group.Exists('Pause_Menu'):
                        print("Pause Menu Open")
                    else:
                        self.pause_menu = self.a_manager.PerformAction(self.scene_manager.pause_menu_data,
                                                                       "create_container")

    def Draw(self):
        #print("*** REDRAWING SCENE ***")

        # Sort the renderable elements by their z-order (Lowest to Highest)
        renderables = sorted(self.renderables_group.renderables.values(), key=lambda renderable: renderable.z_order)

        # Draw any renderables using the screen space multiplier to fit the new resolution
        for renderable in renderables:
            if renderable.visible:
                self.window.blit(renderable.GetSurface(), (renderable.rect.x, renderable.rect.y))

            # Draw any child renderables after drawing the parent
            if renderable.children:
                for child in renderable.children:
                    if child.visible:
                        self.window.blit(child.GetSurface(), (child.rect.x, child.rect.y))

    def SwitchScene(self, scene_file, scene_type):
        self.renderables_group.Clear()
        self.scene_manager.LoadScene(scene_file, scene_type)

    def Resize(self):
        """ Determines a new sprite size based on the difference between the main resolution and the new resolution """

        # Generate the new screen size scale multiplier, then cache it in the scene manager in case scenes change
        new_resolution = self.settings.resolution_options[self.settings.resolution]
        self.resolution_multiplier = self.CalculateScreenSizeMultiplier(self.settings.main_resolution, new_resolution)
        self.scene_manager.resolution_multiplier = self.resolution_multiplier

        # Inform each renderable of the resolution change so they can update their respective elements
        for renderable in self.renderables_group.Get():
            renderable.RecalculateSize(self.resolution_multiplier)
            # Resize any child renderables after resizing the parent
            if renderable.children:
                for child in renderable.children:
                    child.RecalculateSize(self.resolution_multiplier)

        # Redraw the scaled sprites
        self.Draw()

    def LoadSceneData(self):
        """
        Read the scene yaml file, and prepare the scene by spawning object classes, storing scene values, etc. We
        can also use aliases in order to make specific action calls
        """
        # TODO: Create an aliases file so users can write their own

        # 'background' alias for loading the background sprite
        if 'background' in self.scene_data:
            bg_path = self.scene_data['background']
            print(f"Background specified -  Loading: {bg_path}")

            action_data = {
                'action': 'create_background',
                'sprite': bg_path
            }

        self.a_manager.PerformAction(action_data, action_data['action'])

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