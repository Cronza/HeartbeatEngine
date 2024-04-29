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
import pygame.mixer
import copy, operator
from HBEngine.Core import settings
from HBEngine.Core.Objects.renderable import Renderable
from HBEngine.Core.Objects.renderable_sprite import SpriteRenderable
from HBEngine.Core.Objects.renderable_text import TextRenderable
from HBEngine.Core.Objects.interactable import Interactable
from HBEngine.Core.Objects.button import Button
from HBEngine.Core.Objects.choice import Choice
from HBEngine.Core.Objects.checkbox import Checkbox
from HBEngine.Core.Objects.audio import Sound, Music
from HBEngine.Core.Objects.renderable_container import Container
from HBEngine.Core.Modules import dialogue as m_dialogue
from Tools.HBYaml.hb_yaml import Reader

"""
----------------
--- Overview ---
----------------

This file contains every action available to a user when building their games. These actions range from creating
renderables such as sprites (create_sprite) and buttons (create_button), to affecting state such as with
pausing (pause) and muting (set_mute).

Due to the open-ended nature of what actions do, they use a specialized Dictionary structure to house their
parameters. This can be found in the 'ACTION_DATA' class attribute. 

-----------------------------------
--- Understanding 'ACTION_DATA' ---
-----------------------------------
The 'ACTION_DATA' listed for each action not only contains the parameters and their values for that action, but also 
Editor-Specific details for how they're represented in the editor. This structure is referred to as the "Expanded" 
structure.
 
When users create project files (Scenes, interfaces, etc), they utilize Actions to populate those files. Those actions 
are saved within the project files in a different format of what is found in this file. An example of this looks like:

create_background:
  key: Background
  sprite: HBEngine/Content/Sprites/Backgrounds/Basic_Dark_1280x720.png
  flip: false
  post_wait: no_wait

As you can see, everything except for the parameter name and value have been stripped out. This is called the 
"Simplified" format. The Heartbeat Engine uses this format when reading in project files, but also uses the Expanded 
format of 'ACTION_DATA' to ensure that no parameter is missing. The Heartbeat Editor specifically uses the 
Expanded format of 'ACTION_DATA', but saves files using the Simplified format.

-----------------------------------
--- Populating 'ACTION_DATA' ---
-----------------------------------

Actions do not require that ACTION_DATA be populated, and can simply have it be "ACTION_DATA = {}"

However, when populated, ACTION_DATA lists every parameter that the action requires. These parameters can be anything, 
whether that is the sprite used for an image or the volume level for an SFX. This list is optional, but when used can
look like the following:

{
    "key": {
        "type": "String",
        "value": "Hello World!",
        "flags": ["editable", "preview"]
    }
}

---------------------------------
--- Parameter Entry Legend ---
---------------------------------
    value:      The active contents for the parameter. This represents the starting value for the parameter, and is 
                where the user stores their inputs. If present, 'default' will be ignored. 
    default:    Used to connect a parameter to a easily accessible variable defined in the 'Game.yaml' project 
                settings. The syntax is: [<category>, <value>]. This key is used to allow abstraction from modifying 
                actions on a per-instance basis, and instead modify their parameters globally in one singular location. 
                Not every parameter should use this key as some parameters are better suited for manual configuration 
                per-instance.  
    connection: Which project variable this parameter is connected to. If set, 'value' and 'default' will be ignored in 
                favor of the data stored in the referenced variable.

    [Editor Specific]
    type:       Controls which input widget is used when displayed in the editor (IE. Dropdown vs Text Box)
    template:   A special keyword for parameters that allow children to be dynamically created by the
                user. This keyword is only usable with the 'Array' type
    flags:      A list of key words that various sub-editors use. Options:
        editable:       Controls whether a parameter can be changed by the user either in the editor
        preview:        Controls whether certain editors can show the value of the parameter in additional areas of 
                        the interface
        no_exclusion:   Controls whether to remove editor-specific property exclusions for a property and its children. 
                        This is necessary when editors such as 'PointAndClick' have blanket exclusions for properties 
                        such as 'post_wait', and you need it available for a particular action
    
"""


# -------------- BASE ACTIONS --------------


class Action:
    def __init__(self, simplified_ad: dict, parent: Renderable = None, no_draw: bool = False):
        self.parent: Renderable = parent  # Who should be the parent of new renderables created by this action. If blank, defaults to the scene
        self.simplified_ad = simplified_ad  # User-provided action data using the simplified structure
        self.active_transition = None
        self.speed = 500
        self.skippable = True
        self.complete = False
        self.completion_callback = None  # Called by the action manager before it deletes the action

        self.no_draw = no_draw  # Whether to skip drawing for new renderables. Useful when batch performing creation actions

    def Start(self):
        pass

    def Update(self, events):
        pass

    def Skip(self):
        pass

    def Complete(self):
        self.complete = True

    def AddToScene(self, new_renderable):
        """ Adds the provided renderable either to the scene's draw stack, or to 'self.parent' as a child """
        if self.parent:
            # If an object with the matching key already exists, delete it first
            item_to_delete = None
            for child in self.parent.children:
                if child.key == new_renderable.key:
                    item_to_delete = child
                    break
            if item_to_delete:
                self.parent.children.remove(item_to_delete)
            self.parent.children.append(new_renderable)
        else:
            settings.scene.active_renderables.Add(new_renderable)

    def ValidateActionData(self, extended_ad: dict, simplified_ad: dict = None):
        """
        Recursively compares the action's 'simplified_ad' against the provided 'ext_ad', updating the former when
        it is missing data found in the latter

        This update performs the following adjustments:
        - Adds parameters that are missing from the Simplified format using the unedited data from the Expanded format
        - Replaces values with global values if a parameter is using a global setting
        """

        for param_name, param_data in extended_ad.items():
            if "children" in param_data:
                if param_name in simplified_ad:
                    # Param found in simplified data. Recursively update the children as well
                    self.ValidateActionData(param_data["children"], simplified_ad[param_name])

            elif "template" in param_data:
                # Parameters that use templates have a unique data structure in that each child is
                # generated from the template instead of being a part of the data to begin with. Due to this,
                # we must compare the simplified data against the template specifically
                #
                # The template data structure is usually a few layers deep. Example:
                #    choices: (Array)
                #        choice: (ArrayElement)
                #            ...

                # Because the top level key names for ArrayElements are generated, we can't do a typical key name
                # search (IE. 'choice_01' instead of 'choice' which matches the ACTION_DATA). Instead, we're accessing
                # the values dict directly
                template_data = list(param_data["template"].values())[0]

                # Update each ArrayElement
                for element_name, element_data in simplified_ad[param_name].items():
                    # Skip a level as this is the "ArrayElement" container

                    self.ValidateActionData(template_data["children"], element_data)

            elif param_name not in simplified_ad:
                if "global" in param_data:
                    # Global active. Set 'value' to the corresponding global value
                    simplified_ad[param_name] = settings.GetProjectSetting(param_data["global"][0], param_data["global"][1])
                else:
                    # No global active. Use default value from the expanded data
                    simplified_ad[param_name] = param_data["default"]


class SoundAction(Action):
    # @TODO: Add Pause function
    def __init__(self, simplified_ad: dict, parent: Renderable = None, no_draw: bool = False):
        super().__init__(simplified_ad)
        self.assigned_channel = None


# -------------- GRAPHICS ACTIONS --------------


