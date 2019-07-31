from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import numpy as np

columnsHeaders = [ ('Cell',object),
			('Position', object),
			('Current (mA)', float,), 
			('Time (s)', float),
			('Status',object)]

class MyTableWidget(pg.TableWidget):

	def __init__(self):

		pg.TableWidget.__init__(self,editable=False,sortable=False)
	
		data = np.array([
			(u"TXXX_XXX",(0,0),2200,5,u"Done"),
			], dtype=columnsHeaders)
		self.setData(data)
		# self.removeRow(0)
		self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

	def get_selected_rows_idx(self):
		return list(set([item.row() for item in self.selectedIndexes()]))

	def get_first_selected_row(self):
		selection = self.get_selected_rows_idx()
		selection.sort()
		return selection[0]

	def delete_selected_rows(self):
		selection = self.get_selected_rows_idx()
		selection.sort(reverse=True)
		for rowIx in selection:
			self.removeRow(rowIx)

	def get_row(self,row_idx):
		column_indexes = list(range(self.columnCount()))
		row = []
		for c_idx in column_indexes:
			row.append(self.item(row_idx,c_idx).value)
		return row

	def get_rows(self):
		row_indexes = list(range(self.rowCount()))
		rows = []
		for r_idx in row_indexes:
			rows.append(self.get_row(r_idx))
		return rows


	def appendRow(self,row):
		self.addRow(row)
		nrow = self.rowCount()
		self.item(nrow-1,0).setEditable(True)
		self.item(nrow-1,2).setEditable(True)
		self.item(nrow-1,3).setEditable(True)


