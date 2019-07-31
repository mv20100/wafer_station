from PyQt5.QtCore import Qt
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
if __name__ == '__main__':
	app = QtGui.QApplication([])
from .thor_lts import Stage

class Stage_UI(Stage,QtCore.QObject):

	def __init__(self,**kwargs):
		super(Stage_UI, self).__init__(**kwargs)
		QtCore.QObject.__init__(self)
		self.timer = None
		self.layout_wgt = pg.LayoutWidget()
		self.pos_lbl = QtGui.QLabel('Position')
		self.status_lbl = QtGui.QLabel('Status')
		self.maxspeed_lbl = QtGui.QLabel('Max speed')
		self.state_lbl = QtGui.QLabel('State')
		self.jog_left_btn = QtGui.QPushButton('Jog Left')
		self.jog_right_btn = QtGui.QPushButton('Jog Right')
		self.jog_up_btn = QtGui.QPushButton('Jog Up')
		self.jog_down_btn = QtGui.QPushButton('Jog Down')
		self.test_btn = QtGui.QPushButton('Reset connection')
		self.layout_wgt.addWidget(self.jog_up_btn, row=0, col=1, colspan=2)
		self.layout_wgt.addWidget(self.jog_left_btn, row=1, col=0, colspan=2)
		self.layout_wgt.addWidget(self.jog_right_btn, row=1, col=2, colspan=2)
		self.layout_wgt.addWidget(self.jog_down_btn, row=2, col=1, colspan=2)
		self.layout_wgt.addWidget(self.pos_lbl, row=3, col=0, colspan=4)
		self.layout_wgt.addWidget(self.status_lbl, row=4, col=0, colspan=4)
		self.layout_wgt.addWidget(self.maxspeed_lbl, row=5, col=0, colspan=4)		
		self.layout_wgt.addWidget(self.state_lbl, row=6, col=0, colspan=4)		
		self.layout_wgt.addWidget(self.test_btn, row=7, col=0, colspan=2)		
		self.jog_left_btn.pressed.connect(self.jog_left)
		self.jog_right_btn.pressed.connect(self.jog_right)
		self.jog_left_btn.released.connect(self.stop_left_right)
		self.jog_right_btn.released.connect(self.stop_left_right)
		self.jog_up_btn.pressed.connect(self.jog_up)
		self.jog_down_btn.pressed.connect(self.jog_down)
		self.jog_up_btn.released.connect(self.stop_up_down)
		self.jog_down_btn.released.connect(self.stop_up_down)
		self.test_btn.clicked.connect(self.test)
		self.start_live_update()
		#if not self.is_homed: self.popup_home_request()

	def start_live_update(self):
		if self.timer is None or not self.timer.isActive():
			self.timer = QtCore.QTimer()
			self.timer.timeout.connect(self.update_status_label)
			self.timer.start(50)

	def stop_live_update(self):
		if self.timer is not None:
			self.timer.stop()

	def update_status_label(self):
		self.pos_lbl.setText("{0[0]:.3f}, {0[1]:.3f}".format(self.position))
		self.status_lbl.setText("Homed: {},{}".format(self.x_lts.is_homed,self.y_lts.is_homed))
		self.maxspeed_lbl.setText("Max vel.: {},{}".format(self.x_lts.max_velocity,self.y_lts.max_velocity))
		self.state_lbl.setText("State: {},{}".format(self.x_lts.lts.State,self.y_lts.lts.State))
		#self.new_position.emit(position)

	def jog_left(self):
		try: self.x_lts.lts.MoveJog(1,0)
		except Exception as e: print(e)

	def jog_right(self):
		try: self.x_lts.lts.MoveJog(2,0)
		except Exception as e: print(e)

	def stop_left_right(self):
		try: self.x_lts.lts.Stop(0)
		except Exception as e: print(e)

	def jog_up(self):
		try: self.y_lts.lts.MoveJog(1,0)
		except Exception as e: print(e)

	def jog_down(self):
		try: self.y_lts.lts.MoveJog(2,0)
		except Exception as e: print(e)

	def stop_up_down(self):
		try: self.y_lts.lts.Stop(0)
		except Exception as e: print(e)

	def test(self):
		self.x_lts.lts.ResetConnection(self.x_lts.serial)
		self.y_lts.lts.ResetConnection(self.y_lts.serial)
		self.x_lts.lts.StartPolling(250)
		self.y_lts.lts.StartPolling(250)
	# def popup_home_request(self):
	# 	msgBox = QtGui.QMessageBox()
	# 	msgBox.setText("The staged is not homed, do you want to home it now?")
	# 	msgBox.setStandardButtons(QtGui.QMessageBox.No | QtGui.QMessageBox.Yes)
	# 	msgBox.setDefaultButton(QtGui.QMessageBox.No)
	# 	ret = msgBox.exec_()
	# 	if ret == QtGui.QMessageBox.Yes:
	# 		self.moveHome(wait=False)

if __name__ == '__main__':
	stage = Stage_UI(x_serial = '45874656', y_serial = '45874425')
	win = QtGui.QMainWindow()
	win.setWindowTitle('Stage control')
	win.setCentralWidget(stage.layout_wgt)
	win.resize(200,200)
	win.show()
	app.exec_()