class remove_renderable(Action):
    """ Based on a given key, remove the associated renderable from the renderable stack """
    DISPLAY_NAME = "Remove Renderable"
    ACTION_DATA = {
        "key": {
            "type": "String",
            "value": "",
            "connection": "",
            "flags": ["editable", "connectable", "preview"],
        },
        "transition": {
            "type": "Container",
            "flags": ["preview"],
            "children": {
                "type": {
                    "type": "Dropdown",
                    "value": "None",
                    "options": ["None", "fade_out"],
                    "flags": ["editable", "preview"],
                },
                "speed": {
                    "type": "Int",
                    "value": 500,
                    "flags": ["editable", "preview"],
                },
            },
        },
        "conditions": {
            "type": "Array",
            "flags": ["editable"],
            "children": {},
            "template": {
                "condition": {
                    "type": "Array_Element",
                    "flags": ["editable"],
                    "children": {
                        "value_name": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        },
                        "operator": {
                            "type": "Dropdown",
                            "value": "equal",
                            "options": ["equal", "not_equal", "less", "greater", "greater-or-equal", "lesser-or-equal"],
                            "flags": ["editable"],
                        },
                        "goal": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        }
                    }
                }
            },
        }
    }

    def Start(self):
        self.ValidateActionData(self.ACTION_DATA, self.simplified_ad)

        renderable = settings.scene.active_renderables.renderables[self.simplified_ad['key']]
        children = []

        if isinstance(renderable, Container):
            # Collect a flattened list of all children in this container
            children = renderable.GetAllChildren()

        # Any transitions are applied to the sprite pre-unload
        if "None" not in self.simplified_ad["transition"]["type"]:
            if children:
                # In order to apply the transition to each and every child of the container, we merge the surfaces
                # and combine them into the container surface. That way, the rendering only manages a single
                # surface. This causes containers to be non-functional once a transition starts, as the underlying
                # children are destroyed before the transition begins

                # Merge the surfaces, then delete the child (Grim, I know)
                for child in children:
                    renderable.surface.blit(child.GetSurface(), (child.rect.x, child.rect.y))
                    settings.scene.active_renderables.Remove(child.key)

                renderable.visible = True

            from HBEngine.Core import action_manager
            self.active_transition = action_manager.CreateTransition(self.simplified_ad["transition"], renderable)
            self.active_transition.Start()
        else:
            if children:
                # Remove all children first
                for child in children:
                    settings.scene.active_renderables.Remove(child.key)

            settings.scene.active_renderables.Remove(self.simplified_ad["key"])
            settings.scene.Draw()
            self.Complete()

    def Update(self, events):
        if self.active_transition.complete is True:
            settings.scene.active_renderables.Remove(self.simplified_ad["key"])
            self.Complete()
        else:
            self.active_transition.Update()

    def Skip(self):
        if self.active_transition:
            self.active_transition.Skip()
        self.Complete()


class create_sprite(Action):
    """ Create a sprite renderable using passed in settings. Returns a 'SpriteRenderable' """
    DISPLAY_NAME = "Create Sprite"
    ACTION_DATA = {
        "key": {
            "type": "String",
            "value": "",
            "connection": "",
            "flags": ["editable", "connectable", "preview"],
        },
        "sprite": {
            "type": "Asset_Image",
            "value": "None",
            "connection": "",
            "flags": ["editable", "connectable", "preview"],
        },
        "position": {
            "type": "Vector2",
            "value": [0.5, 0.5],
            "connection": "",
            "flags": ["editable", "connectable", "preview"],
        },
        "center_align": {
            "type": "Bool",
            "value": True,
            "flags": ["editable", "preview"],
        },
        "z_order": {
            "type": "Int",
            "value": 0,
            "connection": "",
            "flags": ["editable", "connectable", "preview"],
        },
        "flip": {
            "type": "Bool",
            "value": False,
            "connection": "",
            "flags": ["editable", "connectable"],
        },
        "transition": {
            "type": "Container",
            "flags": ["editable", "preview"],
            "children": {
                "type": {
                    "type": "Dropdown",
                    "value": "None",

                    "options": ["None", "fade_in"],
                    "flags": ["editable", "preview"],
                },
                "speed": {
                    "type": "Int",
                    "value": 500,
                    "flags": ["editable", "preview"],
                },
            },
        },
        "conditions": {
            "type": "Array",
            "flags": ["editable"],
            "children": {},
            "template": {
                "condition": {
                    "type": "Array_Element",
                    "flags": ["editable"],
                    "children": {
                        "value_name": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        },
                        "operator": {
                            "type": "Dropdown",
                            "value": "equal",
                            "options": ["equal", "not_equal", "less", "greater", "greater-or-equal", "lesser-or-equal"],
                            "flags": ["editable"],
                        },
                        "goal": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        }
                    }
                }
            },
        }
    }

    def Start(self):
        self.ValidateActionData(self.ACTION_DATA, self.simplified_ad)
        new_sprite = SpriteRenderable(renderable_data=self.simplified_ad)

        if "flip" in self.simplified_ad:
            if self.simplified_ad["flip"]:
                new_sprite.Flip()

        self.AddToScene(new_sprite)
        if not self.no_draw:
            # Any transitions are applied to the sprite post-load
            if "None" not in self.simplified_ad["transition"]["type"]:
                from HBEngine.Core import action_manager
                self.active_transition = action_manager.CreateTransition(self.simplified_ad["transition"], new_sprite)
                self.active_transition.Start()
            else:
                settings.scene.Draw()
                self.Complete()
        else:
            self.Complete()

        return new_sprite

    def Update(self, events):
        if self.active_transition.complete:
            self.Complete()
        else:
            self.active_transition.Update()

    def Skip(self):
        if self.active_transition:
            self.active_transition.Skip()
        self.Complete()


class create_background(Action):
    """
    Creates a pre-configured 'SpriteRenderable' suitable as a background image. Returns a
    'SpriteRenderable'
    """
    DISPLAY_NAME = "Create Background"
    ACTION_DATA = {
        "key": {
            "type": "String",
            "value": "Background",
            "connection": "",
            "flags": ["editable", "connectable"]
        },
        "sprite": {
            "type": "Asset_Image",
            "default": ["Default Variables - Sprites", "background_sprite"],
            "connection": "",
            "flags": ["editable", "connectable", "preview"]
        },
        "position": {
            "type": "Vector2",
            "value": [0, 0]
        },
        "center_align": {  # Not editable as controlled by the action
            "type": "Bool",
            "value": False
        },
        "z_order": {
            "type": "Int",
            "default": ["Default Variables - Sprites", "background_z_order"],
            "connection": "",
            "flags": ["editable", "connectable"]
        },
        "flip": {
            "type": "Bool",
            "value": False,
            "flags": ["editable"]
        },
        "conditions": {
            "type": "Array",
            "flags": ["editable"],
            "children": {},
            "template": {
                "condition": {
                    "type": "Array_Element",
                    "flags": ["editable"],
                    "children": {
                        "value_name": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        },
                        "operator": {
                            "type": "Dropdown",
                            "value": "equal",
                            "options": ["equal", "not_equal", "less", "greater", "greater-or-equal", "lesser-or-equal"],
                            "flags": ["editable"],
                        },
                        "goal": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        }
                    }
                }
            },
        }
    }

    def Start(self):
        self.ValidateActionData(self.ACTION_DATA, self.simplified_ad)

        self.skippable = False

        new_sprite = SpriteRenderable(renderable_data=self.simplified_ad)

        self.AddToScene(new_sprite)
        if not self.no_draw:
            settings.scene.Draw()

        self.Complete()
        return new_sprite


class create_interactable(Action):
    """ Creates an interactable renderable, and adds it to the renderable stack. Returns an 'Interactable' """
    DISPLAY_NAME = "Create Interactable"
    ACTION_DATA = {
        "key": {
            "type": "String",
            "value": "",
            "connection": "",
            "flags": ["editable", "connectable", "preview"],
        },
        "position": {
            "type": "Vector2",
            "value": [0.5, 0.5],
            "connection": "",
            "flags": ["editable", "connectable", "preview"],
        },
        "center_align": {
            "type": "Bool",
            "value": True,
            "flags": ["editable"]
        },
        "sprite": {
            "type": "Asset_Image",
            "value": "None",
            "connection": "",
            "flags": ["editable", "connectable", "preview"],
        },
        "sprite_hover": {
            "type": "Asset_Image",
            "value": "None",
            "connection": "",
            "flags": ["editable", "connectable", "preview"],
        },
        "sprite_clicked": {
            "type": "Asset_Image",
            "value": "None",
            "connection": "",
            "flags": ["editable", "connectable", "preview"],
        },
        "z_order": {
            "type": "Int",
            "value": 0,
            "connection": "",
            "flags": ["editable", "connectable"]
        },
        "events": {
            "type": "Array",
            "flags": ["editable", "no_exclusion"],
            "children": {},
            "template": {
                "event": {
                    "type": "Array_Element",
                    "flags": ["editable"],
                    "children": {
                        "action": {
                            "type": "Event",
                            "value": "None",
                            "options": [
                                "None",
                                "load_scene",
                                "quit_game",
                                "scene_fade_out",
                                "scene_fade_in",
                                "play_sfx",
                                "set_mute",
                                "set_value",
                                "start_dialogue",
                                "remove_renderable"
                            ],
                            "flags": ["editable"],
                        }
                    },
                }
            },
        },
        "conditions": {
            "type": "Array",
            "flags": ["editable"],
            "children": {},
            "template": {
                "condition": {
                    "type": "Array_Element",
                    "flags": ["editable"],
                    "children": {
                        "value_name": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        },
                        "operator": {
                            "type": "Dropdown",
                            "value": "equal",
                            "options": ["equal", "not_equal", "less", "greater", "greater-or-equal", "lesser-or-equal"],
                            "flags": ["editable"],
                        },
                        "goal": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        }
                    }
                }
            },
        }
    }

    def Start(self):
        self.ValidateActionData(self.ACTION_DATA, self.simplified_ad)
        self.skippable = False

        new_renderable = Interactable(renderable_data=self.simplified_ad)

        # If the user requested a flip action, do so
        if 'flip' in self.simplified_ad:
            if self.simplified_ad['flip']:
                new_renderable.Flip()

        self.AddToScene(new_renderable)
        if not self.no_draw:
            settings.scene.Draw()

        self.Complete()
        return new_renderable


