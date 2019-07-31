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

class SerialReader(threading.Thread):

	running = False

	def __init__(self,heater):
		super(SerialReader, self).__init__()
		self.heater = heater

	def run(self):
		self.running = True
		while self.running:
			line = self.heater.ser.readline().decode()
			if line:
				# print(line[:-1])
				if line[0] == 'T': self.process_temperature_data(line)
				elif line[0] == 'H': self.process_heater_state_data(line)
				elif line[0] in ['S','P','I','D']:
					# print(line)
					self.heater.results[line[0]] = float(line[2:-2])
					# print(self.heater.results)
				elif line[0] == 'R':
					chan_idx, ratio = line[2:-2].split(' ')		
					self.heater.results['R'+str(chan_idx)] = float(ratio)
				else: print(line[:-2])
			time.sleep(0.01)

	def process_temperature_data(self,line):
		try:
			sensor_idx, temperature = line[1:-2].split(' ')			
			temperature = float(temperature)
			if temperature>-127:
				self.heater.temperatures.append([int(sensor_idx),time.time(),temperature])
		except ValueError:
			print("Parsing error: "+line)

	def process_heater_state_data(self,line):
		self.heater.output_intensities.append([time.time(),float(line[2:-2])])
		# self.heater._heater_state = not bool(line[2:-2])

class CellHolderHeater(pg.QtCore.QObject):

	def __init__(self,comPort='com6',sensor_number=9):
		self.ser_reader = None
		self.sensor_number = sensor_number
		self.temperatures = deque(maxlen=9000)
		self.output_intensities = deque(maxlen=1000)
		# _temperature = None
		self.results = {}
		self._heater_state = None
		self._setpoint = None
		self._p_gain = None
		self._i_gain = None
		self._d_gain = None
		super(CellHolderHeater,self).__init__()
		self.waiting = False
		try:
			self.ser = serial.Serial()
			self.ser.port = comPort
			self.ser.baudrate = 115200
			self.ser.setDTR(False) # This prevents the arduino from rebooting on connect
			self.ser.open()
			self.send("A?")
			# self.setpoint
			# self.p_gain
			# self.i_gain
		except serial.serialutil.SerialException:
			self.ser = None
			print("Could not connect to cell holder heater")
		else:
			pass

	def close(self):
		print("Del function called")
		self.stop_data_poller()
		print("Data poller stopped")
		if self.ser:
			self.ser.close()
		# if self.ser_reader:
		

	def send(self, command):
		self.ser.write((command+"\r\n").encode())

	def get_attrib(self,attrib):
		if attrib not in self.results:
			if self.ser_reader:
				self.send(attrib+"?")
				time.sleep(1.)
		try:
			return self.results[attrib]
		except KeyError as e:
			print(e)
			return None

	@property
	def setpoint(self):
		if self._setpoint is None: self._setpoint = self.get_attrib('S')
		return self._setpoint

	@property
	def p_gain(self):
		if self._p_gain is None: self._p_gain = self.get_attrib('P')
		print('P gain',self._p_gain)
		return self._p_gain

	@property
	def i_gain(self):
		if self._i_gain is None: self._i_gain = self.get_attrib('I')
		return self._i_gain

	@property
	def d_gain(self):
		if self._d_gain is None: self._d_gain = self.get_attrib('D')
		return self._d_gain

	@property
	def heater_state(self):
		return self._heater_state

	@setpoint.setter
	def setpoint(self,value):
		self._setpoint = float(value)
		self.send("S "+str(float(value)))

	@p_gain.setter
	def p_gain(self,value):
		self._p_gain = float(value)
		self.send("P "+str(float(value)))

	@i_gain.setter
	def i_gain(self,value):
		self._i_gain = float(value)
		self.send("I "+str(float(value)))

	@d_gain.setter
	def d_gain(self,value):
		self._d_gain = float(value)
		self.send("D "+str(float(value)))

	def get_ratio(self,channel):
		if "R"+str(channel) not in self.results:
			if self.ser_reader:
				self.send("R? "+str(channel))
				time.sleep(1.)
		try:
			return self.results["R"+str(channel)]
		except KeyError as e:
			print(e)
			return None

	def set_ratio(self,channel,ratio):
		self.send("R {:d} {:d}".format(channel,ratio))

	def start_data_poller(self):
		if not self.ser_reader:
			self.ser_reader = SerialReader(self)
			self.ser_reader.start()
			print("Data poller started")

	def stop_data_poller(self):
		self.ser_reader.running = False
		self.ser_reader.join()
		self.ser_reader = None

