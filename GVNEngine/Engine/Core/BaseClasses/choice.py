from Engine.Core.BaseClasses.renderable_container import Container

class Choice(Container):
    def __init__(self, scene, renderable_data):
        super().__init__(scene, renderable_data)
        self.visible = False

        #Pass in a button list, and generate buttons
        assert 'choices' in self.renderable_data, print(
            f"No 'choices' block assigned to {self}. This makes for an impossible action!")

        #for choice in renderable_data['choices']:
        #    # Create each choice button
        #    self.children.append(self.scene.a_manager.PerformAction(choice, 'create_choice_button'))
