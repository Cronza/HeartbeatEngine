from HBEngine.Core import settings
from HBEngine.Core.DataTypes.file_types import FileType
from HBEngine.Core.Scenes.scene_pointandclick import PointAndClickScene
from HBEngine.Core.Scenes.scene_dialogue import DialogueScene


def LoadScene(scene_file: str):
    """ Given a path to a scene file, check its type, and load the corresponding scene object """
    # We need to read the file to find its type. This is denoted by the 'type' value somewhere near the top of the
    # file. We can't guarantee its position since the metadata may grow one day, and the line number would shift.
    scene_type = None
    with open(settings.ConvertPartialToAbsolutePath(scene_file), "r") as f:
        for line in f:
            if line.startswith("type:"):
                scene_type = FileType[line.replace("type: ", "").strip()]

    if scene_type is not None:
        if scene_type in scene_types:
            del settings.active_scene
            settings.active_scene = scene_types[scene_type](scene_file, window)
        else:
            raise ValueError(f"Failed to Load Scene - Specified scene type does not exist: {scene_type}")
    else:
        raise ValueError(f"No scene type specified in file '{scene_file}'")


window = None  # The main window scenes are displayed within

# Note: Scene types will be deprecated in a future update, and will be replaced with a singular scene type
scene_types = {
    FileType.Scene_Dialogue: DialogueScene,
    FileType.Scene_Point_And_Click: PointAndClickScene
}