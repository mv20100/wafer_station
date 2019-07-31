if __name__ == '__main__':
	app = QtGui.QApplication([])
from pyqtgraph.Qt import QtCore, QtGui
from .uc480dotnet import UC480Cam
import numpy as np
import pyqtgraph as pg


class UC480Cam_UI(UC480Cam):

	def __init__(self):
		UC480Cam.__init__(self)
		self.widget = pg.GraphicsLayoutWidget()
		view = self.widget.addViewBox(invertX=True,invertY=True)
		view.setAspectLocked(True)
		self.img = pg.ImageItem(border='w')
		self.img.setLevels([0,254]*3,update=False)
		view.addItem(self.img)
		view.setRange(QtCore.QRectF(0, 0, 1280, 1024))
		line = QtGui.QGraphicsLineItem(int(1280/2), 0, int(1280/2), 1024)
		line2 = QtGui.QGraphicsLineItem(0, int(1024/2), 1280, int(1024/2))
		diameter = 600
		circ = QtGui.QGraphicsEllipseItem(int(1280/2-diameter/2),int(1024/2-diameter/2),diameter,diameter)
		line.setPen(pg.mkPen(0, 254, 254))
		line2.setPen(pg.mkPen(0, 254, 254))
		circ.setPen(pg.mkPen(0, 254, 254))
		view.addItem(line)
		view.addItem(line2)
		view.addItem(circ)
		self.pixelclock = 18
		self.exposure = 150
		self.cam.Gain.Hardware.Factor.SetMaster(427)
		self.cam.Gain.Hardware.Factor.SetBlue(310)
		self.cam.Gain.Hardware.Factor.SetGreen(180)
		self.cam.Gain.Hardware.Factor.SetRed(100)

		self.start()

		def updateData():
			if self.imageData is not None:
				self.img.setImage(self.imageData.reshape(1024,1280,3).transpose(1,0,2),autoLevels=False,levels=(0,255))
			QtCore.QTimer.singleShot(100, updateData)

		updateData()

	## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
	import sys
	camera = UC480Cam_UI()
	camera.widget.show()

	if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
		QtGui.QApplication.instance().exec_()
		camera.stop()