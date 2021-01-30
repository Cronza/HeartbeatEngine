"""
This file lists available actions that can be defined in various .yaml files throughout the GVNEngine project.
All actions take in two parameters:

    - scene - Simply a reference to the scene object. This is handled by the engine
    - action_data - This is a dictionary that is created by reading in a section of .yaml. A .yaml example looks like:
        - action: "create_sprite"
          key: "Speaker_01"
          sprite: "Content/Sprites/Characters/Mary/Mary_Happy.png"
          position:
            x: 0.2
            y: 1.4

All actions can be designed to accept and use a variety of different parameters. To learn more, review some of the
provided actions
"""
from Engine.BaseClasses.renderable_sprite import SpriteRenderable
from Engine.BaseClasses.renderable_text import TextRenderable
from Engine.BaseClasses.interactable import Interactable
from Engine.BaseClasses.button import Button
from Engine.BaseClasses.renderable_container import Container
from Engine.BaseClasses.action import Action

class remove_renderable(Action):
    """ Based on a given key, remove the associated renderable from the renderable stack """
    def Start(self):
        if 'key' in self.action_data:
            renderable = self.scene.renderables_group.renderables[self.action_data['key']]

            # Any transitions are applied to the sprite pre-unload
            if 'transition' in self.action_data:
                self.active_transition = self.a_manager.CreateTransition(self.action_data['transition'], renderable)
                self.active_transition.Start()
            else:
                self.scene.renderables_group.Remove(self.action_data['key'])
                self.scene.Draw()
                self.complete = True
        else:
            print("'remove_renderable' action Failed - Key not specified")

    def Update(self):
        if self.active_transition.complete is True:
            print("Transition Complete")
            self.scene.renderables_group.Remove(self.action_data['key'])
            self.complete = True
        else:
            self.active_transition.Update()

    def Skip(self):
        if self.active_transition:
            self.active_transition.Skip()
        self.complete = True

class remove_container(Action):
    def Start(self):
        if 'key' in self.action_data:
            container = self.scene.renderables_group.renderables[self.action_data['key']]

            # Collect a flattened list of all children in this container
            children = container.GetAllChildren()

            if 'transition' in self.action_data:
                # In order to apply the transition to each and every child of the container, we merge the surfaces
                # and combine them into the container surface. That way, the rendering only manages a single
                # surface. This causes containers to be non-functional once a transition starts, as the underlying
                # children are destroyed before the transition begins

                # Merge the surfaces, then delete the child (Grim, I know)
                for child in list(children):
                    container.surface.blit(child.GetSurface(), (child.rect.x, child.rect.y))
                    self.scene.renderables_group.Remove(child.key)

                container.visible = True
                self.active_transition = self.a_manager.CreateTransition(self.action_data['transition'], container)
                self.active_transition.Start()
            else:
                # Remove all children first
                for child in children:
                    self.scene.renderables_group.Remove(child.key)

                self.scene.renderables_group.Remove(self.action_data['key'])
                self.scene.Draw()
                self.complete = True

        else:
            print("'remove_renderable' action Failed - Key not specified")

    def Update(self):
        if self.active_transition.complete is True:
            print("Transition Complete")
            self.scene.renderables_group.Remove(self.action_data['key'])
            self.complete = True
        else:
            self.active_transition.Update()

    def Skip(self):
        if self.active_transition:
            self.active_transition.Skip()
        self.complete = True

class create_background(Action):
    """
    Creates a specialized 'SpriteRenderable', configured to suit a background image. Returns a
    'SpriteRenderable'
    """
    def Start(self):
        self.skippable = False

        # Background-specific adjustments
        self.action_data['position'] = (0,0)
        self.action_data['key'] = 'Background'
        self.action_data['center_align'] = False

        # PROJECT DEFAULTS OVERRIDE
        if 'z_order' not in self.action_data:
            self.action_data['z_order'] = self.scene.settings.projectSettings['SpriteSettings']['background_z_order']

        new_sprite = SpriteRenderable(
            self.scene,
            self.action_data,
        )

        self.scene.renderables_group.Add(new_sprite)

        self.scene.Draw()
        self.complete = True

        return new_sprite

