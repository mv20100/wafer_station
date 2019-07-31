import sys
from wafer_holder_control_ui import CellHolderHeater_UI
from pyqtgraph.Qt import QtCore, QtGui

app = QtGui.QApplication([])
heater = CellHolderHeater_UI(comPort='com7')
win = QtGui.QMainWindow()
win.setWindowTitle("Cell Holder Heater")
win.setCentralWidget(heater.layout)
win.show()

if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
	QtGui.QApplication.instance().exec_()

if heater.ser: heater.close()