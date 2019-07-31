import thorlabs_apt as apt
import threading

class MyMotor(apt.Motor):

	def __init__(self,*args,**kargs):
		self.reversed = kargs.pop('reversed',False)
		super(MyMotor,self).__init__(*args,**kargs)
		self.min_vel, self.accn, self.max_vel = self.get_velocity_parameters()
		_, self.max_pos, _, _ = self.get_stage_axis_info()
		print(f'Max vel : {self.max_vel}, Max pos : {self.max_pos}')

	def set_velocity(self,velocity):
		self.set_velocity_parameters(self.min_vel, self.accn, min(velocity,self.max_vel))

	def reset_velocity(self):
		self.set_velocity_parameters(self.min_vel, self.accn, self.max_vel)

	@property
	def position(self):
		if self.reversed: return self.max_pos - super(MyMotor,self).position
		else: return super(MyMotor,self).position

	def move_to(self, value, blocking=False):
		if self.reversed: super(MyMotor,self).move_to(self.max_pos - value,blocking=blocking)
		else: super(MyMotor,self).move_to(value,blocking=blocking)

class Stage(object):

	def __init__(self,x_serial = 45874656, y_serial = 45874425):
		self.x_lts = MyMotor(x_serial,reversed=True)
		self.y_lts = MyMotor(y_serial)

	@property
	def position(self):
		return self.x_lts.position, self.y_lts.position

	@position.setter
	def position(self,new_position):
		self.move_to(new_position)

	def move_to(self,new_position,wait=True):
		def thread(axis_lts,position):
			axis_lts.move_to(position, blocking=wait)
		t1 = threading.Thread(name="thread",target=thread,args=(self.x_lts,new_position[0]))
		t2 = threading.Thread(name="thread",target=thread,args=(self.y_lts,new_position[1]))
		t1.start()
		t2.start()
		if wait:
			t1.join()
			t2.join()

	def home(self,wait=True):
		def thread(axis_lts):
			axis_lts.move_home(blocking=wait)
		t1 = threading.Thread(name="thread",target=thread,args=(self.x_lts,))
		t2 = threading.Thread(name="thread",target=thread,args=(self.y_lts,))
		t1.start()
		t2.start()
		if wait:
			t1.join()
			t2.join()		

if __name__ == '__main__':
	stage = Stage(x_serial = 45874656, y_serial = 45874425)