# -*- coding: utf-8 -*-

from PyQt5 import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
from .pico import Picoscope
import peakutils, time
from collections import deque

class Picoscope_UI(Picoscope):

	show_raw_waveforms = False
	signal_threshold = 0.005

	def __init__(self):
		Picoscope.__init__(self)
		self.initialize()

		self.plotLayout = pg.GraphicsLayoutWidget()
		self.plot1 = self.plotLayout.addPlot()
		self.plotLayout.nextRow()
		self.plot2 = self.plotLayout.addPlot()
		self.plot2.addLegend()
		self.plotLayout.nextRow()
		self.plot3 = self.plotLayout.addPlot()
		self.plot3.addLegend()
		self.plotLayout.nextRow()
		self.plot4 = self.plotLayout.addPlot()
		self.plot4.addLegend()
		self.plotLayout.ci.layout.setRowStretchFactor(0, 0)
		self.plotLayout.ci.layout.setRowStretchFactor(1, 2)
		self.plotLayout.ci.layout.setRowStretchFactor(2, 2)
		self.plotLayout.ci.layout.setRowStretchFactor(3, 3)

		yellow = [255, 255,0]
		green = [0, 255, 0]
		cyan = [0, 255, 255]
		red = [255, 0, 0]
		magenta = [255, 0, 255]
		white = [255, 255, 255]

		self.contrast = None

		self.curve_dataC = self.plot1.plot(pen=pg.mkPen(red+[50]))
		self.curve_meanC = self.plot1.plot(pen=pg.mkPen(red+[255]),name='Ramp')

		self.curve_dataA = self.plot2.plot(pen=pg.mkPen(yellow+[50]))
		self.curve_meanA = self.plot2.plot(pen=pg.mkPen(yellow+[255]),name='Cs ref')
		
		self.curve_dataD = self.plot3.plot(pen=pg.mkPen(green+[50]))
		self.curve_meanD = self.plot3.plot(pen=pg.mkPen(green+[255]),name='Rb ref')

		self.curve_dataB = self.plot4.plot(pen=pg.mkPen(cyan+[50]))
		self.curve_meanB = self.plot4.plot(pen=pg.mkPen(cyan+[255]),name='Microcell')
		self.curve_baseline = self.plot4.plot(pen=pg.mkPen(red+[50]))
		self.curve_peak = self.plot4.plot(pen=pg.mkPen(magenta+[100]))
		self.curve_fit = self.plot4.plot(pen=pg.mkPen(red+[255]))
		self.curve_fit_data = self.plot4.plot(pen=pg.mkPen(magenta+[255]))
		self.curve_fit_init = self.plot4.plot(pen=pg.mkPen(yellow+[128]))
		self.text = pg.TextItem("?", anchor=(0.5, 1.0))
		self.plot4.addItem(self.text)
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.update)
		self.timer.start(50)

		self.timer2 = QtCore.QTimer()
		self.timer2.timeout.connect(self.update_measurements)
		self.timer2.start(200)

	def update(self):
		
		Picoscope.update(self)
		self.curve_dataB.setData(self.x, self.dataB[self.ptr,:])
		if self.show_raw_waveforms:
			self.curve_dataA.setData(self.x, self.dataA[self.ptr,:])
			self.curve_dataC.setData(self.x, self.dataC[self.ptr,:])
			self.curve_dataD.setData(self.x, self.dataD[self.ptr,:])
		self.curve_meanA.setData(self.x, self.meanA)
		self.curve_meanB.setData(self.x, self.meanB)
		self.curve_meanC.setData(self.x, self.meanC)
		self.curve_meanD.setData(self.x, self.meanD)

	def update_measurements(self):
		x, _, y, _, _ = self.get_averaged_data(clear=False)
		y2 = np.mean(y[-10:])
		y1 = np.mean(y[:10])
		x2 = x[-1]
		x1 = x[0]
		baseline = (y2-y1)/(x2-x1) * x + y1
		mean_signal = np.mean(baseline)
		arg_min = np.argmin(y-baseline)
		self.text.setPos(x[arg_min],baseline[arg_min])
		if mean_signal>self.signal_threshold:
			self.contrast = (baseline[arg_min]-y[arg_min])/baseline[arg_min]
		else: self.contrast = 0.0
		self.text.setText('{:.1f} %'.format(self.contrast*100.))
		self.curve_baseline.setData(x, baseline)
		self.curve_peak.setData([x[arg_min],x[arg_min]],[baseline[arg_min],y[arg_min]])

	def get_contrast(self,clear=True):
		if clear: self.clear()
		return self.contrast

if __name__ == '__main__':
	app = QtGui.QApplication([])
	pico = Picoscope_UI()
	win = QtGui.QMainWindow()
	win.setWindowTitle('Picoscope')
	win.setCentralWidget(pico.plotLayout)
	win.show()
	app.exec_()