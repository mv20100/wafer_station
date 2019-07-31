import time
import serial
import threading

class Stepper(object):

	setpoint = 0

	def __init__(self,comPort='com4'):
		self.lock = threading.Lock()
		try:
			self.ser = serial.Serial(port=comPort,baudrate=19200,timeout=5)
			time.sleep(3)
			self.setpoint = self.position
		except serial.serialutil.SerialException:
			#no serial connection
			self.ser = None
		else:
			pass

	def __del__(self):
		self.close()

	def close(self):
		if self.ser:
			self.ser.close()		

	def send(self, command):
		self.ser.write((command+"\r\n").encode())

	def query(self, command):
		self.lock.acquire()
		try:
			self.send(command)
			time.sleep(0.020)
			return self.ser.readline()[:-2]
		finally:
			self.lock.release()

	@property
	def position(self):
		return int(self.query("P?"))

	@position.setter
	def position(self,new_pos):
		self.send("P {:d}".format(new_pos))
		self.setpoint = new_pos

if __name__=='__main__':
	stepper = Stepper()