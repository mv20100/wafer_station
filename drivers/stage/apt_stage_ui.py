from PyQt5.QtCore import Qt
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
if __name__ == '__main__':
	app = QtGui.QApplication([])
from .apt_stage import Stage

class JoystickButton(QtGui.QPushButton):
	sigStateChanged = QtCore.Signal(object, object)  ## self, state
    
	def __init__(self, stage, parent=None):
		QtGui.QPushButton.__init__(self, parent)
		self.stage = stage
		self.radius = 200
		self.setCheckable(True)
		self.state = None
		self.setState(0,0)
		self.setFixedWidth(50)
		self.setFixedHeight(50)        

	def mousePressEvent(self, ev):
		self.setChecked(True)
		self.pressPos = ev.pos()
		ev.accept()

	def mouseMoveEvent(self, ev):
		dif = ev.pos()-self.pressPos
		self.setState(dif.x(), -dif.y())

	def mouseReleaseEvent(self, ev):
		self.setChecked(False)
		self.setState(0,0)

	def wheelEvent(self, ev):
		ev.accept()

	def doubleClickEvent(self, ev):
		ev.accept()

	def getState(self):
		return self.state

	def setState(self, *xy):
		xy = list(xy)
		d = (xy[0]**2 + xy[1]**2)**0.5
		nxy = [0,0]
		for i in [0,1]:
			if xy[i] == 0: nxy[i] = 0
			else: nxy[i] = xy[i]/d

		if d > self.radius: d = self.radius
		d = (d/self.radius)**2
		xy = [nxy[0]*d, nxy[1]*d]
		w2 = self.width()/2.
		h2 = self.height()/2
		self.spotPos = QtCore.QPoint(w2*(1+xy[0]), h2*(1-xy[1]))
		self.update()
		if self.state == xy: return		
		self.state = xy
		self.sigStateChanged.emit(self, self.state)
		if xy[0] == 0:
			self.stage.x_lts.stop_profiled()
			self.stage.x_lts.reset_velocity()
		else:
			self.stage.x_lts.set_velocity(abs(xy[0]))
			self.stage.x_lts.move_velocity(int(xy[0]>0)+1)
		if xy[1] == 0:
			self.stage.y_lts.stop_profiled()
			self.stage.y_lts.reset_velocity()
		else:
			self.stage.y_lts.set_velocity(abs(xy[1]))
			self.stage.y_lts.move_velocity(int(xy[1]<0)+1)

	def paintEvent(self, ev):
		QtGui.QPushButton.paintEvent(self, ev)
		p = QtGui.QPainter(self)
		p.setBrush(QtGui.QBrush(QtGui.QColor(0,0,0)))
		p.drawEllipse(self.spotPos.x()-3,self.spotPos.y()-3,6,6)

	def resizeEvent(self, ev):
		self.setState(*self.state)
		QtGui.QPushButton.resizeEvent(self, ev)

class Stage_UI(Stage,QtCore.QObject):

	def __init__(self,*args,**kwargs):
		super(Stage_UI, self).__init__(*args,**kwargs)
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
		self.load_pos_btn = QtGui.QPushButton('Load')
		self.jb = JoystickButton(self)
		self.jb.setFixedWidth(30)
		self.jb.setFixedHeight(30)
		self.layout_wgt.addWidget(self.jog_up_btn, row=0, col=1, colspan=2)
		self.layout_wgt.addWidget(self.jog_left_btn, row=1, col=0, colspan=2)
		self.layout_wgt.addWidget(self.jog_right_btn, row=1, col=2, colspan=2)
		self.layout_wgt.addWidget(self.jog_down_btn, row=2, col=1, colspan=2)
		self.layout_wgt.addWidget(self.pos_lbl, row=3, col=0, colspan=4)
		self.layout_wgt.addWidget(self.status_lbl, row=4, col=0, colspan=4)
		self.layout_wgt.addWidget(self.state_lbl, row=5, col=0, colspan=4)		
		self.layout_wgt.addWidget(self.jb, row=6, col=0, colspan=2)
		self.layout_wgt.addWidget(self.load_pos_btn, row=6, col=2, colspan=2)

		self.jog_left_btn.pressed.connect(self.jog_left)
		self.jog_right_btn.pressed.connect(self.jog_right)
		self.jog_left_btn.released.connect(self.stop_left_right)
		self.jog_right_btn.released.connect(self.stop_left_right)
		self.jog_up_btn.pressed.connect(self.jog_up)
		self.jog_down_btn.pressed.connect(self.jog_down)
		self.jog_up_btn.released.connect(self.stop_up_down)
		self.jog_down_btn.released.connect(self.stop_up_down)
		self.load_pos_btn.pressed.connect(self.goto_load_pos)
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
		self.status_lbl.setText("Homed: {},{}".format(self.x_lts.has_homing_been_completed,self.y_lts.has_homing_been_completed))
		self.state_lbl.setText("Settled: {},{}".format(self.x_lts.is_settled,self.y_lts.is_settled))
		#self.new_position.emit(position)

	def goto_load_pos(self):
		self.move_to([99, 242],wait=False)

	def jog_left(self):
		try: self.x_lts.move_velocity(1)
		except Exception as e: print(e)

	def jog_right(self):
		try: self.x_lts.move_velocity(2)
		except Exception as e: print(e)

	def stop_left_right(self):
		try: self.x_lts.stop_profiled()
		except Exception as e: print(e)

	def jog_up(self):
		try: self.y_lts.move_velocity(1)
		except Exception as e: print(e)

	def jog_down(self):
		try: self.y_lts.move_velocity(2)
		except Exception as e: print(e)

	def stop_up_down(self):
		try: self.y_lts.stop_profiled()
		except Exception as e: print(e)


if __name__ == '__main__':
	stage = Stage_UI(x_serial = 45874656, y_serial = 45874425)
	win = QtGui.QMainWindow()
	win.setWindowTitle('Stage control')
	win.setCentralWidget(stage.layout_wgt)
	win.resize(200,200)
	win.show()
	app.exec_()