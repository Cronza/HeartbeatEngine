from Engine.BaseClasses.transition import Transition

"""
def fade_in(scene, renderable, transition_speed = 5):
    for i in range(0, 256, transition_speed):
        renderable.surface.set_alpha(i)
        scene.Draw(
            scene.settings.main_resolution,
            scene.settings.resolution_options[scene.settings.resolution]
        )

        # Since the loop freezes the main thread, run the display update here
        scene.pygame_lib.display.update()
    return

def fade_out(scene, renderable, transition_speed = 5):
    for i in reversed(range(0, 256, transition_speed)):
        renderable.surface.set_alpha(i)
        scene.Draw(
            scene.settings.main_resolution,
            scene.settings.resolution_options[scene.settings.resolution]
        )

        # Since the loop freezes the main thread, run the display update here
        scene.pygame_lib.display.update()
    return

"""
class fade_in(Transition):
    def __init__(self, scene, a_manager, renderable, transition_speed=5):
        super().__init__(scene, a_manager, renderable, transition_speed)

        self.progress = 0
        self.goal = 256

    def Update(self):
        self.progress += self.transition_speed
        self.renderable.surface.set_alpha(self.progress)

        self.scene.Draw(
            self.scene.settings.main_resolution,
            self.scene.settings.resolution_options[self.scene.settings.resolution]
        )

        if self.progress >= self.goal:
            print("Transition Complete")
            self.complete = True

    class fade_out(Transition):
        def __init__(self, scene, a_manager, renderable, transition_speed=5):
            super().__init__(scene, a_manager, renderable, transition_speed)

            self.progress = 256
            self.goal = 256

        def Update(self):
            self.progress += self.transition_speed
            self.renderable.surface.set_alpha(self.progress)

            self.scene.Draw(
                self.scene.settings.main_resolution,
                self.scene.settings.resolution_options[self.scene.settings.resolution]
            )

            if self.progress >= self.goal:
                print("Transition Complete")
                self.complete = True


    def Skip(self):
        pass