class create_text(Action):
    """
    Create a TextRenderable at the target location, with the given settings. Returns a 'TextRenderable'
    """
    DISPLAY_NAME = "Create Text"
    ACTION_DATA = {
        "key": {
            "type": "String",
            "value": "",
            "connection": "",
            "flags": ["editable", "connectable", "preview"],
        },
        "position": {
            "type": "Vector2",
            "value": [0.5, 0.5],
            "connection": "",
            "flags": ["editable", "connectable", "preview"],
        },
        "center_align": {
            "type": "Bool",
            "default": ["Default Variables - Text", "text_center_align"],
            "flags": ["editable"],
        },
        "text": {
            "type": "Paragraph",
            "value": "Default",
            "connection": "",
            "flags": ["editable", "connectable", "preview"],
        },
        "text_size": {
            "type": "Int",
            "default": ["Default Variables - Text", "text_size"],
            "connection": "",
            "flags": ["editable", "connectable", "preview"],
        },
        "text_color": {
            "type": "Color",
            "default": ["Default Variables - Text", "text_color"],
            "connection": "",
            "flags": ["editable", "connectable", "preview"],
        },
        "font": {
            "type": "Asset_Font",
            "default": ["Default Variables - Text", "text_font"],
            "connection": "",
            "flags": ["editable", "connectable"],
        },
        "z_order": {
            "type": "Int",
            "default": ["Default Variables - Text", "text_z_order"],
            "connection": "",
            "flags": ["editable", "connectable", "preview"],
        },
        "wrap_bounds": {
            "type": "Vector2",
            "default": ["Default Variables - Text", "text_wrap_bounds"],
            "connection": "",
            "flags": ["editable", "connectable"],
        },
        "transition": {
            "type": "Container",
            "flags": ["preview"],
            "children": {
                "type": {
                    "type": "Dropdown",
                    "value": "None",
                    "options": ["None", "fade_in"],
                    "flags": ["editable", "preview"],
                },
                "speed": {
                    "type": "Int",
                    "value": 500,
                    "flags": ["editable", "preview"],
                },
            },
        },
        "conditions": {
            "type": "Array",
            "flags": ["editable"],
            "children": {},
            "template": {
                "condition": {
                    "type": "Array_Element",
                    "flags": ["editable"],
                    "children": {
                        "value_name": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        },
                        "operator": {
                            "type": "Dropdown",
                            "value": "equal",
                            "options": ["equal", "not_equal", "less", "greater", "greater-or-equal", "lesser-or-equal"],
                            "flags": ["editable"],
                        },
                        "goal": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        }
                    }
                }
            },
        }

    }

    def Start(self):
        self.ValidateActionData(self.ACTION_DATA, self.simplified_ad)

        new_text_renderable = TextRenderable(renderable_data=self.simplified_ad)

        self.AddToScene(new_text_renderable)
        if not self.no_draw:
            if "None" not in self.simplified_ad["transition"]["type"]:
                from HBEngine.Core import action_manager
                self.active_transition = action_manager.CreateTransition(self.simplified_ad["transition"], new_text_renderable)
                self.active_transition.Start()
            else:
                settings.scene.Draw()
                self.Complete()
        else:
            self.Complete()

        return new_text_renderable

    def Update(self, events):
        if self.active_transition.complete is True:
            self.Complete()
        else:
            self.active_transition.Update()

    def Skip(self):
        if self.active_transition:
            self.active_transition.Skip()
        self.Complete()


class create_button(Action):
    """
    Creates a button interactable, and adds it to the renderable stack. Returns a 'Button'
    """
    DISPLAY_NAME = "Create Button"
    ACTION_DATA = {
        "key": {
            "type": "String",
            "value": "",
            "connection": "",
            "flags": ["editable", "connectable", "preview"],
        },
        "position": {
            "type": "Vector2",
            "value": [0.5, 0.5],
            "connection": "",
            "flags": ["editable", "connectable", "preview"],
        },
        "center_align": {
            "type": "Bool",
            "value": True,
            "flags": ["editable"],
        },
        "sprite": {
            "type": "Asset_Image",
            "default": ["Default Variables - Button", "button_sprite"],
            "connection": "",
            "flags": ["editable", "connectable", "preview"],
        },
        "sprite_hover": {
            "type": "Asset_Image",
            "default": ["Default Variables - Button", "button_sprite_hover"],
            "connection": "",
            "flags": ["editable", "connectable"],
        },
        "sprite_clicked": {
            "type": "Asset_Image",
            "default": ["Default Variables - Button", "button_sprite_clicked"],
            "connection": "",
            "flags": ["editable", "connectable"],
        },
        "z_order": {
            "type": "Int",
            "default": ["Default Variables - Button", "button_z_order"],
            "connection": "",
            "flags": ["editable", "connectable"],
        },
        "button_text": {
            "type": "Container",
            "flags": ["editable", "preview"],
            "children": {
                "position": {
                    "type": "Vector2",
                    "value": [0.5, 0.5],
                    "connection": "",
                    "flags": ["editable", "connectable", "preview"],
                },
                "center_align": {
                    "type": "Bool",
                    "value": True,
                    "flags": ["editable"],
                },
                "text": {
                    "type": "String",
                    "value": "Default",
                    "connection": "",
                    "flags": ["editable", "connectable", "preview"],
                },
                "text_size": {
                    "type": "Int",
                    "default": ["Default Variables - Text", "text_size"],
                    "connection": "",
                    "flags": ["editable", "connectable"],
                },
                "text_color": {
                    "type": "Color",
                    "default": ["Default Variables - Text", "text_color"],
                    "connection": "",
                    "flags": ["editable", "connectable"],
                },
                "text_color_hover": {
                    "type": "Color",
                    "default": ["Default Variables - Text", "text_color"],
                    "connection": "",
                    "flags": ["editable", "connectable"]
                },
                "text_color_clicked": {
                    "type": "Color",
                    "default": ["Default Variables - Text", "text_color"],
                    "connection": "",
                    "flags": ["editable", "connectable"]
                },
                "font": {
                    "type": "Asset_Font",
                    "default": ["Default Variables - Text", "text_font"],
                    "connection": "",
                    "flags": ["editable", "connectable"]
                },
                "wrap_bounds": {
                    "type": "Vector2",
                    "value": [0.2, 0.2],
                    "flags": ["editable"],
                },
                "z_order": {  # Not editable as controlled by the Button object
                    "type": "Int",
                    "value": 10002,
                }
            },
        },
        "events": {
            "type": "Array",
            "flags": ["editable", "no_exclusion"],
            "children": {},
            "template": {
                "event": {
                    "type": "Array_Element",
                    "flags": ["editable"],
                    "children": {
                        "action": {
                            "type": "Event",
                            "value": "None",
                            "options": [
                                "None",
                                "load_scene",
                                "quit_game",
                                "scene_fade_out",
                                "scene_fade_in",
                                "play_sfx",
                                "set_mute",
                                "set_value",
                                "start_dialogue",
                                "remove_renderable"
                            ],
                            "flags": ["editable"],
                        }
                    },
                }
            },
        },
        "conditions": {
            "type": "Array",
            "flags": ["editable"],
            "children": {},
            "template": {
                "condition": {
                    "type": "Array_Element",
                    "flags": ["editable"],
                    "children": {
                        "value_name": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        },
                        "operator": {
                            "type": "Dropdown",
                            "value": "equal",
                            "options": ["equal", "not_equal", "less", "greater", "greater-or-equal", "lesser-or-equal"],
                            "flags": ["editable"],
                        },
                        "goal": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        }
                    }
                }
            }
        }
    }

    def Start(self):
        self.ValidateActionData(self.ACTION_DATA, self.simplified_ad)
        self.skippable = False

        # System defined overrides
        self.simplified_ad["button_text"]["z_order"] = self.simplified_ad["z_order"] + 1

        new_renderable = Button(renderable_data=self.simplified_ad)

        self.AddToScene(new_renderable)
        if not self.no_draw:
            settings.scene.Draw()

        self.Complete()
        return new_renderable


