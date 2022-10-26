import math
import copy
from PyQt5 import QtWidgets, QtGui, QtCore
from HBEditor.Core import settings
from HBEditor.Core.Logger.logger import Logger
from HBEditor.Core.EditorUtilities.font_manager import FontManager
from HBEditor.Core.DetailsPanel.base_source_entry import SourceEntry
from HBEditor.Core.EditorUtilities import action_data_handler as adh
from HBEditor.Core.EditorUtilities import file_system_handler as fsh


class BaseItem:
    def __init__(self):
        self.root_item = None


class RootItem(QtWidgets.QGraphicsItem, SourceEntry):
    """
    A basic GraphicsItem that acts as the root of a scene_item and its descendants. It serves a few purposes:
    - It is the 'active_entry' for the details panel
    - It can easily be found when using scene.items(), which returns a 1-dimensional array of items (There is no known
    way of just getting the top-most items, so this is workaround)

    Children items don't have the ability to be selected directly. Instead, this item has a boundingrect equal to the
    combined bounding rects of all children, allowing any selection to bubble to this object to decide what should
    happen. When selecting this object, all children are recursively selected as well to allow grouped movement
    """

    def __init__(self, action_data: dict, select_func: callable):
        super().__init__(None)
        self.action_data = copy.deepcopy(action_data)  # Copy to avoid changes bubbling to the origin
        self.select_func = select_func

        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemIsSelectable)
        self.setFlag(self.ItemSendsGeometryChanges)

        self.setAcceptDrops(True)

        self._movement_locked = False  # User controlled
        self._movement_perm_locked = False  # System enforced - Disables the usage of 'movement_locked'

    def GetLocked(self):
        if self._movement_perm_locked:
            return self._movement_perm_locked
        else:
            return self._movement_locked

    def SetLocked(self, state: bool) -> bool:
        """
        Updates the locked state of the item. Return whether the operation was performed successfully

        If the item is permanently locked, then always return False
        """
        if self._movement_perm_locked:
            return False

        self._movement_locked = state
        if state:
            self.setFlags(self.flags() & ~self.ItemIsMovable)
        else:
            self.setFlags(self.flags() | self.ItemIsMovable)

        return True

    def GenerateChildren(self, parent: QtWidgets.QGraphicsItem = None, action_data: dict = None,
                         pixmap: QtGui.QPixmap = None, text: str = "", search_term: str = "requirements"):
        """
        Recursively generate child items in the tree for each item in the action_data. All items are created with
        the full requirements data block
        """
        # Set values for the top-most item
        if not action_data and not parent:
            action_data = self.action_data[adh.GetActionName(self.action_data)][search_term]
            parent = self

            # Some properties have special implications on usability within the editor (IE. position being uneditable
            # could apply a lock which prevents user control). Apply these effects only based on the data
            # from the top-most item
            if "position" in action_data:
                if not action_data['position']['editable']:
                    self.SetLocked(True)
                    self._movement_perm_locked = True

        # In order to determine what child to spawn, we need to look through all the requirements at a given
        # level, and see if certain names appear. If they do, we give them the full data block
        #
        # IE. {text: '', text_size: '', position: ''}. If 'text' is found, provide all 3 keys
        #
        # Note: Only one of these can appear at any level, otherwise multiple items would share a data block and cause
        # stomping issue
        new_item = None

        for req_name, req_data in action_data.items():
            if req_name == "sprite":
                new_item = SpriteItem(
                    action_data=action_data,  # Pass by ref
                    pixmap=pixmap
                )
                new_item.setParentItem(parent)
                new_item.root_item = self
                new_item.Refresh()

            elif req_name == "text":
                new_item = TextItem(
                    action_data=action_data,  # Pass by ref
                    text=text
                )
                new_item.setParentItem(parent)
                new_item.root_item = self
                new_item.Refresh()

            if "children" in req_data:
                self.GenerateChildren(
                    parent=new_item,
                    action_data=req_data["children"],
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

        # The root item uses the top-most child's z-order, so they both need to be updated
        if change_tree[0] == "z_order":
            self.UpdateZValue()

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
            if change_tree[0] in child.action_data:
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

    def UpdateZValue(self):
        """ Updates this object's z-value using it's top-most child's z-value """
        self.setZValue(self.childItems()[0].zValue())

    def boundingRect(self) -> QtCore.QRectF:
        return self.childrenBoundingRect()

    def paint(self, painter, style, widget=None) -> None:
        if self.isSelected():
            # Draw a selection border
            pen = painter.pen()
            pen.setColor(QtGui.QColor(45, 83, 115))
            pen.setWidth(3)
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())

    def mouseReleaseEvent(self, event) -> None:
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
            child.action_data["position"]["value"] = norm_range

        # Refresh in case position changed while dragging
        self.select_func()

        super().mouseReleaseEvent(event)


