import os, glob, inspect, importlib, traceback
from . import basetask
print("Reading available automated tasks:")

thisDir =  os.path.dirname(os.path.abspath(__file__))
autotaskspath = os.path.join(thisDir,"*.py")

tasks = {}

for filename in glob.glob(autotaskspath):
			modulename = os.path.splitext(os.path.basename(filename))[0]
			if modulename.startswith("__"):
				continue
			# module = __import__('.'+modulename, locals(), globals())
			try:
				module = importlib.import_module('tasks.automatedtasks.'+modulename)
				importlib.reload(module)
				for name, obj in inspect.getmembers(module):
					if inspect.isclass(obj) and issubclass(obj,basetask.Task) and obj is not basetask.Task:
						print('  -'+name)
						tasks.update({name:obj})
			except Exception as e:
				print('### Error loading task ###')
				print(e)
				traceback.print_exc()