class create_text_button(Action):
    """
    Creates a text-only button interactable, and adds it to the renderable stack. Returns a 'Button'
    """
    DISPLAY_NAME = "Create Button (Text Only)"
    ACTION_DATA = {
        "key": {
            "type": "String",
            "value": "",
            "connection": "",
            "flags": ["editable", "connectable", "preview"],
        },
        "position": {
            "type": "Vector2",
            "value": [0.5, 0.5],
            "connection": "",
            "flags": ["editable", "connectable", "preview"],
        },
        "center_align": {
            "type": "Bool",
            "value": True,
            "flags": ["editable"],
        },
        "text": {
            "type": "String",
            "value": "Default",
            "connection": "",
            "flags": ["editable", "connectable", "preview"],
        },
        "text_size": {
            "type": "Int",
            "default": ["Default Variables - Text", "text_size"],
            "connection": "",
            "flags": ["editable", "connectable"],
        },
        "text_color": {
            "type": "Color",
            "default": ["Default Variables - Text", "text_color"],
            "connection": "",
            "flags": ["editable", "connectable"]
        },
        "text_color_hover": {
            "type": "Color",
            "default": ["Default Variables - Text", "text_color_hover"],
            "connection": "",
            "flags": ["editable", "connectable"]
        },
        "text_color_clicked": {
            "type": "Color",
            "default": ["Default Variables - Text", "text_color_clicked"],
            "connection": "",
            "flags": ["editable", "connectable"]
        },
        "font": {
            "type": "Asset_Font",
            "default": ["Default Variables - Text", "text_font"],
            "connection": "",
            "flags": ["editable", "connectable"],
        },
        "z_order": {
            "type": "Int",
            "value": 10002,
            "default": 10002
        },
        "wrap_bounds": {
            "type": "Vector2",
            "value": [0.2, 0.2],
            "flags": ["editable"],
        },
        "events": {
            "type": "Array",
            "flags": ["editable", "no_exclusion"],
            "children": {},
            "template": {
                "event": {
                    "type": "Array_Element",
                    "flags": ["editable"],
                    "children": {
                        "action": {
                            "type": "Event",
                            "value": "None",
                            "options": [
                                "None",
                                "load_scene",
                                "quit_game",
                                "scene_fade_out",
                                "scene_fade_in",
                                "play_sfx",
                                "set_mute",
                                "set_value",
                                "start_dialogue",
                                "remove_renderable"
                            ],
                            "flags": ["editable"],
                        }
                    },
                }
            }
        },
        "conditions": {
            "type": "Array",
            "flags": ["editable"],
            "children": {},
            "template": {
                "condition": {
                    "type": "Array_Element",
                    "flags": ["editable"],
                    "children": {
                        "value_name": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        },
                        "operator": {
                            "type": "Dropdown",
                            "value": "equal",
                            "options": ["equal", "not_equal", "less", "greater", "greater-or-equal", "lesser-or-equal"],
                            "flags": ["editable"],
                        },
                        "goal": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        }
                    }
                }
            },
        }
    }

    def Start(self):
        self.ValidateActionData(self.ACTION_DATA, self.simplified_ad)
        self.skippable = False

        new_renderable = Button(renderable_data=self.simplified_ad)

        self.AddToScene(new_renderable)
        if not self.no_draw:
            settings.scene.Draw()

        self.Complete()
        return new_renderable


class create_checkbox(Action):
    """
    Creates a checkbox button interactable, and adds it to the renderable stack. Returns a 'Checkbox'
    """
    DISPLAY_NAME = "Create Checkbox"
    ACTION_DATA = {
        "key": {
            "type": "String",
            "value": "",
            "connection": "",
            "flags": ["editable", "connectable", "preview"],
        },
        "position": {
            "type": "Vector2",
            "value": [0.5, 0.5],
            "connection": "",
            "flags": ["editable", "connectable", "preview"],
        },
        "center_align": {
            "type": "Bool",
            "value": True,
            "flags": ["editable"],
        },
        "sprite": {
            "type": "Asset_Image",
            "default": ["Default Variables - Button", "checkbox_sprite"],
            "connection": "",
            "flags": ["editable", "connectable", "preview"],
        },
        "sprite_hover": {
            "type": "Asset_Image",
            "default": ["Default Variables - Button", "checkbox_sprite_hover"],
            "connection": "",
            "flags": ["editable", "connectable", "preview"],
        },
        "sprite_clicked": {
            "type": "Asset_Image",
            "default": ["Default Variables - Button", "checkbox_sprite_clicked"],
            "connection": "",
            "flags": ["editable", "connectable", "preview"],
        },
        "sprite_icon": {
            "type": "Asset_Image",
            "default": ["Default Variables - Button", "checkbox_sprite_icon"],
            "connection": "",
            "flags": ["editable", "connectable", "preview"],
        },
        "z_order": {
            "type": "Int",
            "default": ["Default Variables - Button", "button_z_order"],
            "connection": "",
            "flags": ["editable", "connectable"],
        },
        "events": {
            "type": "Array",
            "flags": ["editable", "no_exclusion"],
            "children": {},
            "template": {
                "event": {
                    "type": "Array_Element",
                    "flags": ["editable"],
                    "children": {
                        "action": {
                            "type": "Event",
                            "value": "None",
                            "default": "None",
                            "options": [
                                "None",
                                "play_sfx",
                                "set_mute",
                                "set_value"
                            ],
                            "flags": ["editable"],
                        }
                    },
                }
            },
        },
        "conditions": {
            "type": "Array",
            "flags": ["editable"],
            "children": {},
            "template": {
                "condition": {
                    "type": "Array_Element",
                    "flags": ["editable"],
                    "children": {
                        "value_name": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        },
                        "operator": {
                            "type": "Dropdown",
                            "value": "equal",
                            "options": ["equal", "not_equal", "less", "greater", "greater-or-equal", "lesser-or-equal"],
                            "flags": ["editable"],
                        },
                        "goal": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        }
                    }
                }
            },
        }
    }

    def Start(self):
        self.ValidateActionData(self.ACTION_DATA, self.simplified_ad)
        self.skippable = False

        new_renderable = Checkbox(renderable_data=self.simplified_ad)

        self.AddToScene(new_renderable)
        if not self.no_draw:
            settings.scene.Draw()

        self.Complete()
        return new_renderable


# -------------- DIALOGUE ACTIONS --------------


class start_dialogue(Action):
    DISPLAY_NAME = "Start Dialogue"
    ACTION_DATA = {
        "dialogue_file": {
            "type": "Dialogue",
            "value": "",
            "flags": ["editable", "preview"]
        },
        "conditions": {
            "type": "Array",
            "flags": ["editable"],
            "children": {},
            "template": {
                "condition": {
                    "type": "Array_Element",
                    "flags": ["editable"],
                    "children": {
                        "value_name": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        },
                        "operator": {
                            "type": "Dropdown",
                            "value": "equal",
                            "options": ["equal", "not_equal", "less", "greater", "greater-or-equal", "lesser-or-equal"],
                            "flags": ["editable"],
                        },
                        "goal": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        }
                    }
                }
            },
        }
    }

    def Start(self):
        self.ValidateActionData(self.ACTION_DATA, self.simplified_ad)
        from HBEngine import hb_engine
        hb_engine.LoadModule(m_dialogue.Dialogue, self.simplified_ad['dialogue_file'])
        self.Complete()
        return None