class SpriteItem(QtWidgets.QGraphicsPixmapItem, BaseItem):
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
        # - Take the normalize (0-1) position, and denormalize it so we have 'scene coordinates'
        # - Convert the scene coordinates to the equivalent position in this item's coordinates
        # - Convert the item coordinates to the equivalent position in this item's parent's coordinates
        #
        # Additionally, the engine renders child objects based on their parent's coordinate system (IE. 0.5, 0.5 is
        # centered in the parent). For this, we change the calculation to use the parent's bounding rect as the bounds
        if self.action_data["position"]["value"] is not None:
            if self.parentItem() == self.root_item:
                scene_pos = QtCore.QPointF(
                    float(self.action_data["position"]["value"][0]) * self.scene().width(),
                    float(self.action_data["position"]["value"][1]) * self.scene().height()
                )
                item_pos = self.mapFromScene(scene_pos)
                parent_pos = self.mapToParent(item_pos)
                self.setPos(parent_pos)
            else:
                parent_bounds = self.parentItem().boundingRect()
                scene_pos = QtCore.QPointF(
                    float(self.action_data["position"]["value"][0]) * parent_bounds.width(),
                    float(self.action_data["position"]["value"][1]) * parent_bounds.height()
                )
                parent_pos = self.mapToParent(scene_pos)
                self.setPos(parent_pos)

    def UpdateSprite(self):
        image = QtGui.QPixmap(fsh.ResolveImageFilePath(self.action_data["sprite"]["value"]))
        self.setPixmap(image)

    def UpdateZOrder(self):
        self.setZValue(float(self.action_data["z_order"]["value"]))

    def UpdateCenterAlign(self, new_transform: QtGui.QTransform):
        if self.action_data["center_align"]["value"]:
            new_transform.translate(-self.boundingRect().width() / 2, -self.boundingRect().height() / 2)
            self.is_centered = True
        else:
            self.is_centered = False

    def UpdateFlip(self, new_transform: QtGui.QTransform):
        if self.action_data["flip"]["value"]:
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

    def Select(self):
        """ Add this object and all children to the active selection """
        self.setSelected(True)
        for child in self.childItems():
            child.Select()


class TextItem(QtWidgets.QGraphicsTextItem, BaseItem):
    def __init__(self, action_data: dict, text: str = "Default"):
        super().__init__(text)
        self.action_data = action_data

        self.is_centered = False
        self.is_flipped = False

        self.setFlag(self.ItemSendsGeometryChanges)
        self.setAcceptDrops(True)
        self.document().setDocumentMargin(0)

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

            #@TODO: The engine and editor differ on text spacing, and the following code is experimental towards fixing it
            #metrics = QtGui.QFontMetricsF(self.font())
            #normal_rect = metrics.boundingRect(self.toPlainText())
            #tight_rect = metrics.tightBoundingRect(self.toPlainText())
            #print(self.toPlainText())
            #print(f"Normal: {normal_rect}")
            #print(f"Tight: {tight_rect}")
            #print(f"Height: {metrics.height()}")
            #print("\n")

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
        if self.action_data["position"]["value"] is not None:
            if self.parentItem() == self.root_item:
                scene_pos = QtCore.QPointF(
                    float(self.action_data["position"]["value"][0]) * self.scene().width(),
                    float(self.action_data["position"]["value"][1]) * self.scene().height()
                )
                item_pos = self.mapFromScene(scene_pos)
                parent_pos = self.mapToParent(item_pos)
                self.setPos(parent_pos)
            else:
                parent_bounds = self.parentItem().boundingRect()
                parent_pos = QtCore.QPointF(
                    float(self.action_data["position"]["value"][0]) * parent_bounds.width(),
                    float(self.action_data["position"]["value"][1]) * parent_bounds.height()
                )
                self.setPos(parent_pos)

    def UpdateText(self):
        if self.action_data["text"]["value"] == "" or self.action_data["text"]["value"].lower() == "none":
            self.action_data["text"]["value"] = "Default"
        else:
            self.setPlainText(self.action_data["text"]["value"])

    def UpdateTextSize(self):
        # Enforce a minimum text size
        if self.action_data["text_size"]["value"] < 1:
            self.action_data["text_size"]["value"] = 1

        cur_font = self.font()
        cur_font.setPixelSize(self.action_data["text_size"]["value"])
        self.setFont(cur_font)

    def UpdateFont(self):
        new_font = FontManager.LoadCustomFont(fsh.ResolveFontFilePath(self.action_data["font"]["value"]))
        self.setFont(new_font)

    def UpdateTextColor(self):
        color = self.action_data["text_color"]["value"]
        self.setDefaultTextColor(QtGui.QColor(color[0], color[1], color[2]))

    def UpdateZOrder(self):
        self.setZValue(float(self.action_data["z_order"]["value"]))

    def UpdateCenterAlign(self, new_transform: QtGui.QTransform):
        if self.action_data["center_align"]["value"]:
            new_transform.translate(-self.boundingRect().width() / 2, -self.boundingRect().height() / 2)
            self.is_centered = True
        else:
            self.is_centered = False

    def Select(self):
        """ Add this object and all children to the active selection """
        self.setSelected(True)
        for child in self.childItems():
            child.Select()