class create_dialogue_interface(Action):
    """
    Creates sprite renderables for the dialogue and speaker text, and assigns them to the renderable stack using
    pre-configured settings
    """
    def Start(self):
        self.skippable = False

        # Action-specific adjustments
        self.action_data['key'] = 'DialogueFrame'

        # PROJECT DEFAULTS OVERRIDE
        if 'sprite' not in self.action_data:
            self.action_data['sprite'] = self.scene.settings.projectSettings['DialogueSettings'][
                'dialogue_frame_sprite']

        if 'position' not in self.action_data:
            self.action_data['position'] = self.scene.settings.projectSettings['DialogueSettings'][
                'dialogue_frame_position']

        if 'z_order' not in self.action_data:
            self.action_data['z_order'] = self.scene.settings.projectSettings['DialogueSettings'][
                'dialogue_frame_z_order']

        if 'center_align' not in self.action_data:
            self.action_data['center_align'] = self.scene.settings.projectSettings['DialogueSettings'][
                'dialogue_frame_center_align']

        dialogue_frame = SpriteRenderable(
            self.scene,
            self.action_data
        )

        # Add the dialogue interface to the sprite group so they exist until explicitly unloaded
        self.scene.renderables_group.Add(dialogue_frame)

        self.scene.Draw()
        self.complete = True

class create_sprite(Action):
    """
    Create a sprite renderable using passed in settings. Returns a 'SpriteRenderable'
    """
    def Start(self):
        # OVERRIDES WITH NO PROJECT DEFAULTS
        if 'position' not in self.action_data:
            self.action_data['position'] = (0, 0)

        # PROJECT DEFAULTS OVERRIDE
        if 'z_order' not in self.action_data:
            self.action_data['z_order'] = self.scene.settings.projectSettings['SpriteSettings'][
                'z_order']

        if 'center_align' not in self.action_data:
            self.action_data['center_align'] = self.scene.settings.projectSettings['SpriteSettings'][
                'center_align']

        new_sprite = SpriteRenderable(
            self.scene,
            self.action_data
        )

        # If the user requested a flip action, do so
        if 'flip' in self.action_data:
            if self.action_data['flip']:
                new_sprite.Flip()

        self.scene.renderables_group.Add(new_sprite)

        # Any transitions are applied to the sprite post-load
        if 'transition' in self.action_data:
            self.active_transition = self.a_manager.CreateTransition(self.action_data['transition'], new_sprite)
            self.active_transition.Start()
        else:
            self.scene.Draw()
            self.complete = True

        return new_sprite

    def Update(self):
        if self.active_transition.complete:
            print("Transition Complete")
            self.complete = True
        else:
            self.active_transition.Update()

    def Skip(self):
        if self.active_transition:
            self.active_transition.Skip()
        self.complete = True

class create_interactable(Action):
    """ Creates an interactable renderable, and adds it to the renderable stack. Returns an 'Interactable'"""
    def Start(self):
        self.skippable = False

        # OVERRIDES WITH NO PROJECT DEFAULTS
        if 'position' not in self.action_data:
            self.action_data['position'] = (0, 0)

        # PROJECT DEFAULTS OVERRIDE
        if 'z_order' not in self.action_data:
            self.action_data['z_order'] = self.scene.settings.projectSettings['InteractableSettings'][
                'z_order']

        if 'center_align' not in self.action_data:
            self.action_data['center_align'] = self.scene.settings.projectSettings['InteractableSettings'][
                'center_align']

        new_renderable = Interactable(
            self.scene,
            self.action_data,
        )

        # If the user requested a flip action, do so
        if 'flip' in self.action_data:
            if self.action_data['flip']:
                new_renderable.Flip()

        self.scene.renderables_group.Add(new_renderable)

        self.scene.Draw()
        self.complete = True

        return new_renderable

