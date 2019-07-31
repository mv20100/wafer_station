import picoscope, time
import matplotlib.pyplot as plt
import numpy as np
from picoscope.ps3000a import PS3000a
from collections import deque
import pickle
import os.path

class Picoscope(object):
	
	mean = 32

	def __init__(self,serialNumber="CO138/046".encode()):
		self.serialNumber = serialNumber
		self.ps = PS3000a(serialNumber)

	def initialize(self):
		self.samples = 50000
		sampleFreq = 10e6 #S/s
		self.downsamp_fact = 50
		collectionTime = 5e-3 # sec
		noSamples = collectionTime*sampleFreq
		print("noSamples: "+str(noSamples))
		#Example of simple capture
		(self.sampleRate, self.nSamples)  = self.ps.setSamplingFrequency(sampleFreq, noSamples)
		print("Sampling @ %f MHz, %d samples"%(self.sampleRate/1E6, self.nSamples))
		self.ps.setChannel("A", "DC", 0.5,-0.4)
		self.ps.setChannel("B", "DC", 0.5,-0.4)
		self.ps.setChannel("C", "DC", 1.,0.0)
		self.ps.setChannel("D", "DC", 0.5,-0.4)
		self.ps.setSimpleTrigger("External",0.5, 'Rising', timeout_ms=0,delay=24260)

		array_length = int(self.samples/self.downsamp_fact)
		self.x = np.arange(array_length)
		self.meanA = np.zeros(array_length,dtype=np.float64)
		self.dataA = np.zeros((self.mean,array_length),dtype=np.float64)
		self.meanB = np.zeros(array_length,dtype=np.float64)
		self.dataB = np.zeros((self.mean,array_length),dtype=np.float64)
		self.meanC = np.zeros(array_length,dtype=np.float64)
		self.dataC = np.zeros((self.mean,array_length),dtype=np.float64)
		self.meanD = np.zeros(array_length,dtype=np.float64)
		self.dataD = np.zeros((self.mean,array_length),dtype=np.float64)

		self.ptr = 0
		self.deque = deque([],self.mean)

	def clear(self,wait=True):
		self.deque.clear()
		if wait:
			while len(self.deque)<self.mean:
				time.sleep(0.050)

	def get_averaged_data(self,clear=True):
		if clear: self.clear()
		return self.x.copy(), self.meanA.copy(), self.meanB.copy(), self.meanC.copy(), self.meanD.copy()

	def update(self):
		self.ptr=(self.ptr+1)%self.mean
		self.deque.append(self.ptr)
		self.ps.runBlock()
		self.ps.waitReady()
		self.dataA[self.ptr,:] = self.ps.getDataV("A", self.samples).reshape(-1, self.downsamp_fact).mean(axis=1)
		self.dataB[self.ptr,:] = self.ps.getDataV("B", self.samples).reshape(-1, self.downsamp_fact).mean(axis=1)
		self.dataC[self.ptr,:] = self.ps.getDataV("C", self.samples).reshape(-1, self.downsamp_fact).mean(axis=1)
		self.dataD[self.ptr,:] = self.ps.getDataV("D", self.samples).reshape(-1, self.downsamp_fact).mean(axis=1)

		if len(self.deque)>0:
			self.meanA=np.mean(self.dataA[self.deque],axis=0)
			self.meanB=np.mean(self.dataB[self.deque],axis=0)
			self.meanC=np.mean(self.dataC[self.deque],axis=0)
			self.meanD=np.mean(self.dataD[self.deque],axis=0)


	def saveData(self,filename,meta=None, clear=True):
		if clear: self.clear()
		data = {}
		data.update(meta)
		data.update({"meanA":self.meanA})
		data.update({"meanB":self.meanB})
		data.update({"meanC":self.meanC})
		data.update({"meanD":self.meanD})
		print("Saving data")
		pickle.dump(data, open(filename, 'wb'))
		print("Done")

if __name__ == "__main__":
	pico = Picoscope()
