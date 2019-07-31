import clr
clr.AddReference("System")
from System.Text import StringBuilder
# clr.AddReference("M530USBWrap")
clr.AddReference("C:\\Program Files (x86)\\Newport\\Newport USB Driver M530\\Bin\\M530USBWrap")
from Newport import USBComm
if __name__ == '__main__':
	import sys
	sys.path.append('../..')
from base.driver import Driver

usb = USBComm.USB()
success = usb.OpenDevices(0, True)
print(f"Success : {success}")

def list_devices():
	htdt = usb.GetDeviceTable()
	print(f'Found {htdt.Count} device')
	enum = htdt.GetEnumerator()
	while enum.MoveNext():
		print(f'Key: {enum.Current.Key}, ID: {enum.Current.Value}')

list_devices()

class NP560B(Driver):

	dev_name = 'NP560B'

	def __init__(self,dev_key='560B 124207013',name='Mag. field'):
		super(NP560B, self).__init__(name)
		self.dev_key = dev_key
		print(self.identiy)

	def send(self,command):
		usb.Write(self.dev_key,command)

	def query(self,command):
		response = StringBuilder(64)
		usb.Query(self.dev_key,command,response)
		return response.ToString()

	@property
	def identiy(self):
		return self.query('*IDN?')
	
	@property
	def key_switch(self):
		"""
		Returns key switch ON/OFF status.
		"""
		return bool(int(self.query("KEY?")))

	@property
	def hw_temp(self):
		"""
		Returns instrument temperture in degC.
		"""
		return float(self.query("HWTemp?"))

	@property
	def current(self):
		"""
		Get measured laser current in mA.
		"""
		return float(self.query("LAS:LDI?"))

	@property
	def pd_current(self):
		"""
		Get measured photodiode current.
		"""
		return float(self.query("LAS:MDI?"))

	@property
	def fwd_voltage(self):
		"""
		Get measured forward voltage in V.
		"""
		return float(self.query("LAS:LDV?"))

	#Read and write properties

	@property
	def current_set_point(self):
		"""
		Get laser current set point in mA.
		"""
		return float(self.query("LAS:SET:LDI?"))

	@current_set_point.setter
	def current_set_point(self, currentSetPt):
		"""
		Set laser current set point in mA.
		"""
		self.send("LAS:LDI {}".format(float(currentSetPt)))

	@property
	def current_limit(self):
		"""
		Get the value of the laser current limit in mA.
		"""
		return float(self.query("LAS:LIM:LDI?"))

	@current_limit.setter
	def current_limit(self, currentLim):
		"""
		Set the value of the current limit in mA.
		"""
		self.send("LAS:LIM:LDI {}".format(float(currentLim)))

	@property
	def output(self):
		"""
		Get status of the laser output.
		"""
		return bool(int(self.query("LAS:OUT?")))

	@output.setter
	def output(self, state):
		"""
		Turns the laser output on or off.
		"""
		self.send("LAS:OUT {}".format(int(bool(state))))

	#Methods

	def local(self):
		"""
		Makes front panel buttons active.
		"""
		self.send("LOCAL")

if __name__ == '__main__':
	ldd = NP560B(dev_key='560B 124207013')
