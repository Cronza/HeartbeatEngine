import os
from PyQt5 import QtWidgets, QtGui
from HBEditor.Core.settings import Settings
from HBEditor.Core.Logger.logger import Logger
from HBEditor.Core.Managers.font_manager import FontManager
#@TODO: Investigate how to subclass 'QGraphicsItem' to consolidate common code


class SceneItemUtilities:
    def FindProperty(self, action_data, name):
        for index, req in enumerate(action_data["requirements"]):
            if req["name"] == name:
                return req

        return None


class SpriteItem(QtWidgets.QGraphicsPixmapItem, SceneItemUtilities):
    def __init__(self, pixmap, action_data, move_func, select_func, data_changed_func):
        super().__init__(pixmap)

        self.action_data = action_data

        self.move_func = move_func
        self.select_func = select_func
        self.data_changed_func = data_changed_func

        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemIsSelectable)
        self.setFlag(self.ItemSendsGeometryChanges)
        self.setAcceptDrops(True)

        # States
        self.is_centered = False
        self.is_flipped = False

    def Refresh(self):
        """
        Refresh is the common function used by elements that need refreshing when an important U.I change is made
        """
        #@TODO: Investigate making this more efficient

        # Start with a fresh state, so any transforms apply properly
        self.resetTransform()
        new_transform = QtGui.QTransform()

        # Update the position
        new_pos = self.FindProperty(self.action_data, "position")["value"]

        # Because the position is stored normalized between 0-1, inverse normalize the position value
        self.setPos(
            float(new_pos[0]) * self.scene().width(),
            float(new_pos[1]) * self.scene().height()
        )
        # Update the sprite
        sprite_rel_path = self.FindProperty(self.action_data, "sprite")["value"]

        sprite_path = ""
        if sprite_rel_path == "None":
            sprite_path = ":/Sprites/Placeholder.png"
        else:
            sprite_path = f"{Settings.getInstance().user_project_dir}/{sprite_rel_path}"

        if os.path.exists(sprite_path):
            image = QtGui.QPixmap(sprite_path)
            self.setPixmap(image)
        else:
            Logger.getInstance().Log(f"File does not Exist: '{sprite_path}'", 3)

        # Update the z_order
        z_order = self.FindProperty(self.action_data, "z_order")["value"]
        self.setZValue(float(z_order))

        # (OPTIONAL) Update center align
        in_use = self.FindProperty(self.action_data, "center_align")
        if in_use:
            if in_use["value"]:
                new_transform.translate(-self.boundingRect().width() / 2, -self.boundingRect().height() / 2)
                self.is_centered = True
            else:
                self.is_centered = False
        else:
            self.is_centered = False

        # (OPTIONAL) Update flip
        in_use = self.FindProperty(self.action_data, "flip")
        if in_use:
            if in_use["value"]:
                # Due to the fact scaling inherently moves the object due to using the transform origin, AND due to the
                # fact you can't change the origin, we have a hard dependency on knowing whether center align
                # is active, so we know how to counter the movement from the scaling
                if self.is_centered:
                    # We need to reverse the movement from center_align in the X (we don't flip in the Y).
                    # m31 represents the amount of horizontal translation that has been applied so far
                    new_transform.translate(-new_transform.m31() * 2, 0)
                else:
                    new_transform.translate(self.boundingRect().width(), 0)

                new_transform.scale(-1, 1)
                self.is_flipped = True
            else:
                self.is_flipped = False
        else:
            self.is_flipped = False

        # Apply the new transform, and any changes made to it
        self.setTransform(new_transform)

    def itemChange(self, change, value):
        """
        OVERRIDE: Called when the item has a change made to it. Currently, only selection changes are included
        """
        if change == QtWidgets.QGraphicsItem.ItemSelectedHasChanged:
            self.select_func()

        return super().itemChange(change, value)

    def mouseReleaseEvent(self, event) -> None:
        """ OVERRIDE: When the user releases the mouse (presumably after a drag), update the recorded position """

        # Always store a normalized position value between 0-1
        cur_pos = self.pos()
        norm_range = [
            round(cur_pos.x() / self.scene().width(), 2),
            round(cur_pos.y() / self.scene().height(), 2)
        ]
        self.FindProperty(self.action_data, "position")["value"] = norm_range
        self.data_changed_func(self)

        super().mouseReleaseEvent(event)


