class RenderableGroup():
    def __init__(self):
        """
        This class mimics the base pygame sprite group class, but uses a dictionary for the renderable list.
        """

        # While the base class for pygame sprite groups track sprites in a list, we'll be using a dict for quick
        # lookup. The renderable "key" will be the key to the sprite which will be the value
        self.renderables = {}

        super().__init__()

    def Add(self, *r_to_add):
        """
        Add the given renderables to the rend dict using the renderable key as the key, and the actual
        renderable as the value
        """
        for renderable in r_to_add:
            if renderable.key is None:
                print(f"Renderable has no key assigned - Removal will be impossible: {renderable}")
            self.renderables[renderable.key] = renderable

    def Remove(self, *key_to_remove):
        """
        Remove the given renderable key from the dict
        """
        for key in key_to_remove:
            try:
                del self.renderables[key]
            except KeyError as exc:
                print(f"Key not found: {exc}")

    def Clear(self):
        pass

    def Get(self):
        """ Returns the list of renderables inside this group"""
        return self.renderables.values()

    def Update(self):
        for renderable in self.renderables.values():
            renderable.update()
