"""
    The Heartbeat Engine is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    The Heartbeat Engine is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with the Heartbeat Engine. If not, see <https://www.gnu.org/licenses/>.
"""


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

class fade_in(Transition):
    def __init__(self, scene, a_manager, renderable, speed=5):
        super().__init__(scene, a_manager, renderable, speed)

        self.progress = 0
        self.goal = 256

    def Start(self):
        # Start the fade in at 0 opacity
        self.renderable.GetSurface().set_alpha(0)
        self.scene.Draw()

    def Update(self):
        self.progress += (self.speed * self.scene.delta_time)
        self.renderable.GetSurface().set_alpha(self.progress)

        self.scene.Draw()

        if self.progress >= self.goal:
            print("Transition Complete")
            self.complete = True
        # TODO: If you have an unload and load action next to eachother withou a pause, and those two actions refer to
        # TODO: the same key, they'll attempt to overrid eachother. We need a function for "wait" that works alongside
        # TODO: "wait_for_input"

    def Skip(self):
        self.renderable.GetSurface().set_alpha(self.goal)
        self.scene.Draw()
        self.complete = True

class fade_out(Transition):
    def __init__(self, scene, a_manager, renderable, speed=5):
        super().__init__(scene, a_manager, renderable, speed)

        self.progress = self.renderable.GetSurface().get_alpha()
        self.goal = 0

    def Update(self):
        self.progress -= (self.speed * self.scene.delta_time)
        self.renderable.GetSurface().set_alpha(self.progress)

        self.scene.Draw()

        if self.progress <= self.goal:
            print("Transition Complete")
            self.complete = True

    def Skip(self):
        self.renderable.GetSurface().set_alpha(self.goal)
        self.scene.Draw()
        self.complete = True

class text_loading(Transition):
    """ Reveals each letter of a text renderable's text sequentially based on the provided transition speed """
    def __init__(self, scene, a_manager, renderable, speed=5):
        super().__init__(scene, a_manager, renderable, speed)

        self.progress = ""
        self.goal = 0


    def Update(self):
        self.progress -= (self.speed * self.scene.delta_time)
        self.renderable.GetSurface().set_alpha(self.progress)

        self.scene.Draw()

        if self.progress <= self.goal:
            print("Transition Complete")
            self.complete = True

    def Skip(self):
        self.renderable.GetSurface().set_alpha(self.goal)
        self.scene.Draw()
        self.complete = True

