import numpy as np
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter
from PyQt5.QtCore import QObject, pyqtSignal

class ScalableGroup(pTypes.GroupParameter):
	def __init__(self, cell, **opts):
		self.cell = cell
		opts['type'] = 'group'
		opts['addText'] = "Add"
		#opts['addList'] = ['str', 'float', 'int']
		opts['addList'] = [device.name for device in self.cell.slot.slot_holder.device_manager.devices]
		pTypes.GroupParameter.__init__(self, **opts)
	
	def addNew(self, typ):
		print(typ)
		point_param = self.addChild(dict(name="POS%d" % (len(self.childs)+1), type='str', value="", removable=True, renamable=True))
		point_param.sigStateChanged.connect(self.cell.update_points)

class Cell(QObject):

	table_header = ['cell_id','alkali','slot_num','contrast','status']
	saved_properties = ['_alkali','_contrast','_activation_flag','_spectroscopy_flag','_imaging_flag','points']
	update_signal = pyqtSignal()

	def __init__(self,cell_id,cell_manager,alkali='Cs',slot=None,cell_template=None):
		QObject.__init__(self)
		self.update_signal.connect(self.update)
		self.cell_id = cell_id
		self._alkali = alkali
		self.slot = slot
		self.cell_manager = cell_manager
		self._contrast = -1
		self._activation_flag = False
		self._spectroscopy_flag = True
		self._imaging_flag = True
		self.update_table_flag = True
		self.points = []
		if cell_template: self.points = cell_template['points']

	@property
	def alkali(self):
		return self._alkali

	@alkali.setter
	def alkali(self,newAlkali):
		self._alkali = newAlkali
		self.update()

	@property
	def contrast(self):
		return self._contrast

	@contrast.setter
	def contrast(self,contrast):
		self._contrast = contrast
		self.update_signal.emit()
		#self.update()

	@property
	def activation_flag(self):
		return self._activation_flag

	@activation_flag.setter
	def activation_flag(self,flag):
		self._activation_flag = flag
		self.update()

	@property
	def spectroscopy_flag(self):
		return self._spectroscopy_flag

	@spectroscopy_flag.setter
	def spectroscopy_flag(self,flag):
		self._spectroscopy_flag = flag
		self.update()

	@property
	def imaging_flag(self):
		return self._imaging_flag

	@imaging_flag.setter
	def imaging_flag(self,flag):
		self._imaging_flag = flag
		self.update()

	def get_point(self,point_label):
		for point in self.points:
			if point['label'] == point_label:
				return point
		return None

	@property
	def slot_num(self):
		if self.slot is None: return 'None'
		return self.slot.label

	@property
	def status(self):
		status = ""
		if self.activation_flag: status+='A'
		if self.spectroscopy_flag: status+='S'
		if self.imaging_flag: status+='I'
		if status is "": return "0"
		return status

	def make_table_row(self):
		return [getattr(self,key) for key in self.table_header]

	def setSlot(self,slot, update_table=True):
		if self.slot is not None:
			self.slot.clear()
		self.slot = slot
		self.updateSlot()
		if update_table: self.cell_manager.update_table()

	def toggleAlkali(self, update_table=True):
		self.update_table_flag = update_table
		if self.alkali == "Cs": self.alkali = "Rb"
		else: self.alkali = "Cs"
		self.update_table_flag = True

	def toggleActivationFlag(self, update_table=True):
		self.update_table_flag = update_table
		self.activation_flag = not self.activation_flag
		self.update_table_flag = True

	def toggleImagingFlag(self, update_table=True):
		self.update_table_flag = update_table
		self.imaging_flag = not self.imaging_flag
		self.update_table_flag = True

	def toggleSpectroscopyFlag(self, update_table=True):
		self.update_table_flag = update_table
		self.spectroscopy_flag = not self.spectroscopy_flag
		self.update_table_flag = True

	def update(self):
		self.updateSlot()
		if self.update_table_flag: self.cell_manager.update_table()

	def updateSlot(self):
		if self.slot:
			self.slot.slotItem.update_labels()
			self.slot.slotItem.update_contrast_label()		

	def makePropertiesDict(self):
		out_dict = {}
		for prop in self.saved_properties:
			out_dict.update({prop:getattr(self,prop)})
		return {self.cell_id:out_dict}

	def update_points(self,param,change,data):
		print('sigStateChanged')
		print(param,change,data)

	def makeParamGroup(self):
		cell_param_group = pTypes.GroupParameter(name = self.cell_id)
		alkali_param = Parameter.create(name='Alkali',type='list', values=['Cs','Rb'], alue=self.alkali)
		contrast_param = Parameter.create(name='Contrast',type='float',value=self.contrast)
		act_flag_param = Parameter.create(name='Activation flag',type='bool',value=self.activation_flag)
		spec_flag_param = Parameter.create(name='Spectroscopy flag',type='bool',value=self.spectroscopy_flag)
		imag_flag_param = Parameter.create(name='Imaging flag',type='bool',value=self.imaging_flag)
		position_param = Parameter.create(name='Position',type='str',value=str(self.slot.coords),readonly=True)
		points_group = ScalableGroup(self, name = 'Points')


		for point in self.points:
			point_param = Parameter.create(name=point['label'],type='str',value="({:.3f},{:.3f})".format(*point['coords']),readonly=True,renamable= True,removable= True)
			point_param.sigStateChanged.connect(self.update_points)
			points_group.addChild(point_param)
		cell_param_group.addChildren([alkali_param,contrast_param,act_flag_param,spec_flag_param,imag_flag_param,position_param,points_group])

		def change(param, changes):
				for param, change, data in changes:
					if param is alkali_param: self.alkali = alkali_param.value()
					elif param is contrast_param: self.contrast = contrast_param.value()
					elif param is act_flag_param: self.activation_flag = act_flag_param.value()
					elif param is spec_flag_param: self.spectroscopy_flag = spec_flag_param.value()
					elif param is imag_flag_param: self.imaging_flag = imag_flag_param.value()
					elif param is points_group: 
						print('sigTreeStateChanged')
						print(param,change,data)

		cell_param_group.sigTreeStateChanged.connect(change)

		return cell_param_group
