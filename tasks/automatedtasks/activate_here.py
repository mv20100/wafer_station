import time
from .basetask import Task
import numpy as np
import scipy

#folder = r'G:/Utilisateurs/Manip/Desktop/data/'
act_current = 5000 # mA
act_time = 15 # s
print("Activation current: {:d} mA, Duration: {:d} s".format(act_current,act_time))

class Activate_here(Task):
	"""Activate."""

	def __init__(self,*args,**kwargs):
		Task.__init__(self,*args,**kwargs)

	def worker(self):
		self.running = True
		print("Automated task running")
		if self.dm.ldd.key_switch:
			print('Activating')
			self.dm.ldd.current_set_point = 0
			self.dm.ldd.output = True
			time.sleep(3.5)
			self.dm.ldd.current_set_point = act_current
			time.sleep(act_time) # Activation time
			self.dm.ldd.current_set_point = 0
			self.dm.ldd.output = False
		else: print('Key Switch Off!')
		print('Done')


		print("Automated task done")
