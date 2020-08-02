import pygame

class Renderable(pygame.sprite.Sprite):
    """
    The Renderable class is the base class for all renderable elements in the GVNEngine. This includes:
        - Sprites
        - Text
        - Motion graphics
        - Etc

    This class is not meant to be used directly, but to be subclassed into more specialized objects
    """
    def __init__(self, pos):
        super().__init__()

        # Store the normalized screen position for this object
        self.position = pos

        self.surface = None
        self.rect = None

        # Allow renderables to opt out of center aligning (Generally used for things like background sprites, or
        # screen-width sprites
        self.center_align = True

        # For indentification in the rendering stack, allow all renderables the ability be to assigned a unique
        # identifier
        self.key = None

        # Control render order
        self.z_order = 0

    def UpdateRect(self, new_pos):
        """ Sets the rect location to the provided X and Y"""
        self.rect.x = new_pos[0]
        self.rect.y = new_pos[1]
