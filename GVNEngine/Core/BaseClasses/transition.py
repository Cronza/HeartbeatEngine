class Transition:
    def __init__(self, scene, a_manager, renderable, speed=5):
        self.scene = scene
        self.a_manager = a_manager
        self.renderable = renderable
        self.speed = speed

        self.complete = False

    def Start(self):
        pass

    def Update(self):
        pass

    def Skip(self):
        pass