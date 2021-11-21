import os
from PyQt5 import QtWidgets, QtGui


class SceneItem(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, pixmap, settings, action_data):
        super().__init__(pixmap)

        self.settings = settings
        self.action_data = action_data

        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemIsSelectable)

        # Cache the index where the important action data elements are, so we don't iterate through each time
        # (This is on the assumption and knowledge that the order will never change)
        for index, req in enumerate(self.action_data["requirements"]):
            if req["name"] == "position":
                self.position_index = index
            elif req["name"] == "sprite":
                self.sprite_index = index
            elif req["name"] == "z_order":
                self.z_order_index = index

    def Refresh(self):
        """
        Refresh is the common function used by elements that need refreshing when an important U.I change is made
        """
        # Update the position
        new_pos = self.action_data["requirements"][self.position_index]["value"]
        self.setPos(float(new_pos[0]), float(new_pos[1]))

        # Update the sprite
        sprite_path = self.action_data["requirements"][self.sprite_index]["value"]
        if sprite_path != "None":
            if os.path.exists(sprite_path):
                image = QtGui.QPixmap(sprite_path)
                self.setPixmap(image)
            else:
                print("File does not Exist")
                # Implement logger call here

        # Update the z_order
        z_order = self.action_data["requirements"][self.z_order_index]["value"]
        self.setZValue(float(z_order))
