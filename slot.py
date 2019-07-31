import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph import functions as fn
from pyqtgraph.graphicsItems.GraphicsObject import GraphicsObject
import numpy as np
from colour import Color
from functools import partial

red = Color("red")
colors = [QtGui.QColor(*(255*np.array(color.get_rgb()))) for color in list(red.range_to(Color("green"),100))]

class Slot(object):
    def __init__(self, position, coords, label, cell_manager, slot_holder, cell_template=None):
        self.position = position
        self.coords = coords
        self.label = label
        self.is_reference = False
        self.slotItem = SlotItem(self)
        self.cell = None
        self.cell_manager = cell_manager
        self.slot_holder = slot_holder
        if cell_template: self.cell_template = cell_template

    @property
    def stage_coords(self):
        return self.slot_holder.to_stage_coords(self.coords)

    def setCell(self,cell,update_table=True):
        # The slot already has a cell in place, so we delete the cell that is not going to be used
        if self.cell != cell:
            if self.cell is not None:
                self.cell_manager.removeCell(self.cell,update_table)
            self.cell = cell
            self.cell.setSlot(self,update_table)
            self.slotItem.update_labels()
            self.slotItem.update_contrast_label()

    def removeCell(self,update_table=True):
        if self.cell is not None:
                self.cell_manager.removeCell(self.cell,update_table)
        self.cell = None
        self.slotItem.update_labels()

    def setReference(self):
        if not self.is_reference:
            self.slot_holder.addReferenceSlot(self)
            self.slotItem.update()

    def delReference(self):
        self.slot_holder.removeReferenceSlot(self)
        self.slotItem.update()

    def moveTo(self,local_coords=[0.,0.],device_coords=[0.,0.],wait=False):
        self.slot_holder.stage.move_to(self.slot_holder.to_stage_coords(self.coords+np.array(local_coords))-np.array(device_coords),wait=wait)

    # Clear the slot without deleting cell
    def clear(self):
        self.cell = None
        self.slotItem.update_labels()


SlotLabelColor = QtGui.QColor(200, 200, 200)
CellLabelColor = QtGui.QColor(255, 255, 255)
CsLabelColor = QtGui.QColor(50, 50, 255)
RbLabelColor = QtGui.QColor(150, 20, 180)

