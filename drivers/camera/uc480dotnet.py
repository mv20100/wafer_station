import sys, clr, time
sys.path.append(r'C:\Program Files\Thorlabs\Scientific Imaging\ThorCam')
clr.AddReference('uc480DotNet')
clr.AddReference('System.Runtime')
clr.AddReference('System.Runtime.InteropServices')
import uc480
import System
from System import Int32, IntPtr
from System.Runtime.InteropServices import Marshal
import numpy as np
import scipy.misc

def list_devices():
	array = System.Array[uc480.Types.CameraInformation]("")
	statusRet, array = uc480.Info.Camera.GetCameraList(array)
	print("Cameras:")
	print([f"{array.Get(i).Model} {array.Get(i).SerialNumber}" for i in range(len(array))])

list_devices()

class UC480Cam(object):

	def __init__(self):
		self.cam = uc480.Camera()
		statusRet = self.cam.Init()
		self.cam.PixelFormat.Set(uc480.Defines.ColorMode.RGB8Packed)
		if statusRet != 0: print("Init failed")
		statusRet, memID = self.cam.Memory.Allocate(Int32(0),True)
		print(f'mem ID : {memID}')
		if statusRet != 0: print("Allocate failed")
		self.imageData = None
		self.start_capture()

	def start_capture(self):
		statusRet = self.cam.Acquisition.Capture()
		if statusRet != 0: print("Capture failed")

	def stop_capture(self):
		statusRet = self.cam.Acquisition.Stop()

	@property
	def exposure(self):
		 statusRet, exp = self.cam.Timing.Exposure.Get(0)
		 return round(exp,3)

	@exposure.setter
	def exposure(self,exp):
		statusRet = self.cam.Timing.Exposure.Set(float(exp))

	@property
	def framerate(self):
		 statusRet, fr = self.cam.Timing.Framerate.Get(0)
		 return round(fr,3)

	@framerate.setter
	def framerate(self,fr):
		statusRet = self.cam.Timing.Framerate.Set(float(fr))

	@property
	def pixelclock(self):
		 statusRet, pc = self.cam.Timing.PixelClock.Get(0)
		 return round(pc,3)

	@pixelclock.setter
	def pixelclock(self,pc):
		statusRet = self.cam.Timing.PixelClock.Set(float(pc))

	def start(self):
		self.start_time = time.time()
		self.counter = 0
		self.cam.EventFrame += self.on_frame_event

	def stop(self):
		self.cam.EventFrame -= self.on_frame_event

	def on_frame_event(self,cam,eventArgs):
		#print(cam.Timing.Framerate.GetCurrentFps(0))
		self.get_image()

	def get_image(self):
		_, memID = self.cam.Memory.GetActive(Int32(0))
		self.cam.Memory.Lock(memID)
		outarray = System.Array[System.Byte](())
		ErrChk, tmp = self.cam.Memory.CopyToArray(memID, outarray)
		self.imageData = np.empty(len(tmp),dtype=np.uint8)
		Marshal.Copy(tmp, 0,IntPtr.__overloads__[int](self.imageData.__array_interface__['data'][0]), len(tmp))
		self.cam.Memory.Unlock(memID)

	def save_image(self,filename='test.jpg'):
		self.stop()
		self.get_image()
		scipy.misc.imsave(filename, self.imageData.reshape(1024,1280,3).transpose(1,0,2))
		self.start()

if __name__ == '__main__':
	camera = UC480Cam()