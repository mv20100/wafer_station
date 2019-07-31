from .np560b import NP560B
from PyQt5.QtCore import Qt
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg

class NP560B_UI(NP560B):
	def __init__(self,*args,**kwargs):
		super(NP560B_UI, self).__init__(*args,**kwargs)
		self.layout_wgt = pg.LayoutWidget()
		



if __name__ == '__main__':
	app = QtGui.QApplication([])
	ldd = NP560B_UI(dev_key='560B 124207013')
	win = QtGui.QMainWindow()
	win.setWindowTitle('Laser')
	win.setCentralWidget(ldd.layout_wgt)
	win.resize(200,200)
	win.show()
	app.exec_()