class create_text(Action):
    """
    Create a TextRenderable at the target location, with the given settings. Returns a 'TextRenderable'
    """
    def Start(self):

        # OVERRIDES WITH NO PROJECT DEFAULTS
        if 'position' not in self.action_data:
            self.action_data['position'] = (0,0)

        # PROJECT DEFAULTS OVERRIDE
        if 'z_order' not in self.action_data:
            self.action_data['z_order'] = self.scene.settings.projectSettings['TextSettings']['z_order']

        if 'center_align' not in self.action_data:
            self.action_data['center_align'] = self.scene.settings.projectSettings['TextSettings']['center_align']

        if 'font' not in self.action_data:
            self.action_data['font'] = self.scene.settings.projectSettings['TextSettings']['font']

        if 'text_size' not in self.action_data:
            self.action_data['text_size'] = self.scene.settings.projectSettings['TextSettings']['size']

        if 'text_color' not in self.action_data:
            self.action_data['text_color'] = self.scene.settings.projectSettings['TextSettings']['color']

        new_text_renderable = TextRenderable(
            self.scene,
            self.action_data
        )

        # Add the text to the renderables list instead of the sprite group as text is a temporary element that is
        # meant to be drawn over
        self.scene.renderables_group.Add(new_text_renderable)

        if 'transition' in self.action_data:
            self.active_transition = self.a_manager.CreateTransition(self.action_data['transition'], new_text_renderable)
            self.active_transition.Start()
        else:
            self.scene.Draw()
            self.complete = True

        return new_text_renderable

    def Update(self):
        if self.active_transition.complete is True:
            print("Transition Complete")
            self.complete = True
        else:
            self.active_transition.Update()

    def Skip(self):
        if self.active_transition:
            self.active_transition.Skip()
        self.complete = True

class create_button(Action):
    """ Creates a button interactable, and adds it to the renderable stack. Returns a 'Button' """
    def Start(self):
        self.skippable = False

        # OVERRIDES WITH NO PROJECT DEFAULTS
        if 'position' not in self.action_data:
            self.action_data['position'] = (0, 0)

        if 'text_position' not in self.action_data:
            self.action_data['text_position'] = self.action_data['position']

        # PROJECT DEFAULTS OVERRIDE
        if 'sprite' not in self.action_data:
            self.action_data['sprite'] = self.scene.settings.projectSettings['ButtonSettings']['sprite']

        if 'sprite_hover' not in self.action_data:
            self.action_data['sprite_hover'] = self.scene.settings.projectSettings['ButtonSettings']['sprite_hover']

        if 'sprite_clicked' not in self.action_data:
            self.action_data['sprite_clicked'] = self.scene.settings.projectSettings['ButtonSettings']['sprite_clicked']

        if 'z_order' not in self.action_data:
            self.action_data['z_order'] = self.scene.settings.projectSettings['ButtonSettings']['button_z_order']

        if 'center_align' not in self.action_data:
            self.action_data['center_align'] = self.scene.settings.projectSettings['ButtonSettings']['button_center_align']

        if 'text_z_order' not in self.action_data:
            self.action_data['text_z_order'] = self.scene.settings.projectSettings['ButtonSettings']['text_z_order']

        if 'text_center_align' not in self.action_data:
            self.action_data['center_align'] = self.scene.settings.projectSettings['ButtonSettings']['text_center_align']

        if 'font' not in self.action_data:
            self.action_data['font'] = self.scene.settings.projectSettings['ButtonSettings']['font']

        if 'text_size' not in self.action_data:
            self.action_data['text_size'] = self.scene.settings.projectSettings['ButtonSettings']['text_size']

        if 'text_color' not in self.action_data:
            self.action_data['text_color'] = self.scene.settings.projectSettings['ButtonSettings']['text_color']

        new_renderable = Button(
            self.scene,
            self.action_data
        )

        # If the user requested a flip action, do so
        if 'flip' in self.action_data:
            if self.action_data['flip']:
                new_renderable.Flip()

        self.scene.renderables_group.Add(new_renderable)

        self.scene.Draw()
        self.complete = True

        return new_renderable

