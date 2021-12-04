import os
from PyQt5 import QtWidgets, QtGui
from HBEditor.Core.settings import Settings
from HBEditor.Core.Logger.logger import Logger

class SceneItem(QtWidgets.QGraphicsPixmapItem):
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
        #self.is_centered = False
        #self.is_flipped = False

        # Cache the index where the important action data elements are, so we don't iterate through each time
        # (This is on the assumption and knowledge that the order will never change)
        self.position_index = None
        self.sprite_index = None
        self.z_order_index = None
        self.center_align_index = None
        self.flip_index = None
        for index, req in enumerate(self.action_data["requirements"]):
            if req["name"] == "position":
                self.position_index = index
            elif req["name"] == "sprite":
                self.sprite_index = index
            elif req["name"] == "z_order":
                self.z_order_index = index
            elif req["name"] == "center_align":
                self.center_align_index = index
            elif req["name"] == "flip":
                self.flip_index = index

    def Refresh(self):
        """
        Refresh is the common function used by elements that need refreshing when an important U.I change is made
        """
        #@TODO: Investigate making this more efficient

        # Start with a fresh state, so any transforms apply properly
        self.resetTransform()
        new_transform = QtGui.QTransform()
        hori_translation = new_transform.m31()
        vert_translation = new_transform.m32()

        # Update the position
        new_pos = self.action_data["requirements"][self.position_index]["value"]

        # Because the position is stored normalized between 0-1, inverse normalize the position value
        self.setPos(
            float(new_pos[0]) * self.scene().width(),
            float(new_pos[1]) * self.scene().height()
        )
        # Update the sprite
        sprite_path = Settings.getInstance().user_project_dir + "/" + \
                      self.action_data["requirements"][self.sprite_index]["value"]

        if sprite_path != "None":
            if os.path.exists(sprite_path):
                image = QtGui.QPixmap(sprite_path)
                self.setPixmap(image)
            else:
                Logger.getInstance().Log(f"File does not Exist: '{sprite_path}'", 3)

        # Update the z_order
        z_order = self.action_data["requirements"][self.z_order_index]["value"]
        self.setZValue(float(z_order))

        # (OPTIONAL) Update center align
        if self.center_align_index is not None:
            center_align = self.action_data["requirements"][self.center_align_index]["value"]
            if center_align:
                print("Centering")
                new_transform.translate(-self.boundingRect().width() / 2, -self.boundingRect().height() / 2)
                hori_translation = new_transform.m31()
                vert_translation = new_transform.m32()
                print(hori_translation)
                print(vert_translation)

        # (OPTIONAL) Update flip
        if self.flip_index is not None:
            flip = self.action_data["requirements"][self.flip_index]["value"]
            if flip:
                print("Flipping")
                new_transform.scale(-1, 1)
                print(new_transform.m31())
                print(new_transform.m32())

                if hori_translation == 0 and vert_translation == 0:
                    pass
                else:
                    new_transform.translate(
                        hori_translation + new_transform.m31(),
                        vert_translation - new_transform.m32()
                    )

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
        self.action_data["requirements"][self.position_index]["value"] = norm_range
        self.data_changed_func(self)

        super().mouseReleaseEvent(event)

    def AdjustTranslation(self, cur_m31, cur_m32, new_m31, new_m32) -> tuple:
        pass
        #if
        #hori_translation + new_transform.m31(),
        #vert_translation - new_transform.m32()

