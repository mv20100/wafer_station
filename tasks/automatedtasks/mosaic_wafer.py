import time
from .basetask import Task
import numpy as np
import scipy
from PIL import Image, ImageDraw, ImageFont

folder = r'G:/Utilisateurs/Manip/Desktop/data/'

class MosaicWafer(Task):
	"""Make image mosaic of the wafer holder."""

	# def __init__(self,cm, dm):
	# 	Task.__init__(self,cm, dm)

	def worker(self):
		self.running = True
		print("Automated task running")

		self.dm.light.s1.setChecked(True)
		#cell = self.cm.getCell('T01GM')
		selected_cells = []
		for cell in self.cm.cellList:
			if cell.slot.slot_holder.identiy == 'wafer_holder':
				if cell.get_point('OPT') != None or cell.get_point('DISP') != None :
					selected_cells.append(cell)
		xmin = min([cell.slot.position[0] for cell in selected_cells])
		xmax = max([cell.slot.position[0] for cell in selected_cells])
		ymin = min([cell.slot.position[1] for cell in selected_cells])
		ymax = max([cell.slot.position[1] for cell in selected_cells])
		print(xmin,xmax,ymin,ymax)
		mosaic = Image.new('RGB', ((xmax-xmin+1)*800,(ymax-ymin+1)*600))

		for cell in selected_cells:
			point = cell.get_point('OPT')
			if point == None: point = cell.get_point('DISP')
			cell.slot.moveTo(point['coords'],self.dm.getDevice('Camera').coords,wait=True)
			time.sleep(0.5)
			#self.dm.camera.save_image(folder+cell.cell_id+'.jpg')
			try:
				self.dm.camera.stop()
			except:
				pass
			self.dm.camera.get_image()
			#scipy.misc.imsave(folder+cell.cell_id+'.jpg', self.dm.camera.imageData.reshape(1024,1280,3).transpose(1,0,2))
			#scipy.misc.imsave(folder+cell.cell_id+'.jpg', np.flip(self.dm.camera.imageData.reshape(1024,1280,3),1) )
			image = Image.fromarray(np.flip(self.dm.camera.imageData.reshape(1024,1280,3),1).astype('uint8'), 'RGB')
			thumb = image.resize((800,600))
			mosaic.paste(thumb, ( (cell.slot.position[0]-xmin)*800,(cell.slot.position[1]-ymin)*600 ) )
			draw = ImageDraw.Draw(image)
			fnt = ImageFont.truetype('arial',size=40)
			draw.text((10,10), "{:.1f} %".format(cell.contrast), font=fnt, fill=(255,255,255))
			try:
				image.save(folder+cell.cell_id+' '+time.strftime('%Y-%m-%d %H%M')+'.jpg', "JPEG")
			except PIL.PermissionError as e:
				print(e)
			self.dm.camera.start()
			if not self.running: break
		mosaic.save(folder+"wafer "+time.strftime('%Y-%m-%d %H%M')+'.jpg', "JPEG")
		print("Automated task done")