class create_container(Action):
    """ Creates a simple container renderable with the provided action data. Returns a 'Container' """

    # @TODO: Update to new workflow
    def Start(self):
        self.skippable = False

        # Container-specific adjustments
        self.action_data['position'] = (0, 0)
        self.action_data['z_order'] = 0
        self.action_data['center_align'] = False

        # Containers aren't rendered, so use defaults
        new_renderable = Container(
            self.scene,
            self.action_data,
        )

        # If the user requested a flip action, do so
        if 'flip' in self.action_data:
            if self.action_data['flip']:
                new_renderable.Flip()

        self.scene.renderables_group.Add(new_renderable)

        self.scene.Draw()
        self.complete = True

        return new_renderable

class load_scene(Action):
    """
    Switches scenes to the one specified in the action data. Requires an applicable scene type be provided. Returns
    nothing
    """
    def Start(self):
        self.skippable = False

        if 'scene_file' in self.action_data and 'scene_type' in self.action_data:
            self.scene.SwitchScene(self.action_data['scene_file'], self.action_data['scene_type'])
        else:
            print('Load Scene Failed - No scene file provided, or a scene type was not provided')

        self.complete = True

class quit_game(Action):
    """ Immediately closes the game """
    def Start(self):
        self.skippable = False
        self.scene.pygame_lib.quit()
        exit()

# -------------- DIALOGUE ACTIONS --------------

class dialogue(Action):
    """
    Create dialogue and speaker text renderables, and add them to the renderable stack using pre-configured settings
    Returns None
    """

    def Start(self):

        # If the user has specified a 'speaker' block, build the speaker renderable
        if 'speaker' in self.action_data:
            # Dialogue-specific adjustments
            self.action_data['speaker']['key'] = 'SpeakerText'

            # PROJECT DEFAULTS OVERRIDE
            if 'position' not in self.action_data['speaker']:
                self.action_data['speaker']['position'] = self.scene.settings.projectSettings['DialogueSettings'][
                    'speaker_text_position']

            if 'z_order' not in self.action_data['speaker']:
                self.action_data['speaker']['z_order'] = self.scene.settings.projectSettings['DialogueSettings'][
                    'speaker_z_order']

            if 'center_align' not in self.action_data['speaker']:
                self.action_data['speaker']['center_align'] = self.scene.settings.projectSettings['DialogueSettings'][
                    'speaker_center_align']

            if 'font' not in self.action_data['speaker']:
                self.action_data['speaker']['font'] = self.scene.settings.projectSettings['DialogueSettings'][
                    'speaker_font']

            if 'text_size' not in self.action_data['speaker']:
                self.action_data['speaker']['text_size'] = self.scene.settings.projectSettings['DialogueSettings'][
                    'speaker_text_size']

            if 'text_color' not in self.action_data['speaker']:
                self.action_data['speaker']['text_color'] = self.scene.settings.projectSettings['DialogueSettings'][
                    'speaker_text_color']

            new_speaker_text = TextRenderable(
                self.scene,
                self.action_data['speaker']
            )
            # Speaker text does not support transitions currently
            self.scene.renderables_group.Add(new_speaker_text)

        # If the user has specified a 'dialogue' block, build the speaker renderable
        if 'dialogue' in self.action_data:
            # Dialogue-specific adjustments
            self.action_data['dialogue']['key'] = 'DialogueText'

            # PROJECT DEFAULTS OVERRIDE
            if 'position' not in self.action_data['dialogue']:
                self.action_data['dialogue']['position'] = self.scene.settings.projectSettings['DialogueSettings'][
                    'dialogue_text_position']

            if 'z_order' not in self.action_data['dialogue']:
                self.action_data['dialogue']['z_order'] = self.scene.settings.projectSettings['DialogueSettings'][
                    'dialogue_z_order']

            if 'center_align' not in self.action_data['dialogue']:
                self.action_data['dialogue']['center_align'] = self.scene.settings.projectSettings['DialogueSettings'][
                    'dialogue_center_align']

            if 'font' not in self.action_data['dialogue']:
                self.action_data['dialogue']['font'] = self.scene.settings.projectSettings['DialogueSettings'][
                    'dialogue_font']

            if 'text_size' not in self.action_data['dialogue']:
                self.action_data['dialogue']['text_size'] = self.scene.settings.projectSettings['DialogueSettings'][
                    'dialogue_text_size']

            if 'text_color' not in self.action_data['dialogue']:
                self.action_data['dialogue']['text_color'] = self.scene.settings.projectSettings['DialogueSettings'][
                    'dialogue_text_color']

            new_dialogue_text = TextRenderable(
                self.scene,
                self.action_data['dialogue']
            )

            self.scene.renderables_group.Add(new_dialogue_text)

            # By default, dialogue text fades in. However, allow the user to override this behaviour
            if 'transition' in self.action_data['dialogue']:
                self.active_transition = self.a_manager.CreateTransition(self.action_data['dialogue']['transition'],
                                                                         new_dialogue_text)
                self.active_transition.Start()
            else:
                self.action_data['dialogue']['transition'] = {
                    'transition_type': 'fade_in',
                    'transition_speed': 1000
                }
                self.active_transition = self.a_manager.CreateTransition(self.action_data['dialogue']['transition'],
                                                                         new_dialogue_text)
                self.active_transition.Start()

        return None

    def Update(self):
        if self.active_transition.complete is True:
            print("Transition Complete")
            self.complete = True
        else:
            self.active_transition.Update()

    def Skip(self):
        if self.active_transition:
            self.active_transition.Skip()
        self.complete = True