class dialogue(Action):
    """
    Create dialogue and speaker text renderables, and add them to the renderable stack using pre-configured settings.
    If the user specifies a 'character' block, create a speaker text using the character details instead. Returns None
    """
    DISPLAY_NAME = "Dialogue"
    ACTION_DATA = {
        "speaker": {
            "type": "Container",
            "flags": ["editable", "preview"],
            "children": {
                "key": {  # Not editable as controlled by action
                    "type": "String",
                    "value": "SpeakerText",
                    "default": "SpeakerText",
                },
                "position": {
                    "type": "Vector2",
                    "default": ["Default Variables - Dialogue", "speaker_text_position"],
                    "connection": "",
                    "flags": ["editable", "connectable"]
                },
                "center_align": {
                    "type": "Bool",
                    "default": ["Default Variables - Dialogue", "speaker_text_center_align"],
                    "flags": ["editable"],
                },
                "text": {
                    "type": "String",
                    "value": "",
                    "connection": "",
                    "flags": ["editable", "connectable", "preview"],
                },
                "text_size": {
                    "type": "Int",
                    "default": ["Default Variables - Dialogue", "speaker_text_size"],
                    "connection": "",
                    "flags": ["editable", "connectable"],
                },
                "text_color": {
                    "type": "Color",
                    "default": ["Default Variables - Dialogue", "speaker_text_color"],
                    "connection": "",
                    "flags": ["editable", "connectable"],
                },
                "font": {
                    "type": "Asset_Font",
                    "default": ["Default Variables - Dialogue", "speaker_text_font"],
                    "connection": "",
                    "flags": ["editable", "connectable"],
                },
                "z_order": {
                    "type": "Int",
                    "default": ["Default Variables - Dialogue", "speaker_text_z_order"],
                    "connection": "",
                    "flags": ["connectable"],
                },
                "transition": {
                    "type": "Container",
                    "flags": ["editable"],
                    "children": {
                        "type": {
                            "type": "Dropdown",
                            "default": ["Default Variables - Dialogue", "transition_type"],
                            "options": ["fade_in", "None"],
                            "flags": ["editable"]
                        },
                        "speed": {
                            "type": "Int",
                            "default": ["Default Variables - Dialogue", "transition_speed"],
                            "flags": ["editable"]
                        },
                    },
                },
                "wrap_bounds": {
                    "type": "Vector2",
                    "default": ["Default Variables - Dialogue", "speaker_text_wrap_bounds"],
                    "flags": ["editable"],
                }
            },
        },
        "dialogue": {
            "type": "Container",
            "flags": ["editable", "preview"],
            "children": {
                "key": {
                    "type": "String",
                    "value": "",
                },
                "position": {
                    "type": "Vector2",
                    "default": ["Default Variables - Dialogue", "dialogue_text_position"],
                    "connection": "",
                    "flags": ["editable", "connectable"],
                },
                "center_align": {
                    "type": "Bool",
                    "default": ["Default Variables - Dialogue", "dialogue_text_center_align"],
                    "flags": ["editable"],
                },
                "text": {
                    "type": "Paragraph",
                    "value": "",
                    "flags": ["editable", "preview"],
                },
                "text_size": {
                    "type": "Int",
                    "default": ["Default Variables - Dialogue", "dialogue_text_size"],
                    "connection": "",
                    "flags": ["editable", "connectable"],
                },
                "text_color": {
                    "type": "Color",
                    "default": ["Default Variables - Dialogue", "dialogue_text_color"],
                    "connection": "",
                    "flags": ["editable", "connectable"],
                },
                "font": {
                    "type": "Asset_Font",
                    "default": ["Default Variables - Dialogue", "dialogue_text_font"],
                    "connection": "",
                    "flags": ["editable", "connectable"],
                },
                "z_order": {
                    "type": "Int",
                    "default": ["Default Variables - Dialogue", "dialogue_text_z_order"],
                },
                "transition": {
                    "type": "Container",
                    "flags": ["editable"],
                    "children": {
                        "type": {
                            "type": "Dropdown",
                            "default": ["Default Variables - Dialogue", "transition_type"],
                            "options": ["fade_in", "None"],
                            "flags": ["editable"],
                        },
                        "speed": {
                            "type": "Int",
                            "default": ["Default Variables - Dialogue", "transition_speed"],
                            "flags": ["editable"],
                        },
                    },
                },
                "wrap_bounds": {
                    "type": "Vector2",
                    "default": ["Default Variables - Dialogue", "dialogue_text_wrap_bounds"],
                }
            },
        },
        "conditions": {
            "type": "Array",
            "flags": ["editable"],
            "children": {},
            "template": {
                "condition": {
                    "type": "Array_Element",
                    "flags": ["editable"],
                    "children": {
                        "value_name": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        },
                        "operator": {
                            "type": "Dropdown",
                            "value": "equal",
                            "options": ["equal", "not_equal", "less", "greater", "greater-or-equal", "lesser-or-equal"],
                            "flags": ["editable"],
                        },
                        "goal": {
                            "type": "String",
                            "value": "",
                            "default": "",
                            "flags": ["editable"],
                        }
                    }
                }
            },
        }
    }

    def Start(self):
        self.ValidateActionData(self.ACTION_DATA, self.simplified_ad)

        new_speaker_text = TextRenderable(self.simplified_ad["speaker"])
        new_dialogue_text = TextRenderable(self.simplified_ad["dialogue"])

        self.AddToScene(new_speaker_text)
        self.AddToScene(new_dialogue_text)

        # Note: Speaker text does not support transitions currently
        if self.simplified_ad["dialogue"]["transition"]["type"] != "None":
            from HBEngine.Core import action_manager
            self.active_transition = action_manager.CreateTransition(self.simplified_ad["dialogue"]["transition"], new_dialogue_text)
            self.active_transition.Start()
        else:
            settings.scene.Draw()
            self.Complete()

        return None

    def Update(self, events):
        if self.active_transition.complete is True:
            print("Transition Complete")
            self.Complete()
        else:
            self.active_transition.Update()

    def Skip(self):
        if self.active_transition:
            self.active_transition.Skip()
        self.Complete()


