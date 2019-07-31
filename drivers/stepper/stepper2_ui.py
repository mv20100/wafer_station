from stepper2 import Stepper
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import threading, time

class Stepper_UI(Stepper):

	cs_position = 400
	rb_position = 0
	timer = None

	def __init__(self,**kwargs):
		super(Stepper_UI, self).__init__(**kwargs)
		self.layout_wgt = pg.LayoutWidget()

		self.pos_lbl = QtGui.QLabel(str(self.position))

		self.setpoint_spinBox = QtGui.QSpinBox()
		self.setpoint_spinBox.setSingleStep(1)
		self.setpoint_spinBox.setRange(-4000,4000)
		self.set_cs_pos_btn = QtGui.QPushButton('Set')
		self.set_rb_pos_btn = QtGui.QPushButton('Set')
		self.go_cs_pos_btn = QtGui.QPushButton('Go')
		self.go_rb_pos_btn = QtGui.QPushButton('Go')

		self.layout_wgt.addWidget(QtGui.QLabel('Position'), row=0, col=0, colspan=2)
		self.layout_wgt.addWidget(self.pos_lbl, row=0, col=2)
		self.layout_wgt.addWidget(QtGui.QLabel('Setpoint'), row=1, col=0, colspan=2)
		self.layout_wgt.addWidget(self.setpoint_spinBox, row=1, col=2)
		self.layout_wgt.addWidget(QtGui.QLabel('Cs'), row=2, col=0)
		self.layout_wgt.addWidget(self.set_cs_pos_btn, row=2, col=1)
		self.layout_wgt.addWidget(self.go_cs_pos_btn, row=2, col=2)
		self.layout_wgt.addWidget(QtGui.QLabel('Rb'), row=3, col=0)
		self.layout_wgt.addWidget(self.set_rb_pos_btn, row=3, col=1)
		self.layout_wgt.addWidget(self.go_rb_pos_btn, row=3, col=2)

		self.setpoint_spinBox.valueChanged.connect(self.update_setpoint)
		self.set_cs_pos_btn.clicked.connect(self.set_cs_position)
		self.set_rb_pos_btn.clicked.connect(self.set_rb_position)
		self.go_cs_pos_btn.clicked.connect(self.goto_cs_position)
		self.go_rb_pos_btn.clicked.connect(self.goto_rb_position)

		self.start_live_update()
		self.disable_controls()
		threading.Thread(target=self.initialize).start()
		self.stop_live_update()

	def start_live_update(self):
		if self.timer is None or not self.timer.isActive():
			self.timer = QtCore.QTimer()
			self.timer.timeout.connect(self.update_position_label)
			self.timer.start(500)
			# print("Starting live position label update")

	def stop_live_update(self):
		if self.timer is not None:
			self.timer.stop()
			# print("Stopping live position label update")

	def update_setpoint(self):
		self.position = self.setpoint_spinBox.value()
		self.start_live_update()

	def set_cs_position(self):
		self.cs_position = self.setpoint

	def set_rb_position(self):
		self.rb_position = self.setpoint

	def goto_cs_position(self):
		self.position = self.cs_position
		self.start_live_update()

	def goto_rb_position(self):
		self.position = self.rb_position
		self.start_live_update()

	def update_position_label(self):
		current_position = self.position
		self.pos_lbl.setText(str(current_position))
		if self.setpoint == current_position: self.stop_live_update()

	def initialize(self):
		print("Stepper going to Rb position")
		self.position = self.rb_position
		time.sleep(6)
		print("Stepper going to Cs position")
		self.position = self.cs_position
		time.sleep(6)
		print("Stepper initialized")
		self.enable_controls()

	def disable_controls(self):
		self.go_cs_pos_btn.setEnabled(False)
		self.go_rb_pos_btn.setEnabled(False)
		self.setpoint_spinBox.setEnabled(False)

	def enable_controls(self):
		self.go_cs_pos_btn.setEnabled(True)
		self.go_rb_pos_btn.setEnabled(True)
		self.setpoint_spinBox.setEnabled(True)

if __name__ == '__main__':
	app = QtGui.QApplication([])
	stepper = Stepper_UI(comPort='com4')
	win = QtGui.QMainWindow()
	win.setWindowTitle('Stepper control')
	win.setCentralWidget(stepper.layout_wgt)
	win.resize(200,200)
	win.show()
	app.exec_()
	stepper.close()