#@TODO: Organize dialogue actions into their own sections (dialogue, choice, choose_branch)
class choice(Action):
    def Start(self):
        pass

class choose_branch(Action):
    def Start(self):
        pass

# -------------- TRANSITION ACTIONS --------------
""" 
These actions function as transitions in their own right, but are not modifiers on existing actions like
those listed in the 'transitions' file
"""

class fade_scene_from_black(Action):
    """ Creates a black texture covering the entire screen, then slowly fades it out. Returns 'SpriteRenderable'"""
    def Start(self):

        # Action-specific adjustments
        self.action_data['position'] = (0, 0)
        self.action_data['key'] = 'Transition'
        self.action_data['center_align'] = False
        self.action_data['sprite'] = "Engine/Content/Sprites/transition_fade_black.png"

        # PROJECT DEFAULTS OVERRIDE
        if 'z_order' not in self.action_data:
            self.action_data['z_order'] = self.scene.settings.projectSettings['SceneTransitionsSettings']['z_order']

        if 'transition_speed' not in self.action_data:
            self.transition_speed = self.scene.settings.projectSettings['SceneTransitionsSettings']['transition_speed']
        else:
            self.transition_speed = self.action_data['transition_speed']

        new_sprite = SpriteRenderable(
            self.scene,
            self.action_data
        )

        self.scene.renderables_group.Add(new_sprite)
        self.scene.Draw()

        self.renderable = new_sprite
        self.progress = self.renderable.GetSurface().get_alpha()
        self.goal = 0

        return new_sprite

    def Update(self):
        self.progress -= (self.transition_speed * self.scene.delta_time)
        self.renderable.GetSurface().set_alpha(self.progress)

        self.scene.Draw()

        if self.progress <= self.goal:
            print("Transition Complete")
            self.complete = True

    def Skip(self):
        self.renderable.GetSurface().set_alpha(self.goal)
        self.scene.Draw()
        self.complete = True