if __name__=='__main__':
	heater = CellHolderHeater()
	if heater.ser: heater.start_data_poller()
	app = QtGui.QApplication([])

	win = QtGui.QMainWindow()
	win.setWindowTitle("Wafer Heater")
	layout = pg.LayoutWidget()
	param_tree = ParameterTree()
	graph_layout_wgt = pg.GraphicsLayoutWidget()
	win.setCentralWidget(layout)

	layout.addWidget(param_tree,col=0)
	layout.addWidget(graph_layout_wgt,col=1)
	
	param_group = Parameter.create(name='params', type='group')
	setpoint_param = Parameter.create(name='Setpoint',type='float',value=heater.setpoint)
	p_gain_param = Parameter.create(name='P gain',type='float',value=heater.p_gain)
	i_gain_param = Parameter.create(name='I gain',type='float',value=heater.i_gain)
	d_gain_param = Parameter.create(name='D gain',type='float',value=heater.d_gain)
	heater_ratio_params = []
	heater_ratio_group = Parameter.create(name='Heater ratios', type='group')
	for i in range(9):
		heater_ratio_params.append(Parameter.create(name=str(i),type='int',value=heater.get_ratio(i)))
	heater_ratio_group.addChildren(heater_ratio_params)
	param_group.addChildren([setpoint_param,p_gain_param,i_gain_param,d_gain_param,heater_ratio_group])
	param_tree.setParameters(param_group, showTop=False)
	def change(param,changes):
		for param, change, data in changes:
			if param is setpoint_param: heater.setpoint = param.value()
			elif param is p_gain_param: heater.p_gain = param.value()
			elif param is i_gain_param: heater.i_gain = param.value()
			elif param is d_gain_param: heater.d_gain = param.value()
			elif param in heater_ratio_params: heater.set_ratio(int(param.name()),param.value())
	param_group.sigTreeStateChanged.connect(change)

	p1 = graph_layout_wgt.addPlot()
	p1.setLabel('left', "Temperature")
	n = heater.sensor_number
	colors = "wrgbcmy"
	curves = [p1.plot(pen=colors[i%len(colors)]) for i in range(n)]
	graph_layout_wgt.nextRow()
	p2 = graph_layout_wgt.addPlot()
	p2.setLabel('left', "Intensity")
	intensity_curve = p2.plot(pen='r')

	def update_intensiy_graph():
		global intensity_curve,heater
		data = np.array(heater.output_intensities)
		if len(data)>0:
			intensity_curve.setData(x=data[:,0]-data[0,0],y=data[:,1])

	def update_temperature_graph():
		global curves,heater
		for idx,curve in enumerate(curves):
			data = np.array(heater.temperatures)			
			if len(data)>0:
				data = data[data[:,0]==idx] # Select temperatures from sensor 0.
				if len(data)>0:
					x = data[:,1] - data[0,1]
					y = data[:,2]
					curve.setData(x=x,y=y)
					#labels[idx].setText(u"{} °C".format(y[-1]))
					#if idx == 0: setpoint_label.setText(u"{} °C / {} °C".format(y[-1],heater.setpoint))

	def update():		
		update_temperature_graph()
		update_intensiy_graph()

	timer = pg.QtCore.QTimer()
	timer.timeout.connect(update)
	timer.start(300)
	win.show()

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(pg.QtCore, 'PYQT_VERSION'):
        pg.QtGui.QApplication.instance().exec_()

    if heater.ser: heater.close()