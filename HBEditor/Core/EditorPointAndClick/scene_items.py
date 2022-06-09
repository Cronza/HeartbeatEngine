from PyQt5 import QtWidgets, QtGui, QtCore
from HBEditor.Core.settings import Settings
from HBEditor.Core.Logger.logger import Logger
from HBEditor.Core.EditorUtilities.font_manager import FontManager
from HBEditor.Core.DetailsPanel.base_source_entry import SourceEntry


class BaseItem:
    def __init__(self):
        self.root_item = None

    def FindProperty(self, action_data: dict, name: str):
        search_term = "requirements"
        if search_term not in action_data:
            search_term = "children"

        for req in action_data[search_term]:
            if req["name"] == name:
                return req

        return None


class RootItem(QtWidgets.QGraphicsItem, SourceEntry):
    """
    A basic GraphicsItem that acts as the root of a scene_item and its descendents. It serves a few purposes:
    - It is the 'active_entry' for the details panel
    - It can easily be found when using scene.items(), which returns a 1-dimensional array of items (There is no known
    way of just getting the top-most items, so this is workaround)

    Children items don't have the ability to be selected directly. Instead, this item has a boundingrect equal to the
    combined bounding rects of all children, allowing any selection to bubble to this object to decide what should
    happen. When selecting this object, all children are recursively selected as well to allow grouped movement
    """

    def __init__(self, action_data: dict, select_func: callable, data_changed_func: callable):
        super().__init__(None)
        self.action_data = action_data
        self.select_func = select_func
        self.data_changed_func = data_changed_func

        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemIsSelectable)
        self.setFlag(self.ItemSendsGeometryChanges)
        self.setAcceptDrops(True)

    def GenerateChildren(self, parent: QtWidgets.QGraphicsItem = None, action_data: dict = None,
                         pixmap: QtGui.QPixmap = None, text: str = "", search_term: str = "requirements"):
        """ Recursively generate child items in the tree """
        if not action_data:
            action_data = self.action_data

        if not parent:
            parent = self

        # In order to determine what child to spawn, we need to look through all the requirements at a given
        # level, and see if certain names appear. If they do, we give them the full data block
        #
        # IE. {text: '', text_size: '', position: ''}. If 'text' is found, provide all 3 keys
        #
        # Note: Only one of these can appear at any level, otherwise they'd share a data block and cause stomping
        # issues. However, even if we find one of the terms, we keep going in case there are requirements with children
        # which will spawn sub children, causing the process to recurse
        recurse_indices = []
        new_item = None
        for req_index in range(0, len(action_data[search_term])):
            req = action_data[search_term][req_index]
            if req["name"] == "sprite":
                new_item = SpriteItem(
                    action_data=action_data,  # Pass by ref
                    pixmap=pixmap
                )
                new_item.setParentItem(parent)
                new_item.root_item = self
                new_item.Refresh()

            if req["name"] == "text":
                new_item = TextItem(
                    action_data=action_data,  # Pass by ref
                    text=text
                )
                new_item.setParentItem(parent)
                new_item.root_item = self
                new_item.Refresh()

            if "children" in req:
                recurse_indices.insert(-1, req_index)

        for recurse_index in recurse_indices:
            req = action_data[search_term][recurse_index]
            self.GenerateChildren(
                parent=new_item,
                action_data=req,
                pixmap=pixmap,
                text=text,
                search_term="children"
            )

    def Refresh(self, change_tree: list = None):
        # Since 'Refresh' is inherited, we can't change it to allow recursion. To avoid some weird algorithm to achieve
        # that here, use this func as a wrapper to invoke the recursive refresh funcs
        if change_tree:
            self.RefreshRecursivePartial(self, change_tree)
        else:
            self.RefreshRecursive(self)

        # The root item dictates the tree's general z-order. It needs to inherit the z-order of the top-most child
        self.setZValue(self.childItems()[0].zValue())  # The root only ever has a single child

    def RefreshRecursiveAll(self, cur_target: QtWidgets.QGraphicsItem) -> bool:
        """ Perform a full Refresh for all children """
        for child in cur_target.childItems():
            child.Refresh()
            self.RefreshRecursiveAll(child)

        return True

    def RefreshRecursivePartial(self, cur_target: QtWidgets.QGraphicsItem, change_tree: list,
                                search_term: str = "requirements") -> bool:
        """
        Recurse through the child tree for the affected child, then call it's 'Refresh' function with the change
        specified in the change tree
        """
        for child in cur_target.childItems():
            for req in child.action_data[search_term]:
                if req["name"] == change_tree[0]:
                    if len(change_tree) == 1:
                        # We're at the end, so this must be it
                        child.Refresh(change_tree[0])

                        # Certain changes may impact the item's 'boundingRect', which child objects rely on for their
                        # positions. When these changes are detected, we need to fully refresh the item's children
                        # just in case
                        if change_tree[0] == "sprite":
                            self.RefreshRecursiveAll(child)

                        return True
                    else:
                        # Still more to go. Recurse, removing this level from the list we're passing along
                        del change_tree[0]
                        self.RefreshRecursivePartial(
                            cur_target=child,
                            change_tree=change_tree,
                            search_term="children"
                        )
        return False

    def boundingRect(self) -> QtCore.QRectF:
        return self.childrenBoundingRect()

    def paint(self, painter, style, widget=None) -> None:
        pass

    def itemChange(self, change, value):
        """
        OVERRIDE: Called when the item has a change made to it
        """
        if change == QtWidgets.QGraphicsItem.ItemSelectedHasChanged:
            self.select_func()

        return super().itemChange(change, value)

    def mouseReleaseEvent(self, event) -> None:
        """
        OVERRIDE: When the user releases the mouse (presumably after a drag), update the recorded position of
        all children
        """
        for child in self.childItems():
            # Always store a normalized position value between 0-1
            #
            # Normally we'd use 'scenePos' to skip all these conversions, but that seems to return a value that is
            # altered by any translation applied to the item (Needs additional review to confirm). This breaks features
            # such as 'center_align'
            parent_pos = child.pos()
            item_pos = child.mapFromParent(parent_pos)
            scene_pos = child.mapToScene(item_pos)
            norm_range = [
                scene_pos.x() / self.scene().width(),
                scene_pos.y() / self.scene().height()
            ]
            child.FindProperty(child.action_data, "position")["value"] = norm_range

        self.data_changed_func(self)

        super().mouseReleaseEvent(event)


