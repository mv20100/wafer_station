import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.graphicsItems.PlotItem.PlotItem import PlotItem
from pyqtgraph.graphicsItems.ViewBox.ViewBox import ViewBox
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree
import numpy as np
from slot import Slot
from read_wafer_template import read_wafer_template
import yaml

label_txt = ('<font color="red"><b>F</b></font> show all - '
			'<font color="red"><b>E</b></font> enable - '
			'<font color="red"><b>R</b></font> switch Rb/Cs - '
			'<font color="red"><b>Del/D</b></font> remove cell - '
			'<font color="red"><b>A/S/C</b></font> (un)mark for activation/spectroscopy/imaging - '
			'<font color="red"><b>F1/F2</b></font> save/load default allocation')

class SlotHolderViewBox(ViewBox):
	def __init__(self,slot_holder,**kwargs):
		ViewBox.__init__(self,**kwargs)
		self.slot_holder = slot_holder

	def keyPressEvent(self, ev):
		if ev.key() == QtCore.Qt.Key_F:
			ev.accept()
			self.autoRange()
			return
		elif ev.key() == QtCore.Qt.Key_F1:
			ev.accept()
			self.slot_holder.saveAllocation()
			return
		elif ev.key() == QtCore.Qt.Key_F2:
			ev.accept()
			self.slot_holder.loadAllocation()
			return

		items = self.slot_holder._scene.selectedItems()
		if len(items)>0:
			# Remove selected cells when D pressed
			if ev.key() == QtCore.Qt.Key_Delete or ev.key() == QtCore.Qt.Key_D:
				ev.accept()
				for slotItem in items:
					slotItem.slot.removeCell(update_table=False)
				self.slot_holder.cell_manager.update_table()
				return
			# Toggle alkali when R pressed
			elif ev.key() == QtCore.Qt.Key_R:
				ev.accept()
				for slotItem in items:
					if slotItem.slot.cell is not None:
						slotItem.slot.cell.toggleAlkali(update_table=False)
				self.slot_holder.cell_manager.update_table()
				return
			# Toggle activation flag when A pressed
			elif ev.key() == QtCore.Qt.Key_A:
				ev.accept()
				for slotItem in items:
					if slotItem.slot.cell is not None:
						slotItem.slot.cell.toggleActivationFlag(update_table=False)
				self.slot_holder.cell_manager.update_table()
				return
			# Toggle spectroscopy flag when S pressed
			elif ev.key() == QtCore.Qt.Key_S:
				ev.accept()
				for slotItem in items:
					if slotItem.slot.cell is not None:
						slotItem.slot.cell.toggleSpectroscopyFlag(update_table=False)
				self.slot_holder.cell_manager.update_table()
				return
			# Toggle imaging flag when C pressed
			elif ev.key() == QtCore.Qt.Key_C:
				ev.accept()
				for slotItem in items:
					if slotItem.slot.cell is not None:
						slotItem.slot.cell.toggleImagingFlag(update_table=False)
				self.slot_holder.cell_manager.update_table()
				return
			# Enable slot when E pressed
			elif ev.key() == QtCore.Qt.Key_E:
				ev.accept()
				for slotItem in items:
					if slotItem.slot.cell is None:
						slotItem.enableSlot(update_table=False)
				self.slot_holder.cell_manager.update_table()
				return
		ev.ignore()

	def mouseClickEvent(self, ev):
		if int(ev.button()) == int(QtCore.Qt.RightButton):
			ev.accept()
			self.buildMenu()
			self.raiseContextMenu(ev)

	def getMenu(self):
		return self.menu

	def raiseContextMenu(self, ev):
		# menu = self.scene().addParentContextMenus(self, self.getMenu(), ev)
		pos = ev.screenPos()
		self.menu.popup(QtCore.QPoint(pos.x(), pos.y()))

	def buildMenu(self):
		self.menu = QtGui.QMenu()
		self.menu.setTitle("Slot holder")
		self.menu.addAction("Save allocation", self.slot_holder.saveAllocation)
		self.menu.addAction("Load allocation", self.slot_holder.loadAllocation)
		self.menu.addAction("Clear all slots", self.slot_holder.clearSlots)
		self.menu.addAction("Enable all slots", self.slot_holder.enableAllSlots)
		self.menu.addAction("Save cells info", self.slot_holder.cell_manager.saveCellList)


default_wafer_id = "T01"

