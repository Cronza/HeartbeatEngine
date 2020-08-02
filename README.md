# GVNEngine
**Version: 0.1**

# What is the 'GVNEngine'?
![ScreenShot](Progress_Examples/GVNEngine_v01_Dialogue_Scene.png?raw=true "GVNEngine Dialogue Scene")
*I do not own the background in the above photo, and am merely using it as a placeholder. The rightful owner is the talented:*<br/>
*https://www.deviantart.com/aikosanartist*

The GVNEngine is a visual novel / dating simulator game engine created in Python, using the PyGame framework. It is meant as a lightweight, user-friendly engine that offers a content-driven workflow that gets developers right into the action.

# How to Use the 'GVNEngine'?
Currently, the GVNEngine is heavily in development, and not setup for installation quite yet. However, if you're interested in playing with the engine while it's in development, please contact the developer Garrett Fredley at:<br/>
https://twitter.com/SomeCronzaGuy (Professional Twitter) :shipit: <br/>
https://twitter.com/Nixenneth (Private Twitter) :underage:

# License
The GVNEngine is licensed under the Open-Source MIT license. Details can be found in the `LICENSE.txt` file in `/GVNEngine`. Basically, enjoy the engine to it's fullest, and make games without worrying about whether you're allowed to muck around in the source code :smiley:

# Features

## Content-Driven Workflow
The GVNEngine uses YAML for many of it's content files. YAML is a powerful data language built around the concept of human readability. In the engine, YAML is used for all of the following things:
- Scenes
- Dialogue sequences
- Renderables (Objects, interactables, etc)

The GVNEngine is designed to allow users to stick primarily to authoring content in these YAML files without having to deal with much python code. Here is an example of a Point & Click scene YAML file:
```
type: 'PointAndClick'
background: "Content/Sprites/Backgrounds/Classroom_01.jpg"

interactables:
  - data: "Content/Objects/Brown_Bag.yaml"
    position:
      x: 0.65
      y: 0.70
    z_order: 0
    key: "BrownBag"

objects:
  - sprite: "Content/Sprites/Objects/Spreadsheet.png"
    position:
      x: 0.20
      y: 0.70
    z_order: 0
    key: "SpreadSheet"
```
Additional examples of how to create the various YAML files for the engine are provided as a part of the repo.

## Action Manager
The Action Manager system is a flexible system used by the GVNEngine in order to scale to meet any potential number of possible actions the developer may want to perform. Actions are defined as functions in the `actions.py` file. When an action is requested by anything in the engine (Scenes, interactables, etc), it looks to this file for the corresponding action.

Consider the following:

```
- action: "load_sprite"
  key: "Speaker_02"
  sprite: "Content/Sprites/Characters/Rei/Rei_Idle_Smiling.png"
  position:
    x: 0.7
    y: 0.7
  flip: false
  zOrder: 0
  wait_for_input: False
```
The above is an example of an action that loads a sprite into the game. The action name is called 'load_sprite'. In the `actions.py` file, there is a corresponding `def load_sprite` function. The engine is capable of correlating these strings to the functions found in the `actions.py` file. 

Additionally, each action is fed the entire data block of that action. In the example above, we see that various parameters such as 'flip' are provided. Actions are capable of acting on any data provided. For the above `load_sprite` action which is one of the provided engine default actions, flip is used in the action function to flip the sprite when it is drawn to the screen.

# GVNEditor
:warning: *This feature is heavily in development, and will most like be a while before its release
![ScreenShot](Progress_Examples/GVNEditor_v01_Interface.png?raw=true "GVNEditor Main Interface")

The GVNEditor is an editing tool for designing the YAML files used by the GVNEngine. It is built using python and the PyQt5 binding for the Qt framework. 

## License
The GVNEditor, due to its extensive usage of the Qt framework, is licensed under the Open Source GPL license. Details can be found in the `LICENSE.txt` file in `/GVNEditor`. Basically, you can use the editor in most projects besides private, proprietary ones (Where the source code is not available to the general public). This license does not extend to the GVNEngine, and as long as any edits you make to the editor are pushed back to the repo, you are covered :+1:
