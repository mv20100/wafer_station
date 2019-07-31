import time
from .basetask import Task
import numpy as np
import scipy
from PIL import Image, ImageDraw, ImageFont

folder = r'G:/Utilisateurs/Manip/Desktop/data/'

class TakeImages(Task):
	"""Measure contrast once in all cells with an optical cavity."""

	# def __init__(self,cm, dm):
	# 	Task.__init__(self,cm, dm)

	def worker(self):
		self.running = True
		print("Automated task running")

		self.dm.light.s1.setChecked(True)
		#cell = self.cm.getCell('T01GM')
		for cell in self.cm.cellList:
			if cell.get_point('OPT') != None:
				cell.slot.moveTo(cell.get_point('OPT')['coords'],self.dm.getDevice('Camera').coords,wait=True)
				time.sleep(0.3)
				#self.dm.camera.save_image(folder+cell.cell_id+'.jpg')
				try:
					self.dm.camera.stop()
				except:
					pass
				self.dm.camera.get_image()
				#scipy.misc.imsave(folder+cell.cell_id+'.jpg', self.dm.camera.imageData.reshape(1024,1280,3).transpose(1,0,2))
				#scipy.misc.imsave(folder+cell.cell_id+'.jpg', np.flip(self.dm.camera.imageData.reshape(1024,1280,3),1) )
				image = Image.fromarray(np.flip(self.dm.camera.imageData.reshape(1024,1280,3),1).astype('uint8'), 'RGB')
				draw = ImageDraw.Draw(image)
				fnt = ImageFont.truetype('arial',size=40)
				draw.text((10,10), "{:.1f} %".format(cell.contrast), font=fnt, fill=(255,255,255))
				print(cell.slot.position)
				try:
					image.save(folder+cell.cell_id+'.jpg', "JPEG")
				except PIL.PermissionError as e:
					print(e)
				self.dm.camera.start()
				if not self.running: break
		print("Automated task done")