class SlotHolder(QtCore.QObject):

	reference_slots_updated = QtCore.Signal()

	def __init__(self,cell_manager,device_manager,stage=None, identiy=None, is_wafer_holder = True, xml_template = None):
		QtCore.QObject.__init__(self)
		self.cell_manager = cell_manager
		self.device_manager = device_manager
		self.stage = stage
		self.identiy = identiy
		self.is_wafer_holder = is_wafer_holder
		self._wafer_id = None
		self.slots = []
		self.reference_slots = []
		self.transform_matrix = None
		self.rotated_by_default = False

		self.view = pg.GraphicsLayoutWidget()
		self._scene = self.view.scene()
		self._scene.selectionChanged.connect(self.selectionChanged)
		vb = SlotHolderViewBox(self,lockAspect=True, invertY=True)
		self.plt = PlotItem(viewBox=vb)
		self.plt.hideAxis('bottom')
		self.plt.hideAxis('left')
		self.view.addItem(self.plt)
		self.view.nextRow()
		self.view.addLabel(label_txt)

		self.param_group = pTypes.GroupParameter(name = self.identiy)
		if self.is_wafer_holder:
			self.wafer_id_param = Parameter.create(name='wafer_id',type='str')
			self.param_group.addChild(self.wafer_id_param)
			self.wafer_id_param.sigValueChanged.connect(self.wafer_id_changed)

		if xml_template is not None:
			self.generate_from_template(xml_template)
		self.loadAlignement()
		if self.wafer_id is None: self.wafer_id = default_wafer_id
		if not self.is_wafer_holder: self.loadAllocation()

	def wafer_id_changed(self):
		self.wafer_id = self.wafer_id_param.value()

	def addSlot(self, position_dic):
		slot = Slot(position_dic['indices'],
					np.array(position_dic['coords']),
					position_dic['label'],
					self.cell_manager,
					self,
					cell_template=position_dic['cell'])
		self.plt.addItem(slot.slotItem)
		self.slots.append(slot)

	def getSlot(self,label):
		for slot in self.slots:
			if slot.label == label: return slot
		raise Exception('The slot label "{}" could not be found within the slots of {}'.format(label,self.identiy))

	def clearSlots(self):
		for slot in self.slots:
			slot.removeCell(update_table=False)
		self.cell_manager.update_table()

	def enableAllSlots(self):
		for slot in self.slots:
			slot.slotItem.enableSlot(update_table=False)
		self.cell_manager.update_table()

	def addReferenceSlot(self,slot):
		if slot is str:
			slot = self.getSlot(slot)
		if not slot.is_reference:
			slot.is_reference = True
			slot.stage_position = np.array(self.stage.position)
			self.reference_slots.append(slot)
			self.compute_transform_matrix()
			self.reference_slots_updated.emit()

	def removeReferenceSlot(self,slot):
		if slot is str:
			slot = self.getSlot(slot)
		if slot.is_reference:
			slot.is_reference = False
			self.reference_slots.remove(slot)
			self.compute_transform_matrix()
			self.reference_slots_updated.emit()

	@property
	def wafer_id(self):
		return self._wafer_id

	@wafer_id.setter
	def wafer_id(self,new_id):
		if self.is_wafer_holder:
			self.saveAllocation()
			self._wafer_id = new_id
			self.wafer_id_param.setValue(self._wafer_id,blockSignal=self.wafer_id_changed)
			self.loadAllocation()

	def get_allocation_identity(self):
		if self.is_wafer_holder: return "wafer_"+self.wafer_id
		else: return self.identiy

	def get_allocation_filename(self):
		return "./data/"+self.get_allocation_identity()+"_allocation.yaml"

	def saveAllocation(self):
		used_slots_dict = {}
		for slot in self.slots:
			if slot.cell is not None:
				used_slots_dict.update({slot.label: slot.cell.cell_id})
		if len(used_slots_dict)>0:
			with open(self.get_allocation_filename(), 'w') as outfile:
				outfile.write( yaml.dump(used_slots_dict, default_flow_style=False) )
			print("Saved {:d} positions to file {}.".format(len(used_slots_dict),self.get_allocation_filename()))
		else: print("No slots to save")

	def loadAllocation(self):
		self.clearSlots()
		try:
			with open(self.get_allocation_filename(), 'r') as stream:
				used_slots_dict = yaml.load(stream)
			for slot_label in used_slots_dict:
				slot = self.getSlot(slot_label)
				cell = self.cell_manager.addCell(used_slots_dict[slot_label],update_table=False)
				slot.setCell(cell,update_table=False)
			self.cell_manager.update_table()
			print("Loaded {:d} positions from file {}.".format(len(used_slots_dict),self.get_allocation_filename()))
			return len(used_slots_dict)
		except (IOError, OSError):
			print('No allocation file found for {}.'.format(self.get_allocation_identity()))
			return None

	def get_alignment_filename(self):
		return "./data/"+self.identiy+"_alignment.yaml"

	def saveAlignement(self):
		saved_dict = {}
		if self.transform_matrix is not None: 	saved_dict["transform_matrix"] = self.transform_matrix
		if self.is_wafer_holder: 				saved_dict["wafer_id"] = self.wafer_id
		with open(self.get_alignment_filename(), 'w') as outfile:
			outfile.write( yaml.dump(saved_dict, default_flow_style=False) )

	def loadAlignement(self):
		try:
			with open(self.get_alignment_filename(), 'r') as stream:
				loaded_dict = yaml.load(stream)
			if "transform_matrix" in loaded_dict: self.transform_matrix = loaded_dict["transform_matrix"]
			if "wafer_id" in loaded_dict and self.is_wafer_holder: self.wafer_id = loaded_dict["wafer_id"]
		except (IOError, OSError):
			print('No alignment file found for {}.'.format(self.identiy))

	def generate_from_template(self,xml_template):
		positions = read_wafer_template(xml_template)
		for position_dic in positions:
			self.addSlot(position_dic)

	def selectionChanged(self):
		items = self._scene.selectedItems()
		if len(items) == 0:
			self.cell_manager.selected_cell = None
		else:
			item = items[0]
			if item.slot.cell is not None:
				self.cell_manager.selected_cell = item.slot.cell
			else: self.cell_manager.selected_cell = None

	def compute_transform_matrix(self):
		if len(self.reference_slots)==1:
			slot = self.reference_slots[0]
			stage_coords = slot.stage_position
			if not self.rotated_by_default:
				self.transform_matrix =  np.eye(3,dtype=float)
				self.transform_matrix[0:2,2] =  stage_coords - slot.coords
			else:
				self.transform_matrix =  -np.eye(3,dtype=float)
				self.transform_matrix[2,2] = 1
				self.transform_matrix[0:2,2] = stage_coords + slot.coords
			print(self.transform_matrix)
		if len(self.reference_slots)==2:
			src = np.vstack([item.coords for item in self.reference_slots])
			dst = np.vstack([item.stage_position for item in self.reference_slots])
			# https://stackoverflow.com/questions/39704121/compute-the-similarity-transformation-matrix-given-two-sets-of-points
			src_d_y = src[0][1] - src[1][1]
			src_d_x = src[0][0] - src[1][0]
			src_dis = np.sqrt(src_d_y**2 + src_d_x**2)
			dst_d_y = dst[0][1] - dst[1][1]
			dst_d_x = dst[0][0] - dst[1][0]
			dst_dis = np.sqrt(dst_d_y**2 + dst_d_x**2)
			scale = dst_dis / src_dis
			angle = np.arctan2(src_d_y, src_d_x) - np.arctan2(dst_d_y, dst_d_x)
			alpha = np.cos(angle)*scale
			beta = np.sin(angle)*scale
			self.transform_matrix =  np.eye(3,dtype=float)
			self.transform_matrix[0,0] = alpha
			self.transform_matrix[0,1] = beta
			self.transform_matrix[0,2] = (dst[0][0] - alpha*src[0][0] - beta*src[0][1] + dst[1][0] - alpha*src[1][0] - beta*src[1][1])/2.
			self.transform_matrix[1,0] = -beta
			self.transform_matrix[1,1] = alpha
			self.transform_matrix[1,2] = (dst[0][1] + beta*src[0][0] - alpha*src[0][1] + dst[1][1] + beta*src[1][0] - alpha*src[1][1])/2.
			print(self.transform_matrix)

		if len(self.reference_slots)==3:
			A_part = np.vstack([item.coords for item in self.reference_slots])
			X_part = np.vstack([item.stage_position for item in self.reference_slots])
			A = np.vstack([np.transpose(A_part),np.transpose(np.ones(3))])
			X = np.vstack([np.transpose(X_part),np.transpose(np.ones(3))])
			self.transform_matrix = X.dot(np.linalg.inv(A))
			print(self.transform_matrix)

	def to_stage_coords(self,coords):
		vector = np.ones(3,dtype=float)
		vector[0:2] = coords
		return self.transform_matrix.dot(vector)[0:2]
