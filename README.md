# GVNEngine
![ScreenShot](Images/GVNEngine_Banner.jpg?raw=true "GVNEngine Banner")

[![License](https://img.shields.io/badge/license-MIT-green?label=engine-license&style=flat-square)](./GVNEngine/LICENSE.txt)
[![License](https://img.shields.io/badge/license-GPLv2-blue?label=editor-license&style=flat-square)](./GVNEditor/LICENSE.txt)
[![GitHub issues](https://img.shields.io/github/issues-raw/Cronza/GVNEngine?style=flat-square)](https://github.com/Cronza/GVNEngine/issues)
[![Python Version](https://img.shields.io/badge/python-3.8-4B8BBE)](https://www.python.org/downloads/release/python-380/)
[![Twitter Badge](https://img.shields.io/badge/Twitter-Profile-informational?style=flat&logo=twitter&logoColor=white&color=1CA2F1)](https://twitter.com/SomeCronzaGuy)

<p align="center"><em>A Visual Novel / Dating Sim Game Engine Designed for Creative Developers</em></p>

# What is the 'GVNEngine'?

The GVNEngine is a Visual Novel / Dating Simulator game engine written in Python using the PyGame framework. It comes with a fully-fledged editor built in Pyqt5. It is meant as a lightweight, user-friendly engine that offers a content-driven workflow to allow developers to focus more on making games, and less on worrying about coding them.

# Getting Started with the GVNEngine
Currently, the GVNEngine is heavily in development, and not setup for installation quite yet. However, if you're interested in playing with the engine while it's in development, feel free to clone the repo!

# License
The GVNEngine is licensed under the Open-Source MIT license. Details can be found in the `LICENSE.txt` file in `/GVNEngine`. Basically, enjoy the engine to it's fullest, and make games without worrying about whether you're allowed to muck around in the source code :smiley:

The GVNEditor, due to its extensive usage of the Qt framework, is licensed under the Open Source GPL license. Details can be found in the `LICENSE.txt` file in `/GVNEditor`. Basically, you can use the editor in most projects besides private, proprietary ones (Where the source code is not available to the general public). This license does not extend to the GVNEngine, and as long as any edits you make to the editor are pushed back to the repo, you are covered :+1:
 
# Features
## Content-Driven Workflow
![ScreenShot](Progress_Examples/v02/GVNEngine_v02_Dialogue_Scene.png?raw=true "GVNEngine Dialogue Scene")
<p align="center"><em>Fig 1 - A demonstration of dialogue with a choice prompt</em></p>
The GVNEngine leverages a data language called YAML, which was designed for human readability to simplify the process of creating all sorts of content, such as:

- Scenes
- Dialogue sequences
- Renderables (Objects, interactables, buttons, etc)
- Effects (Fades, scene transitions, etc)

An example of a block of YAML representing the action to create a background sprite:
```
action: create_background
key: Background
sprite: Content/Backgrounds/Background_Space_01_1280.jpg
position:
- 0.0
- 0.0
post_wait: no_wait
```

While the GVNEditor acts as a wrapper for these files, anyone can edit these files directly if they need to perform a hotfix, or need to make changes through automation.

## The GVNEditor
![ScreenShot](Progress_Examples/v02/GVNEditor_v02_Dialogue_Editor_02.png?raw=true "GVNEngine Dialogue Scene")
<p align="center"><em>Fig 2 - The 'Dialogue Scene' editor within the GVNEditor</em></p>

Using the GVNEditor, developers can stay out of a complicated IDE or set of code files, and stick to a comfortable environment tailored for content authoring. The editor acts as a wrapper for individual editors, such as:
- Dialogue Scene
- Point and Click Scene *TBD
- Character Creator *TBD
- Project Settings

The GVNEditor comes bundled with the engine, and provides all the tools and functions necessary for interfacing with the GVNEngine

## Action Manager
The Action Manager was created in order to allow developers (and the engine) to access any number of possible in-game actions in a flexible, YAML-accessible manner.

'Actions' are defined as classes in the `actions.py` file. When an action is requested, such as by a YAML file (Dialogue, clicking interactables, etc), it looks to this file for the corresponding action class. For example: `class load_scene(Action)`. Once found, it calls it, passing it any additional pieces of information provided. An example of a dialogue YAML block:

```
- action: "dialogue"
  character: "Isea"
  dialogue:
    text: "Who are you?"
  wait_for_input: True
```
The above is an example of an action used to display dialogue text to the screen. The action name is called `dialogue`. In the `actions.py` file, there is a corresponding `class dialogue(Action)` class. The engine is capable of correlating these strings to the classes found in the `actions.py` file. 

Additionally, each action is fed the entire data block that was provided when it was called. In the example above, we see that various parameters such as `character` are provided. For the above `dialogue` action, which is one of the provided engine default actions, `character` is used to determine the speaker's name, the color of their name, and the font for their name text.
