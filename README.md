# Heartbeat Engine
![ScreenShot](Images/HeartbeatEngine_Banner.jpg?raw=true "Heartbeat Engine Banner")
[![License](https://img.shields.io/badge/license-GPLv3-blue?label=license&style=flat-square)](LICENSE.txt)
[![GitHub issues](https://img.shields.io/github/issues-raw/Cronza/HeartbeatEngine?style=flat-square)](https://github.com/Cronza/HeartbeatEngine/issues)
[![Python Version](https://img.shields.io/badge/python-3.8-4B8BBE?style=flat-square)](https://www.python.org/downloads/release/python-380/)
[![Twitter Badge](https://img.shields.io/badge/Twitter-Profile-informational?style=flat-square&logo=twitter&logoColor=white&color=1CA2F1)](https://twitter.com/SomeCronzaGuy)

<p align="center"><em>A Visual Novel / Dating Sim Game Engine Designed for Creative Developers</em></p>

# What is the 'Heartbeat Engine'?

The Heartbeat Engine is a Visual Novel / Dating Simulator game engine written in Python using the PyGame framework, with a fully-fledged editor built in PyQt5. It is meant as a lightweight, user-friendly engine that allows developers to focus more on making games, and less on worrying about coding them.

# Getting Started
Currently, the Heartbeat Engine is heavily in development, and not setup for installation quite yet. However, if you're interested in playing with the engine while it's in development, feel free to clone the repo!

# License
The Heartbeat Engine is licensed under the GPL version 3 (GPLv3) license. Details can be found in the `LICENSE.txt` file, but essentially any projects created with the engine are entirely, 100% yours. You may use your own license for them, keep them as private works, and release them commercially without worry. 

However, if you decide to fork the engine and alter or extend its behaviour (which I wholeheartedly welcome!), then that code must abide by the GPLv3 license and remain open source.
 
# Features
## Data-Driven Workflow
![ScreenShot](Images/v02_Dialogue_Scene.png?raw=true "Dialogue Scene")
<p align="center"><em>Fig 1 - A demonstration of dialogue with a choice prompt</em></p>
The Heartbeat Engine leverages a data language called YAML, which was designed for human readability to simplify the process of creating all sorts of content, such as:

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

While the Heartbeat Editor acts as a wrapper for these files, anyone can edit these files directly if they need to perform a hotfix, or need to make changes through automation.

## The Heartbeat Editor
![ScreenShot](Images/v02_Dialogue_Editor.png?raw=true "Dialogue Editor")
<p align="center"><em>Fig 2 - The 'Dialogue Scene' editor within the Heartbeat Editor</em></p>

Using the Heartbeat Editor, developers can stay out of a complicated IDE or set of code files, and stick to a comfortable environment tailored for content authoring. The editor acts as a wrapper for individual editors, such as:
- Dialogue Scene
- Point and Click Scene *TBD
- Character Creator *TBD
- Project Settings

The editor comes bundled with the engine, and provides all the tools and functions necessary for interfacing with the engine

## Action Manager
The Action Manager was created in order to allow developers (and the engine) to access any number of possible in-game actions in a flexible, YAML-accessible manner.

'Actions' are defined as classes in the `actions.py` file. When an action is requested, such as by a YAML file (Dialogue, clicking interactables, etc), it looks to this file using Python's reflection capabilities for the corresponding action class. For example: `class load_scene(Action)`. Once found, it calls it, passing it any additional pieces of information provided. An example of a dialogue YAML block:

```
- action: "dialogue"
  character: "Isea"
  dialogue:
    text: "Who are you?"
  wait_for_input: True
```
The above is an example of an action used to display dialogue text to the screen. The action name is called `dialogue`. In the `actions.py` file, there is a corresponding `class dialogue(Action)` class. The engine is capable of correlating these strings to the classes found in the `actions.py` file. 

Additionally, each action is fed the entire data block that was provided when it was called. In the example above, we see that various parameters such as `character` are provided. For the above `dialogue` action, which is one of the provided engine default actions, `character` is used to determine the speaker's name, the color of their name, and the font for their name text.
