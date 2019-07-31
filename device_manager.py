import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import yaml
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter


saved_properties = ['coords']

class Device(object):

	def __init__(self,name,coords=None):
		self.name = name
		if coords is None: self.coords = (0.0,0.0)
		else: self.coords = coords
		self.param = Parameter.create(name=name,type='str',value=str(self.coords))

	def set_coords(self,coords):
		self.coords = coords

	def makeMapLayoutItems(self,plot):
		self.arrow = pg.ArrowItem(pos=(0, 0), angle=-90)
		plot.addItem(self.arrow)
		self.txt = pg.TextItem(html='<div style="text-align: center"><span style="color: #FFF;font-size: 12pt;">{}</span></div>'.format(self.name), anchor=(0.5, 2.0),border='w', fill=(0, 0, 255, 100))
		plot.addItem(self.txt)

	def updateMapLayoutItemsPosition(self,stage_position):
		self.arrow.setPos(stage_position[0]+self.coords[0],stage_position[1]+self.coords[1])
		self.txt.setPos(stage_position[0]+self.coords[0],stage_position[1]+self.coords[1])

	def makePropertiesDict(self):
		out_dict = {}
		for prop in saved_properties:
			out_dict.update({prop:getattr(self,prop)})
		return {self.name:out_dict}

class DeviceManager(object):

	filename = "./data/devices.yaml"

	def __init__(self):
		self.devices = []
		self.devices_dict =  self.loadDeviceList()
		self.param_group = pTypes.GroupParameter(name = 'Devices')
		self.save_devices_param = Parameter.create(name='Save',type='action')
		self.save_devices_param.sigActivated.connect(self.saveDeviceList)
		self.param_group.addChildren([self.save_devices_param])

	def getDevice(self,name):
		for device in self.devices:
			if device.name == name: return device
		return None

	def addDevice(self,name,coords=None):
		device = self.getDevice(name)
		if device is not None: return device
		if self.devices_dict and name in self.devices_dict:
			dev = Device(name,self.devices_dict[name]['coords'])
		else: dev = Device(name,coords)
		self.devices.append(dev)
		self.param_group.addChild(dev.param)

	def loadDeviceList(self):
		try:
			with open(self.filename, 'r') as stream:
				devices_dict = yaml.load(stream)
				print("Loaded {:d} devices from file {}.".format(len(devices_dict),self.filename))
				return devices_dict
		except OSError:
			print('Device info file {} not found.'.format(self.filename))
			return {}

	def saveDeviceList(self):
		new_devices_dict = {}
		for dev in self.devices:
			new_devices_dict.update(dev.makePropertiesDict())
		self.devices_dict.update(new_devices_dict)
		with open(self.filename, 'w') as outfile:
			outfile.write( yaml.dump(self.devices_dict, default_flow_style=False) )
		print("Saved {:d} devices to file {}.".format(len(new_devices_dict),self.filename))


