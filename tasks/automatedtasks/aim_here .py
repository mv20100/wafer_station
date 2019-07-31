import time
from .basetask import Task
import numpy as np
import scipy

#folder = r'G:/Utilisateurs/Manip/Desktop/data/'


class Aim_here(Task):
	"""Aim activation laser."""


	def worker(self):
		self.running = True
		print("Automated task running")
		if self.dm.ldd.key_switch:
			print('Aiming')
			self.dm.ldd.current_set_point = 0
			self.dm.ldd.output = True
			time.sleep(3.5)
			self.dm.ldd.current_set_point = 800
			time.sleep(20) # Activation time
			self.dm.ldd.current_set_point = 0
			self.dm.ldd.output = False
		else: print('Key Switch Off!')
		print('Done')


		print("Automated task done")
