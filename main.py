import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.dockarea import *
from pyqtgraph.parametertree import Parameter, ParameterTree
from tasks.autotaskpanel import AutoTaskPanel
from cell_manager import CellManager
from device_manager import DeviceManager
from slot_holder import SlotHolder
from map_layout import MapLayout

# Create application
app = QtGui.QApplication([])
app.setStyle("cleanlooks")
win = QtGui.QMainWindow()
win.app = app
win2 = QtGui.QMainWindow()
win2.app = app

from drivers.stage.apt_stage_ui import Stage_UI
from drivers.picoscope.pico_ui import Picoscope_UI
from drivers.camera.uc480dotnet_ui import UC480Cam_UI
from drivers.light.lightCtrl_ui import LightCtrl_UI
from drivers.laser_driver.np560b import NP560B
# Connect to devices
cm = CellManager()
dm = DeviceManager()

dm.stage = Stage_UI(x_serial = 45874656, y_serial = 45874425)
dm.picoscope = Picoscope_UI()
dm.camera = UC480Cam_UI()
dm.light = LightCtrl_UI(comPort='com5')
dm.ldd = NP560B()

dm.addDevice('Camera',coords=(0.0,0.0))
dm.addDevice('Activ',coords=(5.6,6.7))
dm.addDevice('Spectro',coords=(8.0,9.0))

###  Make wafer and cell holder ###
cell_holder = SlotHolder(cm, dm, stage=dm.stage, identiy="cell_holder", is_wafer_holder=False, xml_template = "cell_holder_template.xml")
cell_holder.rotated_by_default = True
wafer_holder = SlotHolder(cm, dm, stage=dm.stage, identiy="wafer_holder", xml_template = "wafer_template2.xml")

holders = [cell_holder,wafer_holder]

map_layout = MapLayout(dm.stage,holders,dm)

autotaskpanel = AutoTaskPanel(cm,dm)

# Set up the interface
area = DockArea()
area2 = DockArea()
win.setCentralWidget(area)
win2.setCentralWidget(area2)
win.resize(1260,900)
win.setWindowTitle('Activation setup')
win2.resize(1200,800)
win2.setWindowTitle('Pico/Camera')

controls_dock = Dock("Controls", size=(3,1))
poslist_dock = Dock("Position list", size=(3,1))
cell_hold_alloc_dock = Dock("Slot allocation (Cell holder)", size=(10,1))
wafer_alloc_dock = Dock("Slot allocation (Wafer holder)", size=(10,1))
map_dock = Dock("Map", size=(10,1))
pico_dock = Dock("Picoscope", size=(1,1))
cam_dock = Dock("Camera", size=(1,1))
area.addDock(poslist_dock, 'left')
area.addDock(controls_dock, 'above',poslist_dock)
area.addDock(map_dock, 'right')
area.addDock(cell_hold_alloc_dock, 'above', map_dock)
area.addDock(wafer_alloc_dock, 'above', cell_hold_alloc_dock)
area2.addDock(pico_dock)
area2.addDock(cam_dock,'right')

layout_wgt = pg.LayoutWidget()
p = Parameter.create(name='params', type='group')
p.addChildren([	cell_holder.param_group,
				wafer_holder.param_group,
				cm.param_group,
				dm.param_group,
				autotaskpanel.param_group])
t = ParameterTree()
t.setParameters(p, showTop=False)
layout_wgt.addWidget(dm.stage.layout_wgt, row=0, col=0)
layout_wgt.addWidget(dm.light.layout_wgt, row=1, col=0)
layout_wgt.addWidget(t, row=2, col=0)

poslist_dock.addWidget(cm.table)
cell_hold_alloc_dock.addWidget(cell_holder.view)
wafer_alloc_dock.addWidget(wafer_holder.view)
map_dock.addWidget(map_layout)
controls_dock.addWidget(layout_wgt)
pico_dock.addWidget(dm.picoscope.plotLayout)
cam_dock.addWidget(dm.camera.widget)

win.show()
win2.show()

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
	import sys
	if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
		QtGui.QApplication.instance().exec_()
		cell_holder.saveAlignement()
		wafer_holder.saveAlignement()