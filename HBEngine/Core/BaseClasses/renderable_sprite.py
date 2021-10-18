import pygame

from Core.BaseClasses.renderable import Renderable

class SpriteRenderable(Renderable):
    """
    The Sprite Renderable class is the base class for renderable sprite elements in the HBEngine. This includes:
        - Interactables
        - Non-Interactables
        - Backgrounds
        - etc
    """
    def __init__(self, scene, renderable_data, initial_rescale=True):
        super().__init__(scene, renderable_data)

        # YAML Parameters
        sprite = self.scene.settings.ConvertPartialToAbsolutePath(self.renderable_data['sprite'])

        try:
            self.surface = pygame.image.load(sprite).convert_alpha()
            self.rect = self.surface.get_rect()
        except Exception as exc:
            print("Failed to load data file for Renderable - Either the file was not found, or it is not a "
                  f"supported file type:\n{exc}\n")

        # For new objects, resize initially in case we're already using a scaled resolution. Allow descendents
        # to defer this though if they need to do any additional work beforehand
        if initial_rescale:
            self.RecalculateSize(self.scene.resolution_multiplier)
