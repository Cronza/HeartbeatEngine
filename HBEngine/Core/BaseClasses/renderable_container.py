from Core.BaseClasses.renderable import Renderable


class Container(Renderable):
    def __init__(self, scene, renderable_data):
        super().__init__(scene, renderable_data)
        self.visible = False

        #@TODO: Minimize the specific references to objects here so that containers can be more generalized
        # Load any specified objects (Non-interactables)
        if 'sprites' in renderable_data:
            f_objects = renderable_data['sprites']

            for f_object in f_objects:
                self.children.append(self.scene.a_manager.PerformAction(f_object, 'create_sprite'))
        else:
            print('Data file does not specify any sprites')

        # Load any specified interactables
        if 'interactables' in renderable_data:
            f_interactables = renderable_data['interactables']

            for f_interactable in f_interactables:
                self.children.append(self.scene.a_manager.PerformAction(f_interactable, 'create_interactable'))
        else:
            print('Data file does not specify any interactables')

        # Load any specified buttons
        if 'buttons' in renderable_data:
            f_buttons = renderable_data['buttons']

            for f_button in f_buttons:
                self.children.append(self.scene.a_manager.PerformAction(f_button, 'create_button'))
        else:
            print('Data file does not specify any buttons')

        # Load any specified text
        if 'text' in renderable_data:
            f_texts = renderable_data['text']

            for f_text in f_texts:
                self.children.append(self.scene.a_manager.PerformAction(f_text, 'create_text'))
        else:
            print('Data file does not specify any text')

    def GetAllChildren(self) -> list:
        """ Recursively collect all children to this container """
        f_children = []
        return self.GetChild(self, f_children)


    def GetChild(self, parent, f_children):
        """ Given a renderable, recursively collect itself, and any children it has, and return them as a list """

        # If this object has children, loop through them. Collect a reference to the child, then recurse for it's
        # children
        if parent.children:
            for child in parent.children:
                f_children.append(child) # Add the child
                self.GetChild(child, f_children) # Recurse for this child's children

            # Return the list so the caller can continue
            return f_children
        else:
            return parent
