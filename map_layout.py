import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
from pyqtgraph.graphicsItems.PlotItem import PlotItem


class MapLayout(pg.GraphicsLayoutWidget):

	# lastClicked = []

	def __init__(self,stage,holders,deviceManager):
		pg.GraphicsLayoutWidget.__init__(self)
		self.stage = stage
		self.holders = holders
		self.deviceManager = deviceManager

		for holder in holders:
			holder.reference_slots_updated.connect(self.draw_holder_cells)

		# self.w = self.addViewBox()
		# self.w.invertX(True)
		# self.w.setAspectLocked(True)
		# vb = pg.ViewBox(lockAspect=True, invertY=True)
		plot = self.addPlot()
		#self.plt = PlotItem()
		plot.setAspectLocked(lock=True, ratio=1)
		plot.showGrid(True,True,0.7)
		#self.addLayout(plot)

		#self.w = self.plt.vb
		# self.p = PlotItem(invertY=True)
		self.cell_scatter = pg.ScatterPlotItem(size=10, pen=pg.mkPen('w'), pxMode=True)
		plot.addItem(self.cell_scatter)
		# self.w.showGrid(True,True,0.7)
		# self.addItem(self.p)

		# self.scatter_plot = pg.ScatterPlotItem()
		# self.addItem(self.scatter_plot)
		#self.path_graph = pg.GraphItem()
		#self.w.addItem(self.path_graph)
		# self.cell_scatter.sigClicked.connect(self.clicked)
		# self.label_list = []
		for dev in self.deviceManager.devices:
			dev.makeMapLayoutItems(plot)
		#self.cam_txt.setParentItem(self.cam_arrow)
		# self.arrow2 = pg.ArrowItem(pos=(0, 0), angle=+90,brush=pg.mkBrush('r'))
		# self.arrow3 = pg.ArrowItem(pos=(0, 0), angle=-90,brush=pg.mkBrush('g'))
		
		# self.w.addItem(self.arrow2)
		# self.w.addItem(self.arrow3)
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.update_arrow_position)
		self.timer.start(100)
		#self.stage.update_thread.newStageData.connect(self.update_arrow_position)

		self.draw_holder_cells()

	# def keyPressEvent(self, ev):
	# 	key = ev.key()
	# 	if key in [QtCore.Qt.Key_Up,QtCore.Qt.Key_Down,QtCore.Qt.Key_Left,QtCore.Qt.Key_Right]:
	# 		ev.accept()
	# 		if key == QtCore.Qt.Key_Up: self.stage.jog_y(1)
	# 		elif key == QtCore.Qt.Key_Down: self.stage.jog_y(-1)
	# 		elif key == QtCore.Qt.Key_Right: self.stage.jog_x(1)
	# 		elif key == QtCore.Qt.Key_Left: self.stage.jog_x(-1)
	# 	else: ev.ignore()

	# def keyPressEvent(self, event):
	# 	key = event.key()
	# 	if not event.isAutoRepeat():
	# 		if key == QtCore.Qt.Key_Left: 		self.stage.jog_x(1)
	# 		elif key == QtCore.Qt.Key_Right:	self.stage.jog_x(-1)
	# 		elif key == QtCore.Qt.Key_Up: 		self.stage.jog_y(1)
	# 		elif key == QtCore.Qt.Key_Down:		self.stage.jog_y(-1)

	# def keyReleaseEvent(self,event):
	# 	key = event.key()
	# 	if not event.isAutoRepeat():
	# 		if key == QtCore.Qt.Key_Left:		self.stage.stop_x()
	# 		elif key == QtCore.Qt.Key_Right:	self.stage.stop_x()
	# 		elif key == QtCore.Qt.Key_Up:		self.stage.stop_y()
	# 		elif key == QtCore.Qt.Key_Down:		self.stage.stop_y()

	def update_arrow_position(self):
		for dev in self.deviceManager.devices:
			dev.updateMapLayoutItemsPosition(self.stage.position)

	def draw_holder_cells(self):
		spots = []
		for holder in self.holders:
			# spots = [{'pos': position, 'data': row, 'brush':'c', 'symbol': 's', 'size': 20}]
			if holder.transform_matrix is not None:
				for slot in holder.slots:
					if slot.is_reference: brush = 'r'
					else: brush = 'c'
					spots.append({'pos':slot.stage_coords, 'brush':brush, 'symbol': 's', 'size': 15})
		self.cell_scatter.setData(spots)

	# def update_cell_positions(self,tableRows):
	# 	self.cell_scatter.clear()
	# 	for item in self.label_list: #Clear the text labels
	# 		self.w.removeItem(item)
	# 	del self.label_list[:]
	# 	for row in tableRows:
	# 		if len(row)>=2:
	# 			cellName = row[0]
	# 			position = row[1]
	# 			spots = [{'pos': position, 'data': row, 'brush':'c', 'symbol': 's', 'size': 20}]
	# 			self.cell_scatter.addPoints(spots)
	# 			text = pg.TextItem(cellName, anchor=(0.5, -0.5))
	# 			self.w.addItem(text)
	# 			self.label_list.append(text)
	# 			text.setPos(*position)

	# def update_path(self,path):
	# 	path = np.array(path)
	# 	adj = np.array( [ [ i,  i+1 ] for i in range(len(path)-1) ] )
	# 	self.path_graph.setData(pos=path,pen="w", adj=adj)

	# def clicked(self,plot,points):
	# 	for p in self.lastClicked:
	# 		p.resetPen()
	# 	print("clicked points", points)
	# 	for p in points:
	# 		p.setPen('b', width=2)
	# 	self.lastClicked = points
