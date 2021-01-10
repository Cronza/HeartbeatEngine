class Transition:
    def __init__(self, scene, a_manager, renderable, transition_speed=5):
        self.scene = scene
        self.a_manager = a_manager
        self.renderable = renderable
        self.transition_speed = transition_speed

        self.complete = False

    def Start(self):
        pass

    def Update(self):
        pass

    def Skip(self):
        pass