class SlotItem(pg.GraphicsObject):

    def __init__(self, slot):
        pg.GraphicsObject.__init__(self)
        self.pen = fn.mkPen(0,0,0)
        self.reference_pen = fn.mkPen(255,0,0,125,width=5)
        self.selectPen = fn.mkPen(200,200,200,width=2)
        self.brush = fn.mkBrush(100, 100, 100, 100)
        self.occupiedBrush = fn.mkBrush(150, 150, 150, 150)
        self.hoverBrush = fn.mkBrush(200, 200, 255, 100)
        self.selectBrush = fn.mkBrush(200, 200, 255, 200)
        self.hovered = False
        self.slot = slot

        flags = self.ItemIsSelectable | self.ItemIsFocusable #|self.ItemSendsGeometryChanges

        self.setFlags(flags)
        self.setPos(44*self.slot.position[0],64*self.slot.position[1])
        self.bounds = QtCore.QRectF(0, 0, 40, 60)
        self.nameItem = QtGui.QGraphicsTextItem(self.slot.label, self)
        self.nameItem.setDefaultTextColor(SlotLabelColor)
        self.nameItem.moveBy(self.bounds.width()/2. - self.nameItem.boundingRect().width()/2., 0)
        self.nameItem.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)

        self.nameItem.focusOutEvent = self.labelFocusOut
        self.nameItem.keyPressEvent = self.labelKeyPress

        self.alkaliItem = QtGui.QGraphicsTextItem("", self)
        self.alkaliItem.setDefaultTextColor(CsLabelColor)
        self.alkaliItem.moveBy(0, 40)

        self.statusItem = QtGui.QGraphicsTextItem("", self)
        self.statusItem.setDefaultTextColor(SlotLabelColor)
        self.statusItem.moveBy(0, 25)

        self.contrastItem = QtGui.QGraphicsTextItem("", self)
        self.contrastItem.setDefaultTextColor(SlotLabelColor)
        self.contrastItem.moveBy(10, 40)
        self.contrastItem.setTextWidth(30)


    def boundingRect(self):
        return self.bounds.adjusted(-5, -5, 5, 5)

    def labelFocusOut(self, ev):
        QtGui.QGraphicsTextItem.focusOutEvent(self.nameItem, ev)
        # Removes potential text selection remains
        # cursor = self.nameItem.textCursor()
        # cursor.clearSelection()
        # self.nameItem.setTextCursor(cursor)
        self.labelChanged()

    def labelKeyPress(self, ev):
        if ev.key() == QtCore.Qt.Key_Enter or ev.key() == QtCore.Qt.Key_Return:
            self.labelChanged()
            # After pressing Enter we want to exit the edit mode:
            self.nameItem.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
            self.nameItem.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        else:
            QtGui.QGraphicsTextItem.keyPressEvent(self.nameItem, ev)

    def labelChanged(self):
        newName = str(self.nameItem.toPlainText())
        # Deallocate the slot
        if newName == '':
            self.slot.removeCell()
        elif newName != self.slot.label:
            cell = self.slot.cell_manager.addCell(newName)
            self.slot.setCell(cell)
        ### re-center the label

    def enableSlot(self,update_table=True):
        if self.slot.slot_holder.is_wafer_holder:
            cell = self.slot.cell_manager.addCell(self.slot.slot_holder.wafer_id+self.slot.label,update_table=update_table,cell_template=self.slot.cell_template)
        else:
            cell = self.slot.cell_manager.addCell(self.slot.label,update_table=update_table)
        self.slot.setCell(cell,update_table=update_table)

    def update_labels(self):
        if self.slot.cell is None:
            self.nameItem.setDefaultTextColor(SlotLabelColor)
            self.nameItem.setPlainText(self.slot.label)
            self.alkaliItem.setPlainText('')
            self.statusItem.setPlainText('')
            self.contrastItem.setPlainText('')
        else:
            self.nameItem.setDefaultTextColor(CellLabelColor)
            self.nameItem.setPlainText(self.slot.cell.cell_id)
            self.alkaliItem.setPlainText(self.slot.cell.alkali)
            self.statusItem.setPlainText(self.slot.cell.status)
            if self.slot.cell.alkali == 'Cs':
                self.alkaliItem.setDefaultTextColor(CsLabelColor)
            else:
                self.alkaliItem.setDefaultTextColor(RbLabelColor)
        self.nameItem.setPos(self.bounds.width()/2. - self.nameItem.boundingRect().width()/2., 0)
        self.update()

    def update_contrast_label(self):
        contrast = self.slot.cell.contrast
        if contrast != -1:
            color_index = sorted([0, int(contrast), 99])[1]
            self.contrastItem.setDefaultTextColor(colors[color_index])
            self.contrastItem.setHtml('<div align="right">{:2.0f}</div>'.format(contrast))
        else:
            self.contrastItem.setPlainText('')

    def setPen(self, *args, **kwargs):
        self.pen = fn.mkPen(*args, **kwargs)
        self.update()

    def setBrush(self, brush):
        self.brush = brush
        self.update()

    def paint(self, p, *args):
        if self.slot.is_reference:
            p.setPen(self.reference_pen)
            p.drawRect(self.bounds)
        if self.isSelected():
            p.setPen(self.selectPen)
            p.setBrush(self.selectBrush)
        else:
            p.setPen(self.pen)
            if self.hovered:
                p.setBrush(self.hoverBrush)
            else:
                if self.slot.cell is None:
                    p.setBrush(self.brush)
                else:
                    p.setBrush(self.occupiedBrush)
        p.drawRect(self.bounds)

    def mousePressEvent(self, ev):
        ev.ignore()

    def mouseClickEvent(self, ev):
        if int(ev.button()) == int(QtCore.Qt.LeftButton):
            ev.accept()
            sel = self.isSelected()
            self.setSelected(True)
            if not sel and self.isSelected():
                self.update()

        elif int(ev.button()) == int(QtCore.Qt.RightButton):
            ev.accept()
            self.buildMenu()
            self.raiseContextMenu(ev)

    def mouseDragEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            ev.accept()

    def hoverEvent(self, ev):
        if not ev.isExit() and ev.acceptClicks(QtCore.Qt.LeftButton):
            ev.acceptDrags(QtCore.Qt.LeftButton)
            self.hovered = True
        else:
            self.hovered = False
        self.update()


    def itemChange(self, change, val):
        if change == self.ItemPositionHasChanged:
            pass
        return GraphicsObject.itemChange(self, change, val)

    def getMenu(self):
        return self.menu

    def raiseContextMenu(self, ev):
        # menu = self.scene().addParentContextMenus(self, self.getMenu(), ev)
        pos = ev.screenPos()
        self.menu.popup(QtCore.QPoint(pos.x(), pos.y()))

    def buildMenu(self):
        self.menu = QtGui.QMenu()
        self.menu.setTitle("Slot")
        if self.slot.cell is not None:
            self.menu.addAction("Switch Rb/Cs", self.slot.cell.toggleAlkali)
            self.menu.addAction("Remove cell", self.slot.removeCell)
            goto_menu = QtGui.QMenu('Go to',self.menu)
            #goto_menu.addAction("Origin", self.slot.moveTo)
            for device in self.slot.slot_holder.device_manager.devices:
                goto_menu.addAction(device.name+'>'+'origin',partial(self.slot.moveTo,[0.,0.],device.coords))
                for point in self.slot.cell.points:
                    action = goto_menu.addAction(device.name+'>'+point['label'],partial(self.slot.moveTo,point['coords'],device.coords))
            self.menu.addMenu(goto_menu)
            define_menu = QtGui.QMenu('Define pos.',self.menu)
            for device in self.slot.slot_holder.device_manager.devices:
                device_menu = QtGui.QMenu(device.name,define_menu)
                for point in self.slot.cell.points:
                    action = device_menu.addAction('from '+point['label'],
                                        partial(device.set_coords,
                                                self.slot.slot_holder.to_stage_coords(self.slot.coords+np.array(point['coords']))-np.array(self.slot.slot_holder.stage.position)))
                define_menu.addMenu(device_menu)
            self.menu.addMenu(define_menu)

        else:
            self.menu.addAction("Go to origin", self.slot.moveTo)
            self.menu.addAction("Enable slot", self.enableSlot)
        self.menu.addSeparator()
        if not self.slot.is_reference:
            self.menu.addAction("Set as reference", self.slot.setReference)
        else:
            self.menu.addAction("Delete reference", self.slot.delReference)
