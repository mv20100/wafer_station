# import xml.etree.ElementTree as ET
from lxml import etree as ET

def read_template(filename):
	tree = ET.parse(filename)
	root = tree.getroot()
	positions = root.findall("Array/PositionList/Position")
	labels = []
	pos_indicies = []
	pos_coords = []
	for position in positions:
		labels.append(position.get("label"))
		pos_indicies.append([int(position.get("indX")),int(position.get("indY"))])
		pos_coords.append([float(position.get("posX"))/1000.,float(position.get("posY"))/1000.]) # Convert um to mm
	return pos_indicies, pos_coords, labels

def read_cell_template(filename):
	tree = ET.parse(filename)
	root = tree.getroot()
	cells = root.findall("CellList/Cell")
	cells_array = []
	for cell in cells:
		cell_dic = dict(cell.attrib)
		points = cell.findall('Point')
		points_array = []
		for point in points:
			point_dic = dict(point.attrib)
			point_dic['coords'] = float(point_dic['posX'])/1000. , float(point_dic['posY'])/1000.
			point_dic = {k:v for k,v in point_dic.items() if k not in ['posX','posY']}
			points_array.append(point_dic)
		cell_dic["points"] = points_array
		cells_array.append(cell_dic)
	return cells_array

def read_array_template(filename):
	tree = ET.parse(filename)
	root = tree.getroot()
	positions = root.findall("Array/PositionList/Position")
	positions_array = []
	for position in positions:
		position_dic = dict(position.attrib)
		position_dic['coords'] = float(position_dic['posX'])/1000. , float(position_dic['posY'])/1000.
		position_dic['indices'] = int(position_dic['indX']), int(position_dic['indY'])
		position_dic = {k:v for k,v in position_dic.items() if k not in ["indX","indY",'posX','posY']}
		positions_array.append(position_dic)
	return positions_array

def read_wafer_template(filename):
	cells = read_cell_template(filename)
	positions = read_array_template(filename)
	for position in positions:
		found_cells = [cell for cell in cells if cell['id'] == position['id']]
		if len(found_cells)>0 : position["cell"] = found_cells[0]
		else: position["cell"] = None
	return positions