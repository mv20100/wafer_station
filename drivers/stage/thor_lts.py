import clr, threading, sys
sys.path.append("C:\\Program Files\\Thorlabs\\Kinesis")
clr.AddReference("System")
clr.AddReference(r"Thorlabs.MotionControl.DeviceManagerCLI")
clr.AddReference(r"Thorlabs.MotionControl.IntegratedStepperMotorsCLI")
from System import Decimal
import Thorlabs.MotionControl.DeviceManagerCLI
import Thorlabs.MotionControl.IntegratedStepperMotorsCLI
dmcli = Thorlabs.MotionControl.DeviceManagerCLI.DeviceManagerCLI()

def list_devices():
	dmcli.BuildDeviceList()
	dev_list = dmcli.GetDeviceList()
	print(f"Found {len(dev_list)} Kinesis devices: {str(dev_list)}")

list_devices()

class ThorLTS(object):

	def __init__(self,serial='45874425'):
		self.serial = serial
		self.lts = Thorlabs.MotionControl.IntegratedStepperMotorsCLI.LongTravelStage.CreateLongTravelStage(serial)
		self.lts.Connect(self.serial)
		print(f"Connected: {self.lts.IsConnected}")
		if not self.lts.IsSettingsInitialized(): self.lts.WaitForSettingsInitialized(5000)
		self.lts.StartPolling(250)
		self.motorSettings = self.lts.LoadMotorConfiguration(self.serial)
		self.motorDeviceSettings =  self.lts.MotorDeviceSettings

	@property
	def position(self):
		return Decimal.ToDouble(self.lts.Position)

	@position.setter
	def position(self,new_position):
		return self.lts.MoveTo(Decimal(float(new_position)),20000)

	@property
	def is_homed(self):
		return self.lts.Status.IsHomed

	@property
	def max_velocity(self):
		return Decimal.ToDouble(self.lts.GetVelocityParams().MaxVelocity)

	@property
	def acceleration(self):
		return Decimal.ToDouble(self.lts.GetVelocityParams().Acceleration)	
 	
class Stage(object):

	def __init__(self, x_serial = '45874656', y_serial = '45874425'):
		self.x_lts = ThorLTS(x_serial)
		self.y_lts = ThorLTS(y_serial)

	@property
	def position(self):
		return 150.0-self.x_lts.position, self.y_lts.position

	@position.setter
	def position(self,new_position):
		self.move_to(new_position)

	def move_to(self,new_position,wait=True):
		def thread(axis_lts,position):
			axis_lts.position = position
		t1 = threading.Thread(name="thread",target=thread,args=(self.x_lts,150.0-new_position[0]))
		t2 = threading.Thread(name="thread",target=thread,args=(self.y_lts,new_position[1]))
		t1.start()
		t2.start()
		if wait:
			t1.join()
			t2.join()

	def home(self,wait=True):
		def thread(axis_lts):
			axis_lts.lts.Home(60000)
		t1 = threading.Thread(name="thread",target=thread,args=(self.x_lts,))
		t2 = threading.Thread(name="thread",target=thread,args=(self.y_lts,))
		t1.start()
		t2.start()
		if wait:
			t1.join()
			t2.join()		

if __name__ == '__main__':
	stage = Stage(x_serial = '45874656', y_serial = '45874425')