class TextItem(QtWidgets.QGraphicsTextItem, SceneItemUtilities):
    def __init__(self, text, action_data, move_func, select_func, data_changed_func):
        super().__init__(text)

        self.action_data = action_data

        self.move_func = move_func
        self.select_func = select_func
        self.data_changed_func = data_changed_func

        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemIsSelectable)
        self.setFlag(self.ItemSendsGeometryChanges)
        self.setAcceptDrops(True)

        # States
        self.is_centered = False

    def Refresh(self):
        """
        Refresh is the common function used by elements that need refreshing when an important U.I change is made
        """
        #@TODO: Investigate making this more efficient

        # Start with a fresh state, so any transforms apply properly
        self.resetTransform()
        new_transform = QtGui.QTransform()

        # Update the position
        new_pos = self.FindProperty(self.action_data, "position")["value"]

        # Because the position is stored normalized between 0-1, inverse normalize the position value
        self.setPos(
            float(new_pos[0]) * self.scene().width(),
            float(new_pos[1]) * self.scene().height()
        )

        # Update the text
        text = self.FindProperty(self.action_data, "text")["value"]
        if not text:
            text = "Default"
        self.setPlainText(text)

        # Update the font, text_size
        text_size = self.FindProperty(self.action_data, "text_size")["value"]
        font = self.FindProperty(self.action_data, "font")["value"]

        new_font = None
        if font == "None" or not font:
            # Use the default editor-kept font if the user did not assign a font
            font = ":/Fonts/Comfortaa-Regular.ttf"
            new_font = FontManager.LoadCustomFont(font)

        #@ TODO: Review whether this is the optimal way of differentiating this case and the next one
        elif font.startswith("Content"):
            # This is likely a real path
            font = f"{Settings.getInstance().user_project_dir}/{font}"
            new_font = FontManager.LoadCustomFont(font)

        else:
            # This might be the user trying to load a system font
            split_str = font.split("|", 1)
            if len(split_str) == 2:
                new_font = FontManager.LoadFont(split_str[0], split_str[1])  # Format: <name> <style>
            else:
                new_font = FontManager.LoadFont(split_str[0])

        # Enforce a minimum text size
        if text_size < 1:
            text_size = 1

        # If the font load failed for any reason, only update the size
        if new_font:
            new_font.setPointSize(text_size)
            self.setFont(new_font)
        else:
            self.font().setPointSize(text_size)
            self.setFont(self.font())

        # Update the text color
        color = self.FindProperty(self.action_data, "text_color")["value"]
        self.setDefaultTextColor(QtGui.QColor(color[0], color[1], color[2]))

        # Update the z_order
        z_order = self.FindProperty(self.action_data, "z_order")["value"]
        self.setZValue(float(z_order))

        # (OPTIONAL) Update center align
        center_align = self.FindProperty(self.action_data, "position")["value"]
        if center_align:
            new_transform.translate(-self.boundingRect().width() / 2, -self.boundingRect().height() / 2)
            self.is_centered = True
        else:
            self.is_centered = False

        # Apply the new transform, and any changes made to it
        self.setTransform(new_transform)

    def itemChange(self, change, value):
        """
        OVERRIDE: Called when the item has a change made to it. Currently, only selection changes are included
        """
        if change == QtWidgets.QGraphicsItem.ItemSelectedHasChanged:
            self.select_func()

        return super().itemChange(change, value)

    def mouseReleaseEvent(self, event) -> None:
        """ OVERRIDE: When the user releases the mouse (presumably after a drag), update the recorded position """

        # Always store a normalized position value between 0-1
        cur_pos = self.pos()
        norm_range = [
            round(cur_pos.x() / self.scene().width(), 2),
            round(cur_pos.y() / self.scene().height(), 2)
        ]
        self.FindProperty(self.action_data, "position")["value"] = norm_range
        self.data_changed_func(self)

        super().mouseReleaseEvent(event)


