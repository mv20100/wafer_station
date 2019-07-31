import time
from .basetask import Task
import numpy as np
from lmfit.models import LinearModel, GaussianModel
import os

def fit_cesium(x,y):
    bg = LinearModel()
    p1 = GaussianModel(prefix='p1_')
    p2 = GaussianModel(prefix='p2_')
    model = bg + p1 + p2
    params = bg.guess(np.delete(y, np.s_[10:-10], 0),x=np.delete(x, np.s_[10:-10], 0))
    bg_out = bg.fit(np.delete(y, np.s_[10:-10], 0),x=np.delete(x, np.s_[10:-10], 0),params=params)
    bg_y = bg_out.model.func(x=x,**bg_out.params)
    params.update(p1.make_params())
    params.update(p2.make_params())
    span = max(x) - min(x)
    peak_amplitude = - (max(y-bg_y) - min(y-bg_y))
    default_sigma = span/20.
    default_amplitude = peak_amplitude*default_sigma*np.sqrt(2*np.pi)
    default_p2_center = x[np.argmin(y-bg_y)]
    default_p1_center = default_p2_center + 250.
    params['p1_amplitude'].set(default_amplitude/2.,max=0)
    params['p2_amplitude'].set(default_amplitude,max=0)
    params['p1_sigma'].set(default_sigma, max = span/6., min = span/40.)
    params['p2_sigma'].set(default_sigma, max = span/6., min = span/40.)
    params['p1_center'].set(default_p1_center,min=np.quantile(x,0.05),max=np.quantile(x,0.95))
    params['p2_center'].set(default_p2_center,min=np.quantile(x,0.05),max=np.quantile(x,0.95))
    params.add('spacing', expr='p1_center-p2_center', min=span/6., max=3*span/4.)
    #params.add('spacing', expr='p2_center-p1_center', min=span/6., max=3*span/4.)
    params.add('peak_ratio', expr='p1_amplitude/p2_amplitude', min=0.4, max=0.6)
    out = model.fit(y,x=x,params=params)
    return out

class FitCesium(Task):
	"""Fit cesium lines."""

	header = [	'cell_id','Time (s)','Contrast (%)',
				'P1 FWHM (MHz)','P2 FWHM (MHz)',
				'P1 center (1)','P2 center (1)',
				'P1 height (V)','P2 height (V)',
				'BG intercept (V)','BG slope (V/1)',
				'chisqr']

	def __init__(self,*args,**kwargs):
		Task.__init__(self,*args,**kwargs)

	def worker(self):
		self.running = True
		print("Automated task running")

		#cell = self.cm.getCell('T01GM')
		self.dm.camera.stop_capture()
		self.dm.light.s1.setChecked(False)
		dirname = r"G:/Utilisateurs/Manip/Desktop/data/"
		filename = 'fit_results.csv'
		log_file = open(os.path.join(dirname,filename),'a')
		if os.stat(os.path.join(dirname,filename)).st_size == 0:
			log_file.write(','.join(self.header) + "\n")

		# while self.running:
		for cell in self.cm.cellList:
			if cell.get_point('OPT') != None:
				cell.slot.moveTo(cell.get_point('OPT')['coords'],self.dm.getDevice('Spectro').coords,wait=True)
				contrast = self.dm.picoscope.get_contrast()*100
				cell.contrast = contrast
				if contrast > 5.:
					x, _, y, _, _ = self.dm.picoscope.get_averaged_data(clear=False)
					out = fit_cesium(x, y)
					p1_fwhm_mhz = 1168.0 * out.params['p1_fwhm'].value / out.params['spacing'].value
					p2_fwhm_mhz = 1168.0 * out.params['p2_fwhm'].value / out.params['spacing'].value
					print(f'{cell.cell_id} : Cst={round(contrast,2)} % ; FWHM={round(p1_fwhm_mhz,2)} MHz ; chisqr {out.chisqr}')
					self.dm.picoscope.curve_fit.setData(x,out.best_fit)
					self.dm.picoscope.curve_fit_data.setData(x,out.data)
					self.dm.picoscope.curve_fit_init.setData(x,out.init_fit)
					data_array = [	cell.cell_id, time.time(), contrast,
									p1_fwhm_mhz, p2_fwhm_mhz,
									out.params['p1_center'].value, out.params['p2_center'].value,
									out.params['p1_height'].value, out.params['p2_height'].value,
									out.params['intercept'].value, out.params['slope'].value,
									out.chisqr]
					if out.chisqr > 0.0016:
						print('Fit failed')
						filename = "failed_fit_data " + time.strftime('%Y-%m-%d %H%M')+'.csv'
						np.savetxt(os.path.join(dirname,filename),np.vstack([x,y]).transpose(),delimiter=',',header=cell.cell_id)
				else:
					data_array = [	cell.cell_id, time.time(), contrast,
									np.nan, np.nan,
									np.nan, np.nan,
									np.nan, np.nan,
									np.nan, np.nan,
									np.nan]
				log_file.write( ','.join( list(map(str,data_array)) ) + "\n" )

			if not self.running:
				print("Exiting")
				break
		log_file.close()
		self.dm.camera.start_capture()
		print("Automated task done")