class SpriteItem(QtWidgets.QGraphicsPixmapItem, BaseItem):
    DEFAULT_SPRITE = ":/Sprites/Placeholder.png"

    def __init__(self, action_data: dict, pixmap: QtGui.QPixmap = None):
        super().__init__(pixmap)
        self.action_data = action_data

        self.is_centered = False
        self.is_flipped = False

        self.setFlag(self.ItemSendsGeometryChanges)
        self.setAcceptDrops(True)

    def Refresh(self, changed_entry_name: str = ""):

        if changed_entry_name == "position" or changed_entry_name == "":
            self.UpdatePosition()

        if changed_entry_name == "sprite" or changed_entry_name == "":
            self.UpdateSprite()

        if changed_entry_name == "z_order" or changed_entry_name == "":
            self.UpdateZOrder()

        # Any changes that require a transform adjustment requires all others be updated as well
        if changed_entry_name == "center_align" or self.is_centered or changed_entry_name == "flip" or changed_entry_name == "":
            self.resetTransform()
            new_transform = QtGui.QTransform()

            self.UpdateCenterAlign(new_transform)
            self.UpdateFlip(new_transform)

            self.setTransform(new_transform)

    def UpdatePosition(self):
        # In order to properly update the position, we need to do a number of conversions as 'setPos' is based on the
        # parent's coordinate system, and we typically store position data as scene coordinates. So, we need to:
        #
        # - Take the normalize (0-1) position, and de-normalize it so we have 'scene coordinates'
        # - Convert the scene coordinates to the equivalent position in this item's coordinates
        # - Convert the item coordinates to the equivalent position in this item's parent's coordinates
        #
        # Additionally, the engine renders child objects based on their parent's coordinate system (IE. 0.5, 0.5 is
        # centered in the parent). For this, we change the calculation to use the parent's bounding rect as the bounds
        pos_data = self.FindProperty(self.action_data, "position")["value"]

        if self.parentItem() == self.root_item:
            scene_pos = QtCore.QPointF(
                float(pos_data[0]) * self.scene().width(),
                float(pos_data[1]) * self.scene().height()
            )
            item_pos = self.mapFromScene(scene_pos)
            parent_pos = self.mapToParent(item_pos)
            self.setPos(parent_pos)
        else:
            parent_bounds = self.parentItem().boundingRect()
            scene_pos = QtCore.QPointF(
                float(pos_data[0]) * parent_bounds.width(),
                float(pos_data[1]) * parent_bounds.height()
            )
            parent_pos = self.mapToParent(scene_pos)
            self.setPos(parent_pos)

    def UpdateSprite(self):
        sprite_path = self.DEFAULT_SPRITE
        sprite_rel_path = self.FindProperty(self.action_data, "sprite")["value"]
        if sprite_rel_path != "None":
            sprite_path = f"{Settings.getInstance().user_project_dir}/{sprite_rel_path}"

        image = QtGui.QPixmap(sprite_path)  # If the file does not exist, it will create a null pixmap
        if not image.isNull():
            self.setPixmap(image)
        else:
            Logger.getInstance().Log(f"File does not Exist: '{sprite_path}' - Loading default sprite", 3)
            image = QtGui.QPixmap(self.DEFAULT_SPRITE)
            self.setPixmap(image)

    def UpdateZOrder(self):
        z_order = self.FindProperty(self.action_data, "z_order")["value"]
        self.setZValue(float(z_order))

    def UpdateCenterAlign(self, new_transform: QtGui.QTransform):
        in_use = self.FindProperty(self.action_data, "center_align")
        if in_use:
            if in_use["value"]:
                new_transform.translate(-self.boundingRect().width() / 2, -self.boundingRect().height() / 2)
                self.is_centered = True
            else:
                self.is_centered = False
        else:
            self.is_centered = False

    def UpdateFlip(self, new_transform: QtGui.QTransform):
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

    def Select(self):
        """ Add this object and all children to the active selection """
        self.setSelected(True)
        for child in self.childItems():
            child.Select()


