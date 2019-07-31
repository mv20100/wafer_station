import time
from .basetask import Task
import numpy as np

class ContrastMapping(Task):
	"""Measure contrast once in all cells with an optical cavity."""


	def worker(self):
		assert not self.running
		self.running = True
		print("Automated task running")

		#cell = self.cm.getCell('T01GM')
		self.dm.light.s1.setChecked(False)
		for cell in self.cm.cellList:
			if cell.get_point('OPT') != None:
				cell.slot.moveTo(cell.get_point('OPT')['coords'],self.dm.getDevice('Spectro').coords,wait=True)
				contrast = self.dm.picoscope.get_contrast()*100
				cell.contrast = contrast
				print(f'{cell.cell_id} : Cst={round(contrast,2)} %')
			if not self.running:
				print("Exiting")
				break
		print("Automated task done")
