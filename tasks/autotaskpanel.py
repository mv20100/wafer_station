# import tasks.automation
import apscheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree
import inspect, glob, os, importlib
from . import automatedtasks


class AutoTaskPanel(object):

	task = None

	def __init__(self, cell_manager = None, device_manager = None):   
		self.cell_manager = cell_manager
		self.device_manager = device_manager
		self.scheduler = BackgroundScheduler(executors={'default':ThreadPoolExecutor(1)})
		self.scheduler.start()
		self.param_group = pTypes.GroupParameter(name = 'Automated tasks')
		self.running_param = Parameter.create(name='Running', type='bool',value=True)
		self.param_group.addChild(self.running_param)
		self.add_group_param = Parameter.create(name='Add job', type='group', expanded = False)
		refresh_param = Parameter.create(name='Refresh list', type='action')
		self.job_select_param = Parameter.create(name='Selected task', type='list',values= {"":None})
		self.job_select_param.setLimits(automatedtasks.tasks)
		self.job_doc_param = Parameter.create(name='Description',type='text',readonly=True,expanded=False)
		self.trigger_select_param = Parameter.create(name='Trigger', type='list',values=['Once','Interval'],value='Once')
		self.interval_param = Parameter.create(name='Interval (min)', type='float',value=5)
		self.add_param = Parameter.create(name='Start', type='action')
		self.add_group_param.addChildren([refresh_param,self.job_select_param,self.job_doc_param,self.trigger_select_param,self.interval_param,self.add_param])
		self.param_group.addChild(self.add_group_param)
		self.jobs_param = Parameter.create(name='Jobs', type='group')
		self.param_group.addChild(self.jobs_param)
		self.add_param.sigActivated.connect(self.add_job)
		self.running_param.sigValueChanged.connect(self.pause_resume)
		self.trigger_select_param.sigValueChanged.connect(self.display_interval)
		self.display_interval()
		self.param_group.sigTreeStateChanged.connect(self.change)
		refresh_param.sigActivated.connect(self.on_refresh_task_list)

	def pause_resume(self,param):
		if param.value():
			self.scheduler.resume()
			print('Scheduler resumed')
		else:
			self.scheduler.pause()
			print('Scheduler paused (wait for task to finish!)')

	def change(self,param,changes):
		for param, change, data in changes:
			if param is self.job_select_param: self.job_doc_param.setValue(str(param.value().__doc__))

	def on_refresh_task_list(self):
		print("Reloading automated task list")
		importlib.reload(automatedtasks)
		self.job_select_param.setLimits(automatedtasks.tasks)

	def add_job(self):
		job_class = self.job_select_param.value()
		if self.trigger_select_param.value() == 'Interval': 
			job = job_class(self.cell_manager,self.device_manager,self.scheduler,job_class.__name__,trigger='interval',interval=self.interval_param.value())
		else:
			job = job_class(self.cell_manager,self.device_manager,self.scheduler,job_class.__name__,trigger=None)
		self.jobs_param.addChild(job.param,autoIncrementName=True)

	def display_interval(self):
		if self.trigger_select_param.value() == 'Interval': self.add_group_param.insertChild(self.add_param,self.interval_param)
		else: self.add_group_param.removeChild(self.interval_param)
