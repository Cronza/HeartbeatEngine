import os
import pathlib
from PIL import Image, UnidentifiedImageError
from HBEditor.Core import settings
from HBEditor.Core.Logger.logger import Logger


def GenerateThumbnail(path: str) -> str:
    """
    Given a relative file path to an image with the Content folder as the root, generate a thumbnail image for it
    and save it to /Thumbnails. Return the path for the thumbnail if successfully created. Otherwise, return an empty
    string
    """
    # Full path to the source image
    full_image_path = f"{settings.user_project_dir}/{path}"

    # Full path to the thumbnail (Remove the root folder for 'path' as we need the thumbnail folder to be the root)
    thumbnail_image_path = f"{settings.user_project_dir}/Thumbnails/{'/'.join(path.split('/')[1:])}"
    pathlib.Path(os.path.dirname(thumbnail_image_path)).mkdir(parents=True, exist_ok=True)

    try:
        # Open the original file, and overwrite it with a generated, smaller copy. Use (64, 64) to match the size
        # of the editor icons
        img = Image.open(full_image_path)
        img.thumbnail((64, 64))
        bg = Image.new('RGB', (64, 64), (0, 0, 0))

        # Paste the image onto the center of the background
        bg.paste(img, (round(bg.width / 2 - img.width / 2), round(bg.height / 2 - img.height / 2)))

        # Write the changes back to the copy on disc
        img = bg
        img.save(thumbnail_image_path)

        return thumbnail_image_path
    except UnidentifiedImageError:
        Logger.getInstance().Log(
            f"Unable to generate thumbnail for '{full_image_path}' as it does not appear to be an image")

    return ""


def GetThumbnail(path: str) -> str:
    """
    Given a relative file path to an image with the Content folder as the root, check if there is a matching
    thumbnail in the thumbnails directory. Returns the thumbnail file path if found. Otherwise, returns an empty string
    """
    # Full path to the thumbnail (Remove the root folder for 'path' as we need the thumbnail folder to be the root)
    thumbnail_image_path = f"{settings.user_project_dir}/Thumbnails/{'/'.join(path.split('/')[1:])}"
    if os.path.exists(thumbnail_image_path):
        return thumbnail_image_path
    else:
        return ""