# import threading
from datetime import datetime
import apscheduler
from apscheduler.triggers.date import DateTrigger
from pyqtgraph.parametertree import Parameter

class Task(object):
	"""This is the abstract Task class that all other tasks should inherit"""
	def __init__(self, cell_manager, device_manager,scheduler,label='Blabla',trigger='interval',interval=0.1):
		self.dm = device_manager
		self.cm = cell_manager
		self.scheduler = scheduler
		self.running = False
		self.label = label
		self.interval = interval
		self.param = Parameter.create(name=label+'-', type='group',expanded=False)
		kargs = {}
		if trigger == 'interval':
			self.interval_param = Parameter.create(name='Interval (min)', type='float',value=self.interval)
			self.interval_param.sigValueChanged.connect(self.change_interval)
			self.param.addChild(self.interval_param)
			kargs = {'minutes':interval}
		self.delete_param = Parameter.create(name='Delete', type='action')
		self.param.addChild(self.delete_param)
		self.job_id = self.__class__.__name__+str(id(self))
		self.job = self.scheduler.add_job(self.worker, trigger,
										id=self.job_id,
										next_run_time=datetime.now(),
										misfire_grace_time=600,
										coalesce=True,
										**kargs)
		self.scheduler.add_listener(self.clean_up_callback, mask=apscheduler.events.EVENT_JOB_EXECUTED)
		self.scheduler.add_listener(self.clean_up_callback, mask=apscheduler.events.EVENT_JOB_ERROR)
		print(self.__class__.__name__+str(id(self)))
		self.delete_param.sigActivated.connect(self.delete)

	def delete(self):
		self.running = False
		try: self.job.remove()
		except: pass
		self.param.parent().removeChild(self.param)

	def clean_up_callback(self,event):
		if event.job_id == self.job_id and isinstance(self.job.trigger, DateTrigger):
			self.delete()

	def change_interval(self):
		self.job.reschedule(trigger='interval', minutes=self.interval_param.value())

	def worker(self):
		self.running = True
		print("Task started")
		#Do something
		# while self.running:
		print("Task done")
			# pass