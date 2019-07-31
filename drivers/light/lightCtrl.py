import time, serial, threading

class LightCtrl(object):

	def __init__(self,comPort='com5'):
		self.lock = threading.Lock()
		try:
			self.ser = serial.Serial()
			self.ser.port = comPort
			self.ser.timeout = 5
			self.ser.setDTR(False) # This prevents the arduino from rebooting on connect
			self.ser.open()
		except serial.serialutil.SerialException:
			#no serial connection
			self.ser = None
		else:
			pass
		print("Light controller connection open")
	
	def send(self,command):
		self.ser.write((command+"\n").encode())

	def query(self,command):
		self.lock.acquire()
		try:
			self.ser.write((command+"\n").encode())
			time.sleep(0.020)
			return self.ser.readline().decode()[:-2].split(' ')[1]
		finally:
			self.lock.release()

	@property
	def is_enabled(self):
		return bool(int(self.query('E?')))

	@is_enabled.setter
	def is_enabled(self,state):
		self.send('E '+str(int(bool(state))))

	@property
	def red(self):
		return int(self.query('R?'))

	@red.setter
	def red(self,value):
		value = min(255,max(0,value))
		self.send('R '+str(int(value)))

	@property
	def green(self):
		return int(self.query('G?'))

	@green.setter
	def green(self,value):
		value = min(255,max(0,value))
		self.send('G '+str(int(value)))

	@property
	def blue(self):
		return int(self.query('B?'))

	@blue.setter
	def blue(self,value):
		value = min(255,max(0,value))
		self.send('B '+str(int(value)))

	def close(self):
		if self.ser:
			self.ser.close()
	
if __name__=='__main__':
	lightCtrl = LightCtrl()