import pygame

from Engine.Utilities.yaml_reader import Reader
from Engine.BaseClasses.renderable import Renderable

class SpriteRenderable(Renderable):
    """
    The Sprite Renderable class is the base class for renderable sprite elements in the GVNEngine. This includes:
        - Interactables
        - Non-Interactables
        - Backgrounds
        - etc

    The Sprite Renderable class has two accepted values for 'data_path':
        - If a path to an image asset is provided, the renderable will not attempt to load any data, and simply render
          that sprite at position (0,0)

        - If a path to a object .yaml file is provided, it will load the corresponding .yaml file, and use its
          defined position value
    """
    def __init__(self, data_path, pos):
        super().__init__(pos)

        self.renderable_data = {}

        if ".yaml" in data_path:
            # Read in the object data from the associated yaml file
            self.renderable_data = Reader.ReadAll(data_path)
            self.surface = pygame.image.load(self.renderable_data['sprite']).convert_alpha()
            self.rect = self.surface.get_rect()
        else:
            # Provided file was not a data file. Try and load it directly as the image
            try:
                self.surface = pygame.image.load(data_path).convert_alpha()
                self.rect = self.surface.get_rect()
            except Exception as exc:
                print("Failed to load data file for Renderable - Either the file was not found, or it is not a "
                      f"supported file type:\n{exc}\n")
