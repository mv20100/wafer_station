import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree
from pyqtgraph.Qt import QtCore, QtGui
import time

class UpdateThread(QtCore.QThread):

	newStageData = QtCore.Signal(object)

	def __init__(self,stage):
		super(UpdateThread, self).__init__()
		self.stage = stage
		self.running = True

	def run(self):
		while self.running:
			if self.stage.x_jog_dir != 0:
				self.stage.x_position += self.stage.x_jog_dir
				self.newStageData.emit([self.stage.x_position, self.stage.y_position])
			if self.stage.y_jog_dir != 0:
				self.stage.y_position += self.stage.y_jog_dir
				self.newStageData.emit([self.stage.x_position, self.stage.y_position])
			time.sleep(0.050)

class VirtualStage(QtCore.QObject):

	x_position = 0.
	y_position = 0.
	x_jog_dir = 0.
	y_jog_dir = 0.
	step_size = 0.5

	def __init__(self):
		QtCore.QObject.__init__(self)
		self.param_group = pTypes.GroupParameter(name = "VirtualStage")
		self.x_position_param = Parameter.create(name='x_position',
												type='float',
												value=self.x_position,
												readonly=True,
												decimals=3)
		self.y_position_param = Parameter.create(name='y_position',
												type='float',
												value=self.y_position,
												readonly=True)
		self.param_group.addChildren([self.x_position_param,self.y_position_param])

		self.update_thread = UpdateThread(self)
		self.update_thread.newStageData.connect(self.update_position_param)
		self.update_thread.start()

	@property
	def position(self):
		return [self.x_position,self.y_position]

	def jog_x(self,jogDir):
		if jogDir>0: self.x_jog_dir = -1. * self.step_size
		if jogDir<0: self.x_jog_dir = 1. * self.step_size

	def jog_y(self,jogDir):
		if jogDir>0: self.y_jog_dir = 1. * self.step_size
		if jogDir<0: self.y_jog_dir = -1. * self.step_size

	def stop_x(self):
		self.x_jog_dir = 0

	def stop_y(self):
		self.y_jog_dir = 0

	def update_position_param(self,position):
		self.x_position_param.setValue(self.x_position)
		self.y_position_param.setValue(self.y_position)