class TextItem(QtWidgets.QGraphicsTextItem, BaseItem):
    DEFAULT_FONT = ":/Fonts/Comfortaa-Regular.ttf"

    def __init__(self, action_data: dict, text: str = "Default"):
        super().__init__(text)
        self.action_data = action_data

        self.is_centered = False
        self.is_flipped = False

        self.setFlag(self.ItemSendsGeometryChanges)
        self.setAcceptDrops(True)

    def Refresh(self, changed_entry_name: str = ""):
        """
        Refresh is the common function used by elements that need refreshing when an important U.I change is made
        """
        if changed_entry_name == "position" or changed_entry_name == "":
            self.UpdatePosition()

        if changed_entry_name == "text" or changed_entry_name == "":
            self.UpdateText()

        if changed_entry_name == "font" or changed_entry_name == "":
            # Changing the font resets the font size, so we must refresh both
            self.UpdateFont()
            self.UpdateTextSize()

        if changed_entry_name == "text_size" or changed_entry_name == "":
            self.UpdateTextSize()

        if changed_entry_name == "text_color" or changed_entry_name == "":
            self.UpdateTextColor()

        if changed_entry_name == "z_order" or changed_entry_name == "":
            self.UpdateZOrder()

        # Any changes that require a transform adjustment requires all others be updated as well
        if changed_entry_name == "center_align" or self.is_centered or changed_entry_name == "":
            self.resetTransform()
            new_transform = QtGui.QTransform()

            self.UpdateCenterAlign(new_transform)

            self.setTransform(new_transform)

    def UpdatePosition(self):
        # In order to properly update the position, we need to do a number of conversions as 'setPos' is based on the
        # parent's coordinate system, and we typically store position data as scene coordinates. So, we need to:
        #
        # - Take the normalize (0-1) position, and de-normalize it so we have 'scene coordinates'
        # - Convert the scene coordinates to the equivalent position in this item's coordinates
        # - Convert the item coordinates to the equivalent position in this item's parent's coordinates
        #
        # Additionally, the engine renders child objects based on their parent's coordinate system (IE. 0.5, 0.5 is
        # centered in the parent). For this, we change the calculation to use the parent's bounding rect as the bounds
        pos_data = self.FindProperty(self.action_data, "position")["value"]

        if self.parentItem() == self.root_item:
            scene_pos = QtCore.QPointF(
                float(pos_data[0]) * self.scene().width(),
                float(pos_data[1]) * self.scene().height()
            )
            item_pos = self.mapFromScene(scene_pos)
            parent_pos = self.mapToParent(item_pos)
            self.setPos(parent_pos)
        else:
            parent_bounds = self.parentItem().boundingRect()
            parent_pos = QtCore.QPointF(
                float(pos_data[0]) * parent_bounds.width(),
                float(pos_data[1]) * parent_bounds.height()
            )
            self.setPos(parent_pos)

    def UpdateText(self):
        text = self.FindProperty(self.action_data, "text")["value"]
        if not text:
            text = "Default"
        self.setPlainText(text)

    def UpdateTextSize(self):
        text_size = self.FindProperty(self.action_data, "text_size")["value"]

        # Enforce a minimum text size
        if text_size < 1:
            text_size = 1

        cur_font = self.font()
        cur_font.setPointSize(text_size)
        self.setFont(cur_font)

    def UpdateFont(self):
        font = self.FindProperty(self.action_data, "font")["value"]
        new_font = None
        if font == "None" or not font:
            font = self.DEFAULT_FONT
            new_font = FontManager.LoadCustomFont(font)

        # @ TODO: Review whether this is the optimal way of differentiating this case and the next one
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

        if new_font:
            self.setFont(new_font)

    def UpdateTextColor(self):
        color = self.FindProperty(self.action_data, "text_color")["value"]
        self.setDefaultTextColor(QtGui.QColor(color[0], color[1], color[2]))

    def UpdateZOrder(self):
        z_order = self.FindProperty(self.action_data, "z_order")["value"]
        self.setZValue(float(z_order))

    def UpdateCenterAlign(self, new_transform: QtGui.QTransform):
        in_use = self.FindProperty(self.action_data, "center_align")
        if in_use:
            if in_use["value"]:
                new_transform.translate(-self.boundingRect().width() / 2, -self.boundingRect().height() / 2)
                self.is_centered = True
            else:
                self.is_centered = False
        else:
            self.is_centered = False

    def Select(self):
        """ Add this object and all children to the active selection """
        self.setSelected(True)
        for child in self.childItems():
            child.Select()