class choice(Action):
    DISPLAY_NAME = "Choice"
    ACTION_DATA = {
        "choices": {
            "type": "Array",
            "flags": ["editable", "preview"],
            "children": {},
            "template": {
                "choice": {
                    "type": "Array_Element",
                    "flags": ["editable", "preview"],
                    "children": {
                        "branch": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable", "preview"],
                        },
                        "position": {
                            "type": "Vector2",
                            "value": [0.5, 0.5],
                            "flags": ["editable"],
                        },
                        "center_align": {
                            "type": "Bool",
                            "value": True,
                        },
                        "sprite": {
                            "type": "Asset_Image",
                            "default": ["Default Variables - Dialogue", "choice_button_sprite"],
                            "connection": "",
                            "flags": ["editable", "connectable"],
                        },
                        "sprite_hover": {
                            "type": "Asset_Image",
                            "default": ["Default Variables - Dialogue", "choice_button_sprite_hover"],
                            "connection": "",
                            "flags": ["editable", "connectable"],
                        },
                        "sprite_clicked": {
                            "type": "Asset_Image",
                            "default": ["Default Variables - Dialogue", "choice_button_sprite_clicked"],
                            "connection": "",
                            "flags": ["editable", "connectable"],
                        },
                        "z_order": {
                            "type": "Int",
                            "default": ["Default Variables - Dialogue", "choice_button_text_size"],
                            "connection": "",
                            "flags": ["global_active"],
                        },
                        "button_text": {
                            "type": "Container",
                            "flags": ["editable", "preview"],
                            "children": {
                                "position": {
                                    "type": "Vector2",
                                    "value": [0.5, 0.5],
                                    "flags": ["editable"],
                                },
                                "center_align": {
                                    "type": "Bool",
                                    "value": True,
                                    "flags": ["editable"],
                                },
                                "text": {
                                    "type": "String",
                                    "value": "Default",
                                    "flags": ["editable", "preview"],
                                },
                                "text_size": {
                                    "type": "Int",
                                    "default": ["Default Variables - Dialogue", "choice_button_text_size"],
                                    "connection": "",
                                    "flags": ["editable", "connectable"],
                                },
                                "text_color": {
                                    "type": "Color",
                                    "default": ["Default Variables - Dialogue", "choice_button_text_color"],
                                    "connection": "",
                                    "flags": ["editable", "connectable"],
                                },
                                "text_color_hover": {
                                    "type": "Color",
                                    "default": ["Default Variables - Dialogue", "choice_button_text_color_hover"],
                                    "connection": "",
                                    "flags": ["editable", "connectable"],
                                },
                                "text_color_clicked": {
                                    "type": "Color",
                                    "default": ["Default Variables - Dialogue", "choice_button_text_color_clicked"],
                                    "connection": "",
                                    "flags": ["editable", "connectable"],
                                },
                                "font": {
                                    "type": "Asset_Font",
                                    "default": ["Default Variables - Dialogue", "choice_button_font"],
                                    "connection": "",
                                    "flags": ["editable", "connectable"],
                                },
                                "z_order": {
                                    "type": "Int",
                                    "value": 10002,
                                },
                                "wrap_bounds": {
                                    "type": "Vector2",
                                    "value": [0.25, 0.25],
                                    "flags": ["editable"],
                                }
                            }
                        }
                    }
                }
            }
        },
        "conditions": {
            "type": "Array",
            "flags": ["editable"],
            "children": {},
            "template": {
                "condition": {
                    "type": "Array_Element",
                    "flags": ["editable"],
                    "children": {
                        "value_name": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        },
                        "operator": {
                            "type": "Dropdown",
                            "value": "equal",
                            "options": ["equal", "not_equal", "less", "greater", "greater-or-equal", "lesser-or-equal"],
                            "flags": ["editable"],
                        },
                        "goal": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        }
                    }
                }
            },
        }
    }

    def Start(self):
        self.ValidateActionData(self.ACTION_DATA, self.simplified_ad)
        self.skippable = False

        # Create an object that acts as a parent for all the choice buttons. When this is deleted, the buttons
        # will be deleted with it
        self.simplified_ad["position"] = (0, 0)
        self.simplified_ad["z_order"] = 0
        self.simplified_ad["center_align"] = False
        self.simplified_ad["key"] = "Choice"
        new_renderable = Choice(renderable_data=self.simplified_ad)

        # Generate a button for each choice, adding them to the active renderables group for access to updates
        # and rendering. Then, add them as a child to the choice object so they're destroyed as a collective
        #
        # Because we the data comes from the 'template' key, we don't have a mechanism to load from the action
        for choice_name, choice_data in self.simplified_ad["choices"].items():
            # Define what the button does when clicked
            choice_data["event"] = {
                "action": "switch_branch",
                "branch": choice_data["branch"]
            }

            # The key is generated dynamically instead of being provided by the file
            choice_data["key"] = choice_name

            new_child = Button(choice_data)
            settings.scene.active_renderables.Add(new_child)
            new_renderable.children.append(new_child)

        # Add the choice parent object to the render stack
        settings.scene.active_renderables.Add(new_renderable)

        settings.scene.Draw()
        self.Complete()

        return new_renderable


class switch_branch(Action):
    DISPLAY_NAME = "Switch Branch"
    ACTION_DATA = {
        "branch": {
            "type": "String",
            "value": "",
            "flags": ["editable", "preview"],
        },
        "conditions": {
            "type": "Array",
            "flags": ["editable"],
            "children": {},
            "template": {
                "condition": {
                    "type": "Array_Element",
                    "flags": ["editable"],
                    "children": {
                        "value_name": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        },
                        "operator": {
                            "type": "Dropdown",
                            "value": "equal",
                            "options": ["equal", "not_equal", "less", "greater", "greater-or-equal", "lesser-or-equal"],
                            "flags": ["editable"],
                        },
                        "goal": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        }
                    }
                }
            },
        }
    }

    def Start(self):
        self.ValidateActionData(self.ACTION_DATA, self.simplified_ad)

        # If a choice button lead to this, delete that whole choice container, otherwise it would persist
        # into the new branch
        if settings.scene.active_renderables.Exists("Choice"):
            from HBEngine.Core import action_manager
            action_manager.PerformAction(
                {"key": "Choice", "transition": {"type": "None"}},
                "remove_renderable"
            )

        # Request that the Dialogue module load the given branch
        settings.modules[m_dialogue.Dialogue.MODULE_NAME].SwitchDialogueBranch(self.simplified_ad['branch'])

        settings.scene.Draw()
        self.Complete()

        return None


# -------------- SOUND ACTIONS --------------


class play_sfx(SoundAction):
    DISPLAY_NAME = "Play SFX"
    ACTION_DATA = {
        "key": {
            "type": "String",
            "value": "SFX",
            "flags": ["editable", "preview"],
        },
        "sound": {
            "type": "Asset_Sound",
            "value": "",
            "flags": ["editable", "preview"],
        },
        "volume": {
            "type": "Float",
            "value": 1.0,
            "flags": ["editable", "preview"],
        },
        "loop": {
            "type": "Bool",
            "value": False,
            "flags": ["editable", "preview"],
        },
        "conditions": {
            "type": "Array",
            "flags": ["editable"],
            "children": {},
            "template": {
                "condition": {
                    "type": "Array_Element",
                    "flags": ["editable"],
                    "children": {
                        "value_name": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        },
                        "operator": {
                            "type": "Dropdown",
                            "value": "equal",
                            "options": ["equal", "not_equal", "less", "greater", "greater-or-equal", "lesser-or-equal"],
                            "flags": ["editable"],
                        },
                        "goal": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        }
                    }
                }
            },
        }
    }

    def Start(self):
        self.ValidateActionData(self.ACTION_DATA, self.simplified_ad)

        new_sound = Sound(self.simplified_ad)

        # Start the playback (internally stores the channel object)
        new_sound.Play()
        settings.scene.active_sounds[self.simplified_ad["key"]] = new_sound

        return new_sound

    def Update(self, events):
        if not settings.scene.active_sounds[self.simplified_ad["key"]].GetBusy():
            settings.scene.active_sounds[self.simplified_ad["key"]].Stop()
            settings.scene.active_sounds.pop(self.simplified_ad["key"])  # Remove from the scene sfx list
            self.Complete()  # Remove from the action manager

    def Skip(self):
        settings.scene.active_sounds.pop(self.simplified_ad["key"])
        self.Complete()


class stop_sfx(Action):
    """
    Based on a given key, stop and remove the associated sfx from the sound stack
    """
    DISPLAY_NAME = "Stop SFX"
    ACTION_DATA = {
        "key": {
            "type": "String",
            "value": "SFX",
            "flags": ["editable", "preview"],
        },
        "conditions": {
            "type": "Array",
            "flags": ["editable"],
            "children": {},
            "template": {
                "condition": {
                    "type": "Array_Element",
                    "flags": ["editable"],
                    "children": {
                        "value_name": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        },
                        "operator": {
                            "type": "Dropdown",
                            "value": "equal",
                            "options": ["equal", "not_equal", "less", "greater", "greater-or-equal", "lesser-or-equal"],
                            "flags": ["editable"],
                        },
                        "goal": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        }
                    }
                }
            }
        }
    }

    def Start(self):
        self.ValidateActionData(self.ACTION_DATA, self.simplified_ad)
        self.skippable = False

        if "key" in self.simplified_ad:
            settings.scene.active_sounds[self.simplified_ad["key"]].stop()  # Stop the sound
            del settings.scene.active_sounds[self.simplified_ad["key"]]  # Delete the sound
            settings.scene.active_sounds.pop(self.simplified_ad["key"])  # Remove key

            self.Complete()
        else:
            raise ValueError("'stop_sfx' action Failed - Key not specified")


