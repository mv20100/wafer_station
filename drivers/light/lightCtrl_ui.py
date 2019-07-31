from .lightCtrl import LightCtrl
from PyQt5.QtCore import Qt
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg

from PyQt5.QtCore import QPropertyAnimation, QRectF, QSize, Qt, pyqtProperty
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import (
    QAbstractButton,
    QApplication,
    QHBoxLayout,
    QSizePolicy,
    QWidget,
)


class Switch(QAbstractButton):
    def __init__(self, parent=None, track_radius=10, thumb_radius=8):
        super().__init__(parent=parent)
        self.setCheckable(True)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self._track_radius = track_radius
        self._thumb_radius = thumb_radius

        self._margin = max(0, self._thumb_radius - self._track_radius)
        self._base_offset = max(self._thumb_radius, self._track_radius)
        self._end_offset = {
            True: lambda: self.width() - self._base_offset,
            False: lambda: self._base_offset,
        }
        self._offset = self._base_offset

        palette = self.palette()
        if self._thumb_radius > self._track_radius:
            self._track_color = {
                True: palette.highlight(),
                False: palette.dark(),
            }
            self._thumb_color = {
                True: palette.highlight(),
                False: palette.light(),
            }
            self._text_color = {
                True: palette.highlightedText().color(),
                False: palette.dark().color(),
            }
            self._thumb_text = {
                True: '',
                False: '',
            }
            self._track_opacity = 0.5
        else:
            self._thumb_color = {
                True: palette.highlightedText(),
                False: palette.light(),
            }
            self._track_color = {
                True: palette.highlight(),
                False: palette.dark(),
            }
            self._text_color = {
                True: palette.highlight().color(),
                False: palette.dark().color(),
            }
            self._thumb_text = {
                True: '✔',
                False: '✕',
            }
            self._track_opacity = 1

    @pyqtProperty(int)
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = value
        self.update()

    def sizeHint(self):  # pylint: disable=invalid-name
        return QSize(
            4 * self._track_radius + 2 * self._margin,
            2 * self._track_radius + 2 * self._margin,
        )

    def setChecked(self, checked):
        super().setChecked(checked)
        self.offset = self._end_offset[checked]()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.offset = self._end_offset[self.isChecked()]()

    def paintEvent(self, event):  # pylint: disable=invalid-name, unused-argument
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setPen(Qt.NoPen)
        track_opacity = self._track_opacity
        thumb_opacity = 1.0
        text_opacity = 1.0
        if self.isEnabled():
            track_brush = self._track_color[self.isChecked()]
            thumb_brush = self._thumb_color[self.isChecked()]
            text_color = self._text_color[self.isChecked()]
        else:
            track_opacity *= 0.8
            track_brush = self.palette().shadow()
            thumb_brush = self.palette().mid()
            text_color = self.palette().shadow().color()

        p.setBrush(track_brush)
        p.setOpacity(track_opacity)
        p.drawRoundedRect(
            self._margin,
            self._margin,
            self.width() - 2 * self._margin,
            self.height() - 2 * self._margin,
            self._track_radius,
            self._track_radius,
        )
        p.setBrush(thumb_brush)
        p.setOpacity(thumb_opacity)
        p.drawEllipse(
            self.offset - self._thumb_radius,
            self._base_offset - self._thumb_radius,
            2 * self._thumb_radius,
            2 * self._thumb_radius,
        )
        p.setPen(text_color)
        p.setOpacity(text_opacity)
        font = p.font()
        font.setPixelSize(1.5 * self._thumb_radius)
        p.setFont(font)
        p.drawText(
            QRectF(
                self.offset - self._thumb_radius,
                self._base_offset - self._thumb_radius,
                2 * self._thumb_radius,
                2 * self._thumb_radius,
            ),
            Qt.AlignCenter,
            self._thumb_text[self.isChecked()],
        )

    def mouseReleaseEvent(self, event):  # pylint: disable=invalid-name
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            anim = QPropertyAnimation(self, b'offset', self)
            anim.setDuration(120)
            anim.setStartValue(self.offset)
            anim.setEndValue(self._end_offset[self.isChecked()]())
            anim.start()

    def enterEvent(self, event):  # pylint: disable=invalid-name
        self.setCursor(Qt.PointingHandCursor)
        super().enterEvent(event)

class LightCtrl_UI(LightCtrl):

	def __init__(self,**kwargs):
		super(LightCtrl_UI, self).__init__(**kwargs)

		self.layout_wgt = pg.LayoutWidget()

		self.s1 = Switch()
		self.s1.setChecked(self.is_enabled)
		self.s1.toggled.connect(self.switch)
		self.r_slider = QtGui.QSlider(Qt.Horizontal)
		self.g_slider = QtGui.QSlider(Qt.Horizontal)
		self.b_slider = QtGui.QSlider(Qt.Horizontal)
		for slider in [self.r_slider,self.g_slider,self.b_slider]:
			slider.setMinimum(0)
			slider.setMaximum(255)
		self.r_slider.setValue(self.red)
		self.g_slider.setValue(self.green)
		self.b_slider.setValue(self.blue)
		self.layout_wgt.addWidget(self.s1, row=0, col=1)
		self.layout_wgt.addWidget(QtGui.QLabel('R'), row=1, col=0)
		self.layout_wgt.addWidget(self.r_slider, 	 row=1, col=1)
		self.layout_wgt.addWidget(QtGui.QLabel('G'), row=2, col=0)
		self.layout_wgt.addWidget(self.g_slider,	 row=2, col=1)
		self.layout_wgt.addWidget(QtGui.QLabel('B'), row=3, col=0)
		self.layout_wgt.addWidget(self.b_slider,	 row=3, col=1)

		self.r_slider.valueChanged.connect(self.light_r_changed)
		self.g_slider.valueChanged.connect(self.light_g_changed)
		self.b_slider.valueChanged.connect(self.light_b_changed)

	def switch(self,value):
		self.is_enabled = self.s1.isChecked()

	def light_r_changed(self,value):
		self.red = value

	def light_g_changed(self,value):
		self.green = value

	def light_b_changed(self,value):
		self.blue = value

if __name__ == '__main__':
	app = QtGui.QApplication([])
	lightCtrl = LightCtrl_UI(comPort='com5')
	win = QtGui.QMainWindow()
	win.setWindowTitle('Light')
	win.setCentralWidget(lightCtrl.layout_wgt)
	win.resize(200,200)
	win.show()
	app.exec_()
	lightCtrl.close()