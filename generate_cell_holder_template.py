# import xml.etree.ElementTree as ET
from lxml import etree as ET
import numpy as np

cell_size = np.array([4000.,6000.])
matrix_spacing = np.array([4000.,4000.])
slot_number = np.array([11,9])

positions = list(np.ndindex(*slot_number))
no_slot_positions = [(i,j) for i in [0,5,10] for j in [0,4,8]]
positions = [np.array(position) for position in positions if position not in no_slot_positions]

posList = ET.Element("PositionList")

for idx, position in enumerate(positions):
	label = "Slot{:02d}".format(idx+1)
	coords = (cell_size + matrix_spacing) * position
	node = ET.Element("Position")
	node.set("label",label)
	node.set("posX",str(coords[0]))
	node.set("posY",str(-coords[1]))
	node.set("indX",str(position[0]))
	node.set("indY",str(position[1]))
	posList.append(node)
	print(label+" "+str(coords))

arrayNode = ET.Element("Array")
arrayNode.set("cellNumber",str(len(positions)))
arrayNode.append(posList)
layoutNode = ET.Element("Layout")
layoutNode.append(arrayNode)
tree = ET.ElementTree(layoutNode)
tree.write("cell_holder_template.xml", pretty_print=True)
