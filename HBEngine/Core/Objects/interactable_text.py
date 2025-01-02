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
import pygame
from HBEngine.Core import settings, action_manager
from HBEngine.Core.DataTypes.input_states import State
from HBEngine.Core.Objects.renderable import Renderable
from HBEngine.Core.Objects.renderable_text import TextRenderable
from Tools.HBYaml.CustomTags.connection import Connection


class InteractableText(TextRenderable):
    """
    The InteractableText class extends the 'TextRenderable' class, and provides additional logic for
    interactivity, including:
    - Normal, hover, and clicked input states
    - A 'click' action

    This class has the following (additional) Renderable Data requirements:
    - text_hover_color (String)
    - text_clicked_color (String)
    - events (Dict)

    """
    def __init__(self, renderable_data: dict, parent: Renderable = None, process_data: bool = True):
        # Parameters
        self.original_text_color = (0, 0, 0) # Used to cache the text color when interacting
        self.text_color_hover = (0, 0, 0)
        self.text_color_clicked = (0, 0, 0)
        self.events = {}

        # Run parent implementation which will perform recalculations with the aforementioned parameters
        super().__init__(renderable_data, parent, process_data)

        self.state = State.normal

        # Track whether the previous input frame was clicking to determine whether this interactable was clicked
        self.isClicking = False

        # Since interactions can contain any number of resulting actions, store the list of actions here
        self.interact_events = []

    def ApplyRenderableData(self):
        if 'text_color_hover' in self.renderable_data:
            if isinstance(self.renderable_data['text_color_hover'], Connection):
                self.text_color_hover = settings.GetConnectionData(
                    self.renderable_data['text_color_hover'])
            else:
                self.text_color_hover = self.renderable_data['text_color_hover']

        if 'text_color_clicked' in self.renderable_data:
            if isinstance(self.renderable_data['text_color_clicked'], Connection):
                self.text_color_clicked = settings.GetConnectionData(
                    self.renderable_data['text_color_clicked'])
            else:
                self.text_color_clicked = self.renderable_data['text_color_clicked']

        if "events" in self.renderable_data:
            self.events = self.renderable_data['events']

        # Run the parent implementation to ensure all changes are considered, and the surfaces are recalculated
        super().ApplyRenderableData()

        # Store a copy of the base text color so we can restore it when necessary
        self.original_text_color = self.text_color

    def update(self, *args):
        super().update()
        if not settings.scene.stop_interactions:
            # If being hovered...
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                # If not already in the hover state...
                if self.state is State.normal:
                    self.ChangeState(State.hover)
                else:  # Track whether the user has released their cursor over the sprite
                    if pygame.mouse.get_pressed()[0] == 1:
                        # Begin the click
                        self.ChangeState(State.pressed)
                        self.isClicking = True
                    elif pygame.mouse.get_pressed()[0] == 0 and self.isClicking is True:
                        # User has released the mouse after clicking this renderable. Reset state
                        self.ChangeState(State.hover)
                        self.isClicking = False
                        self.Interact()
                    elif self.isClicking is True:
                        # End the click
                        self.ChangeState(State.normal)
                        self.isClicking = False

            # If no longer hovering...
            elif self.state is not State.normal:
                self.isClicking = False
                self.ChangeState(State.normal)

    def Interact(self):
        if self.events:
            # Collect and store all event actions
            for array_elem_name, array_elem_data in self.events.items():
                # There is a wrapper layer for each event to give them a unique key. Shed this layer
                self.interact_events.append(array_elem_data[next(iter(array_elem_data))])

            if self.interact_events:
                settings.scene.stop_interactions = True
                if "post_wait" in self.interact_events[0]:
                    if self.interact_events[0]["post_wait"] == "wait_until_complete":
                        action_manager.PerformAction(
                            action_data=self.interact_events[0],
                            action_name=self.interact_events[0]["action"],
                            completion_callback=self.ContinueInteract,
                            parent=self.parent
                        )
                    else:
                        # All other cases use 'no_wait'
                        action_manager.PerformAction(
                            action_data=self.interact_events[0],
                            action_name=self.interact_events[0]["action"],
                            parent=self.parent
                        )
                        self.ContinueInteract()
                else:
                    action_manager.PerformAction(
                        action_data=self.interact_events[0],
                        action_name=self.interact_events[0]["action"],
                        parent=self.parent
                    )
                    self.ContinueInteract()
            else:
                settings.scene.Draw()
        else:
            settings.scene.Draw()

    def ContinueInteract(self):
        self.interact_events.pop(0)

        # If there are still more events, perform them
        if self.interact_events:
            action_manager.PerformAction(
                action_data=self.interact_events[0],
                action_name=self.interact_events[0]["action"],
                completion_callback=self.ContinueInteract,
                parent=self.parent
            )
        else:
            settings.scene.stop_interactions = False

    def ChangeState(self, new_state: State):
        """ Updates the active interact state with the provided state, refreshing the active surface """
        #self.SetActiveSurface(self.GetStateSurface(new_state))
        self.state = new_state

        # Update text color where appropriate
        if new_state == State.normal:
            # Reset using the value stored in the data since the text_color parameter var is out of date
            self.text_color = self.original_text_color
        elif new_state == State.hover:
            self.text_color = self.text_color_hover
        elif new_state == State.pressed:
            self.text_color = self.text_color_clicked

        self.WrapText()

        settings.scene.Draw()
