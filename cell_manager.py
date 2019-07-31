import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import yaml
from cell import Cell
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter

class CellManager(object):

	save_filename = "./data/cells.yaml"
	_saved_cell_dict = None
	_selected_cell = None

	def __init__(self):
		self.cellList = []
		self.table = pg.TableWidget(editable=False,sortable=True)
		self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

		self.param_group = pTypes.GroupParameter(name = "Cell manager")
		self.default_alkali_param = Parameter.create(name='Default alkali',
													type='list',
													values=['Cs','Rb'],
													value='Cs')
		self.selected_cell_param_group = pTypes.GroupParameter(name = "No cell selected")
		self.selected_cell_child_param_group = None
		self.param_group.addChildren([self.default_alkali_param,
									self.selected_cell_param_group])
		# def nothing():
		# 	pass
		# self.selected_cell_param_group.sigTreeStateChanged.connect(nothing)


	def init_table(self):
		QtGui.QTableWidget.clear(self.table)
		self.table.items = []
		self.table.setColumnCount(len(Cell.table_header))
		self.table.setRowCount(0)
		self.table.setHorizontalHeaderLabels(Cell.table_header)

	def update_table(self):
		#print("Updating table")
		rows = []
		for cell in self.cellList:
			rows.append(cell.make_table_row())
		self.init_table()
		self.table.appendData(rows)
		self.table.resizeColumnsToContents()

	def getCell(self,cell_id):
		for cell in self.cellList:
			if cell.cell_id == cell_id:
				return cell
		return None

	def generateCellFromSavedList(self,cell_id):
		if cell_id in self.getSavedCellList():
			cell_dict = self.getSavedCellList()[cell_id]
			cell = Cell(cell_id=cell_id,cell_manager=self)
			for attr in cell_dict:				
				setattr(cell,attr,cell_dict[attr])
			return cell
		return None

	def addCell(self,cell_id,update_table=True,cell_template=None):
		cell = self.getCell(cell_id)
		if cell is not None: return cell
		cell = self.generateCellFromSavedList(cell_id)
		if cell is None:
			cell = Cell(cell_id=cell_id,cell_manager=self,alkali=self.default_alkali_param.value(),cell_template=cell_template)
		self.cellList.append(cell)
		if update_table: self.update_table()
		return cell

	def removeCell(self,cell,update_table=True):
		if cell is self.selected_cell: self.selected_cell = None
		self.cellList.remove(cell)
		if update_table: self.update_table()

	def getSavedCellList(self):
		if self._saved_cell_dict is not None: return self._saved_cell_dict
		try:
			with open(self.save_filename, 'r') as stream:
				cell_dict = yaml.load(stream)
			print("Loaded {:d} cells from file {}.".format(len(cell_dict),self.save_filename))
			self._saved_cell_dict = cell_dict
			return cell_dict
		except OSError:
			print('Cell info file {} not found.'.format(self.save_filename))
			self._saved_cell_dict = {}
			return {}

	def saveCellList(self):
		old_cell_dict = self.getSavedCellList()
		cell_dict = {}
		for cell in self.cellList:
			cell_dict.update(cell.makePropertiesDict())
		old_cell_dict.update(cell_dict)
		with open(self.save_filename, 'w') as outfile:
			outfile.write( yaml.dump(old_cell_dict, default_flow_style=False) )
		print("Saved {:d} cells to file {}.".format(len(cell_dict),self.save_filename))

	@property
	def selected_cell(self):
		return self._selected_cell

	@selected_cell.setter
	def selected_cell(self,cell):
		if cell != self.selected_cell:
			if self.selected_cell_child_param_group is not None:
				self.selected_cell_param_group.removeChild(self.selected_cell_child_param_group)
				try: self.selected_cell_child_param_group.sigTreeStateChanged.disconnect()
				except: pass
				del self.selected_cell_child_param_group
				self.selected_cell_child_param_group = None
			self._selected_cell = None
			if cell != None:
				self.selected_cell_param_group.setName('Selected cell')
				# print("New cell selected")
				self._selected_cell = cell
				self.selected_cell_child_param_group = cell.makeParamGroup()
				self.selected_cell_param_group.addChild(self.selected_cell_child_param_group)
			else:
				self.selected_cell_param_group.setName('No cell selected')