class play_music(SoundAction):
    #@TODO: Implement end-event so this action completes when the song reaches last frame
    DISPLAY_NAME = "Play Music"
    ACTION_DATA = {
        "music": {
            "type": "Asset_Sound",
            "value": "",
            "flags": ["editable", "preview"],
        },
        "volume": {
            "type": "Float",
            "value": 1.0,
            "flags": ["editable", "preview"],
        },
        "loop": {
            "type": "Bool",
            "value": False,
            "flags": ["editable", "preview"],
        },
        "conditions": {
            "type": "Array",
            "flags": ["editable"],
            "children": {},
            "template": {
                "condition": {
                    "type": "Array_Element",
                    "flags": ["editable"],
                    "children": {
                        "value_name": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        },
                        "operator": {
                            "type": "Dropdown",
                            "value": "equal",
                            "options": ["equal", "not_equal", "less", "greater", "greater-or-equal", "lesser-or-equal"],
                            "flags": ["editable"],
                        },
                        "goal": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        }
                    }
                }
            }
        }
    }

    def Start(self):
        self.ValidateActionData(self.ACTION_DATA, self.simplified_ad)
        self.skippable = False

        new_music = Music(self.simplified_ad)

        #new_music.end_event = #@TODO: This needs to delete the action upon completion or the action will exist forever
        # If the user hasn't removed the previous music, forcefully remove it here without any transition
        if settings.scene.active_music:
            settings.scene.active_music.Stop()  # This will invoke the end-event on the existing music action #@TODO: Review if this comment is accurate
            del settings.scene.active_music  # Delete the music

        new_music.Play()
        settings.scene.active_music = new_music

        self.Complete()

    def Update(self, events):
        if not settings.scene.active_music.GetBusy(): #@TODO: Review whether this triggers when audio is paused
            print("Music completed")
            self.Complete()


class stop_music(Action):
    """
    Stops the currently active music
    """
    DISPLAY_NAME = "Stop Music"
    ACTION_DATA = {
        "key": {
            "type": "String",
            "value": "",
            "flags": ["editable", "preview"],
        },
        "conditions": {
            "type": "Array",
            "flags": ["editable"],
            "children": {},
            "template": {
                "condition": {
                    "type": "Array_Element",
                    "flags": ["editable"],
                    "children": {
                        "value_name": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        },
                        "operator": {
                            "type": "Dropdown",
                            "value": "equal",
                            "options": ["equal", "not_equal", "less", "greater", "greater-or-equal", "lesser-or-equal"],
                            "flags": ["editable"],
                        },
                        "goal": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        }
                    }
                }
            }
        }
    }

    def Start(self):
        self.ValidateActionData(self.ACTION_DATA, self.simplified_ad)
        self.skippable = False

        settings.scene.active_music.Stop() #@TODO: Update
        settings.scene.active_music.complete = True
        settings.scene.active_music = None  # DEBUG: Remove once the end-event is implemented
        self.Complete()
        return None


class set_mute(Action):
    DISPLAY_NAME = "Set Mute"
    ACTION_DATA = {
        "toggle": {
            "type": "Bool",
            "value": True,
            "flags": ["editable"],
        },
        "value": {
            "type": "Bool",
            "value": True,
            "flags": ["editable"],
        },
        "conditions": {
            "type": "Array",
            "flags": ["editable"],
            "children": {},
            "template": {
                "condition": {
                    "type": "Array_Element",
                    "flags": ["editable"],
                    "children": {
                        "value_name": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        },
                        "operator": {
                            "type": "Dropdown",
                            "value": "equal",
                            "options": ["equal", "not_equal", "less", "greater", "greater-or-equal", "lesser-or-equal"],
                            "flags": ["editable"],
                        },
                        "goal": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        }
                    }
                }
            }
        }
    }

    def Start(self):
        self.ValidateActionData(self.ACTION_DATA, self.simplified_ad)
        self.skippable = False

        # Update the project setting
        if self.simplified_ad["toggle"]:
            settings.SetProjectSetting("Audio", "mute", not settings.GetProjectSetting("Audio", "mute"))
        else:
            settings.SetProjectSetting("Audio", "mute", self.simplified_ad["value"])

        # Update all active audio objects
        if settings.GetProjectSetting("Audio", "mute"):
            for sfx in settings.scene.active_sounds.values():
                sfx.Mute()
            if settings.scene.active_music: settings.scene.active_music.Mute()
        else:
            for sfx in settings.scene.active_sounds.values():
                sfx.Unmute()
            if settings.scene.active_music: settings.scene.active_music.Unmute()

        self.Complete()

        return None


# -------------- VALUE ACTIONS --------------


class set_value(Action):
    DISPLAY_NAME = "Set Value"
    ACTION_DATA = {
        "name": {
            "type": "String",
            "value": "",
            "flags": ["editable", "preview"],
        },
        "value": {
            "type": "String",
            "value": "",
            "flags": ["editable", "preview"],
        },
        "conditions": {
            "type": "Array",
            "flags": ["editable"],
            "children": {},
            "template": {
                "condition": {
                    "type": "Array_Element",
                    "flags": ["editable"],
                    "children": {
                        "value_name": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        },
                        "operator": {
                            "type": "Dropdown",
                            "value": "equal",
                            "options": ["equal", "not_equal", "less", "greater", "greater-or-equal", "lesser-or-equal"],
                            "flags": ["editable"],
                        },
                        "goal": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        }
                    }
                }
            }
        }
    }

    def Start(self):
        self.ValidateActionData(self.ACTION_DATA, self.simplified_ad)
        self.skippable = False

        # Set the project value
        settings.SetValue(self.simplified_ad['name'], self.simplified_ad['value'])

        self.Complete()
        return None


# -------------- UTILITY ACTIONS --------------


class load_scene(Action):
    """ Switches scenes to the one specified in the action data """
    DISPLAY_NAME = "Load Scene"
    ACTION_DATA = {
        "scene_file": {
            "type": "Scene",
            "value": "",
            "flags": ["editable", "preview"],
        },
        "conditions": {
            "type": "Array",
            "flags": ["editable"],
            "children": {},
            "template": {
                "condition": {
                    "type": "Array_Element",
                    "flags": ["editable"],
                    "children": {
                        "value_name": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        },
                        "operator": {
                            "type": "Dropdown",
                            "value": "equal",
                            "options": ["equal", "not_equal", "less", "greater", "greater-or-equal", "lesser-or-equal"],
                            "flags": ["editable"],
                        },
                        "goal": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        }
                    }
                }
            }
        }
    }

    def Start(self):
        self.skippable = False

        settings.scene.SwitchScene(self.simplified_ad["scene_file"])
        self.Complete()


class wait(Action):
    """ Waits for a set amount of time before completing """
    DISPLAY_NAME = "Wait"
    ACTION_DATA = {
        "seconds": {
            "type": "Int",
            "value": 300,
            "flags": ["editable", "preview"],
        },
        "conditions": {
            "type": "Array",
            "flags": ["editable"],
            "children": {},
            "template": {
                "condition": {
                    "type": "Array_Element",
                    "flags": ["editable"],
                    "children": {
                        "value_name": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        },
                        "operator": {
                            "type": "Dropdown",
                            "value": "equal",
                            "options": ["equal", "not_equal", "less", "greater", "greater-or-equal", "lesser-or-equal"],
                            "flags": ["editable"],
                        },
                        "goal": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        }
                    }
                }
            }
        }
    }

    def Start(self):
        self.ValidateActionData(self.ACTION_DATA, self.simplified_ad)
        self.counter = 0
        self.target = self.simplified_ad["seconds"]

        return None

    def Update(self, events):
        self.counter += 1 * settings.scene.delta_time
        print(self.counter)

        if self.counter >= self.target:
            print("Times up!")
            self.Complete()

    def Skip(self):
        self.Complete()


class quit_game(Action):
    """
    Immediately closes the game
    This is not meant to be called during scenes, but is available as an action for inputs, buttons, etc
    """
    DISPLAY_NAME = "Quit Game"
    ACTION_DATA = {}

    def Start(self):
        self.ValidateActionData(self.ACTION_DATA, self.simplified_ad)
        self.skippable = False
        pygame.quit()
        exit()


# -------------- TRANSITION ACTIONS --------------
""" 
These actions function as transitions in their own right, but are not modifiers on existing actions like
those listed in the 'transitions' file
"""


