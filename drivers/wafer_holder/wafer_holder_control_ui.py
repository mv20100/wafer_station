# -*- coding: utf-8 -*-

import time, serial, queue
import threading
# from utils.misc import Buffer
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.parametertree import Parameter, ParameterTree
from collections import deque
import numpy as np
from functools import partial
from wafer_holder_control import CellHolderHeater

class CellHolderHeater_UI(CellHolderHeater):

	def __init__(self,*args,**kwargs):
		CellHolderHeater.__init__(self,*args,**kwargs)
		if self.ser: self.start_data_poller()

		self.layout = pg.LayoutWidget()
		param_tree = ParameterTree()
		graph_layout_wgt = pg.GraphicsLayoutWidget()
		

		self.layout.addWidget(param_tree,col=0)
		self.layout.addWidget(graph_layout_wgt,col=1)
		
		param_group = Parameter.create(name='params', type='group')
		setpoint_param = Parameter.create(name='Setpoint',type='float',value=self.setpoint)
		p_gain_param = Parameter.create(name='P gain',type='float',value=self.p_gain)
		i_gain_param = Parameter.create(name='I gain',type='float',value=self.i_gain)
		d_gain_param = Parameter.create(name='D gain',type='float',value=self.d_gain)
		heater_ratio_params = []
		heater_ratio_group = Parameter.create(name='Heater ratios', type='group')
		for i in range(9):
			heater_ratio_params.append(Parameter.create(name=str(i),type='int',value=self.get_ratio(i)))
		heater_ratio_group.addChildren(heater_ratio_params)
		param_group.addChildren([setpoint_param,p_gain_param,i_gain_param,d_gain_param,heater_ratio_group])
		param_tree.setParameters(param_group, showTop=False)
		def change(param,changes):
			for param, change, data in changes:
				if param is setpoint_param: self.setpoint = param.value()
				elif param is p_gain_param: self.p_gain = param.value()
				elif param is i_gain_param: self.i_gain = param.value()
				elif param is d_gain_param: self.d_gain = param.value()
				elif param in heater_ratio_params: self.set_ratio(int(param.name()),param.value())
		param_group.sigTreeStateChanged.connect(change)

		p1 = graph_layout_wgt.addPlot()
		p1.setLabel('left', "Temperature")
		n = self.sensor_number
		colors = "wrgbcmy"
		p1.addLegend()
		self.curves = []
		self.texts = []
		for i in range(n):
			self.curves.append(p1.plot(pen=(i,n*1.3),name=f'T{i}'))
			text = pg.TextItem(text=f'T{i}')
			self.texts.append(text)
			p1.addItem(text)
		graph_layout_wgt.nextRow()
		p2 = graph_layout_wgt.addPlot()
		p2.setLabel('left', "Intensity")
		self.intensity_curve = p2.plot(pen='r')

		self.timer = pg.QtCore.QTimer()
		self.timer.timeout.connect(self.update)
		self.timer.start(300)

	def update_intensiy_graph(self):
		data = np.array(self.output_intensities)
		if len(data)>0:
			self.intensity_curve.setData(x=data[:,0]-data[0,0],y=data[:,1])

	def update_temperature_graph(self):
		for idx,curve in enumerate(self.curves):
			data = np.array(self.temperatures)			
			if len(data)>0:
				data = data[data[:,0]==idx] # Select temperatures from sensor 0.
				if len(data)>0:
					x = data[:,1] - data[0,1]
					y = data[:,2]
					curve.setData(x=x,y=y)
					self.texts[idx].setPos(x[-1], y[-1])
					#labels[idx].setText(u"{} °C".format(y[-1]))
					#if idx == 0: setpoint_label.setText(u"{} °C / {} °C".format(y[-1],heater.setpoint))

	def update(self):		
		self.update_temperature_graph()
		self.update_intensiy_graph()
	

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
	import sys
	app = QtGui.QApplication([])
	heater1 = CellHolderHeater_UI(comPort='com6')
	heater2 = CellHolderHeater_UI(comPort='com7')
	win = QtGui.QMainWindow()
	win2 = QtGui.QMainWindow()
	win.setWindowTitle("Wafer Heater")
	win.setCentralWidget(heater1.layout)
	win2.setWindowTitle("Holder Heater")
	win2.setCentralWidget(heater2.layout)
	win.show()
	win2.show()

	if (sys.flags.interactive != 1) or not hasattr(pg.QtCore, 'PYQT_VERSION'):
		pg.QtGui.QApplication.instance().exec_()

	if heater1.ser: heater1.close()
	if heater2.ser: heater2.close()