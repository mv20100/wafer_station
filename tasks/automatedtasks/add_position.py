import time
from .basetask import Task
import numpy as np
import scipy
from PIL import Image, ImageDraw, ImageFont

folder = r'G:/Utilisateurs/Manip/Desktop/data/'

class AddPosition(Task):
	"""Add OPT position."""

	def worker(self):
		print("Automated task running")

		#self.dm.light.s1.setChecked(True)
		#cell = self.cm.getCell('T01GM')
		for cell in self.cm.cellList:
			if len(cell.points)==0:
				point_dic = {'label':'OPT','coords':[2.0,-2.0]}
				cell.points.append(point_dic)

		print("Automated task done")