class scene_fade_in(Action):
    """
    Creates a texture of the selected color covering the entire screen, then slowly fades it out

    Returns 'SpriteRenderable'
    """
    DISPLAY_NAME = "Scene Fade In"
    ACTION_DATA = {
        "color": {
            "type": "Dropdown",
            "value": "black",
            "options": ["black", "white"],
            "flags": ["editable", "preview"],
        },
        "speed": {
            "type": "Int",
            "value": 300,
            "flags": ["editable", "preview"],
        },
        "conditions": {
            "type": "Array",
            "flags": ["editable"],
            "children": {},
            "template": {
                "condition": {
                    "type": "Array_Element",
                    "flags": ["editable"],
                    "children": {
                        "value_name": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        },
                        "operator": {
                            "type": "Dropdown",
                            "value": "equal",
                            "options": ["equal", "not_equal", "less", "greater", "greater-or-equal", "lesser-or-equal"],
                            "flags": ["editable"],
                        },
                        "goal": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        }
                    }
                }
            }
        }
    }

    def Start(self):
        self.ValidateActionData(self.ACTION_DATA, self.simplified_ad)

        self.simplified_ad['key'] = 'Transition_SceneFade'
        self.simplified_ad['z_order'] = 9999999999999999999
        self.simplified_ad['center_align'] = False

        if self.simplified_ad["color"] == "black":
            self.simplified_ad['sprite'] = "HBEngine/Content/Sprites/TransitionEffects/transition_fade_black.png"
        elif self.simplified_ad["color"] == "white":
            self.simplified_ad['sprite'] = "HBEngine/Content/Sprites/TransitionEffects/transition_fade_white.png"
        else:
            raise ValueError(f"'scene_fade_in' action Failed - Invalid color value provided: {self.simplified_ad['color']}")

        if 'speed' in self.simplified_ad:
            self.speed = self.simplified_ad['speed']

        new_sprite = SpriteRenderable(renderable_data=self.simplified_ad)

        self.AddToScene(new_sprite)
        settings.scene.Draw()

        self.renderable = new_sprite
        self.progress = self.renderable.GetSurface().get_alpha()
        self.goal = 0

        return new_sprite

    def Update(self, events):
        self.progress -= (self.speed * settings.scene.delta_time)
        self.renderable.GetSurface().set_alpha(self.progress)

        settings.scene.Draw()

        if self.progress <= self.goal:
            self.Complete()

    def Skip(self):
        self.renderable.GetSurface().set_alpha(self.goal)
        settings.scene.Draw()
        self.Complete()


class scene_fade_out(Action):
    """
    Creates a texture of the selected color covering the entire screen, then slowly fades it in

    Returns 'SpriteRenderable'
    """
    DISPLAY_NAME = "Scene Fade Out"
    ACTION_DATA = {
        "color": {
            "type": "Dropdown",
            "value": "black",
            "options": ["black", "white"],
            "flags": ["editable", "preview"],
        },
        "speed": {
            "type": "Int",
            "value": 300,
            "flags": ["editable", "preview"],
        },
        "conditions": {
            "type": "Array",
            "flags": ["editable"],
            "children": {},
            "template": {
                "condition": {
                    "type": "Array_Element",
                    "flags": ["editable"],
                    "children": {
                        "value_name": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        },
                        "operator": {
                            "type": "Dropdown",
                            "value": "equal",
                            "options": ["equal", "not_equal", "less", "greater", "greater-or-equal", "lesser-or-equal"],
                            "flags": ["editable"],
                        },
                        "goal": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        }
                    }
                }
            }
        }
    }

    def Start(self):
        self.ValidateActionData(self.ACTION_DATA, self.simplified_ad)

        self.simplified_ad['key'] = 'Transition_SceneFade'
        self.simplified_ad['z_order'] = 9999999999999999999
        self.simplified_ad['center_align'] = False

        if self.simplified_ad["color"] == "black":
            self.simplified_ad['sprite'] = "HBEngine/Content/Sprites/TransitionEffects/transition_fade_black.png"
        elif self.simplified_ad["color"] == "white":
            self.simplified_ad['sprite'] = "HBEngine/Content/Sprites/TransitionEffects/transition_fade_white.png"
        else:
            raise ValueError(f"'scene_fade_out' action Failed - Invalid color value provided: {self.simplified_ad['color']}")

        if 'speed' in self.simplified_ad:
            self.speed = self.simplified_ad['speed']

        new_sprite = SpriteRenderable(renderable_data=self.simplified_ad)
        new_sprite.GetSurface().set_alpha(0)

        self.AddToScene(new_sprite)
        settings.scene.Draw()

        self.renderable = new_sprite
        self.progress = 0
        self.goal = 256

        return new_sprite

    def Update(self, events):
        self.progress += (self.speed * settings.scene.delta_time)
        self.renderable.GetSurface().set_alpha(self.progress)

        settings.scene.Draw()

        if self.progress >= self.goal:
            self.Complete()

    def Skip(self):
        self.renderable.GetSurface().set_alpha(self.goal)
        settings.scene.Draw()
        self.Complete()


# -------------- INTERFACE ACTIONS --------------

class load_interface(Action):
    """ Loads the provided interface. Returns 'Interface' """
    DISPLAY_NAME = "Load Interface"
    ACTION_DATA = {
        "interface_file": {
            "type": "Interface",
            "value": "None",
            "flags": ["editable", "preview"],
        }
    }

    def Start(self):
        new_interface = settings.scene.LoadInterface(
            interface_file=self.simplified_ad["interface_file"],
            parent=self.parent
        )
        settings.scene.Draw()
        self.Complete()
        return new_interface


class unload_interface(Action):
    """ Unloads the provided interface. Returns None """
    DISPLAY_NAME = "Unload Interface"
    ACTION_DATA = {
        "key": {
            "type": "String",
            "value": "",
            "flags": ["editable", "preview"]
        }
    }

    def Start(self):
        new_interface = settings.scene.UnloadInterface(
            key_to_remove=self.simplified_ad["key"],
            parent=self.parent
        )
        settings.scene.Draw()
        self.Complete()
        return new_interface


class pause(Action):
    """ Requests that the active scene pause the game and show the pause interface. Returns 'None' """
    DISPLAY_NAME = "Pause"
    ACTION_DATA = {}

    def Start(self):
        from HBEngine import hb_engine
        hb_engine.Pause()
        self.Complete()
        return None


class unpause(Action):
    """ Requests that the active scene unpause the game and remove the pause interface. Returns 'None' """
    DISPLAY_NAME = "Unpause"
    ACTION_DATA = {}

    def Start(self):
        from HBEngine import hb_engine
        hb_engine.Unpause()
        self.Complete()
        return None


class switch_page(Action):
    """ Requests a page load for the target interface. Returns 'None' """
    DISPLAY_NAME = "Switch Page"
    ACTION_DATA = {
        "owner": {
            "type": "String",
            "value": "",
            "flags": ["editable"],
        },
        "page": {
            "type": "String",
            "value": "",
            "default": "",
            "flags": ["editable"],
        },
        "conditions": {
            "type": "Array",
            "flags": ["editable"],
            "children": {},
            "template": {
                "condition": {
                    "type": "Array_Element",
                    "flags": ["editable"],
                    "children": {
                        "value_name": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        },
                        "operator": {
                            "type": "Dropdown",
                            "value": "equal",
                            "options": ["equal", "not_equal", "less", "greater", "greater-or-equal", "lesser-or-equal"],
                            "flags": ["editable"],
                        },
                        "goal": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        }
                    }
                }
            }
        }
    }

    def Start(self):
        if self.simplified_ad["owner"] in settings.scene.active_interfaces:
            settings.scene.active_interfaces[self.simplified_ad["owner"]].LoadPage(self.simplified_ad["page"])

        settings.scene.Draw()
        self.Complete()
        return None


class remove_page(Action):
    """ Removes the target interface and all of its children. Returns 'None' """
    DISPLAY_NAME = "Remove Page"
    ACTION_DATA = {
        "owner": {
            "type": "String",
            "value": "",
            "flags": ["editable"],
        },
        "conditions": {
            "type": "Array",
            "flags": ["editable"],
            "children": {},
            "template": {
                "condition": {
                    "type": "Array_Element",
                    "flags": ["editable"],
                    "children": {
                        "value_name": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        },
                        "operator": {
                            "type": "Dropdown",
                            "value": "equal",
                            "options": ["equal", "not_equal", "less", "greater", "greater-or-equal", "lesser-or-equal"],
                            "flags": ["editable"],
                        },
                        "goal": {
                            "type": "String",
                            "value": "",
                            "flags": ["editable"],
                        }
                    }
                }
            }
        }
    }

    def Start(self):
        if self.simplified_ad["owner"] in settings.scene.active_interfaces:
            settings.scene.active_interfaces[self.simplified_ad["owner"]].RemovePage(self.simplified_ad["page"])

        settings.scene.Draw()
        self.Complete()
        return None
