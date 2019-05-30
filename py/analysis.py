# -*- coding: utf-8 -*-
"""
Created on Thu May 23 14:04:23 2019

@author: dionysius
Angle-dependence experiment analysis code
"""

from scipy.signal import hilbert
import scipy.optimize as sc
import numpy as np
import matplotlib.pyplot as plt
from os import listdir, mkdir
from os.path import isfile, isdir, join
import re
from time import clock

# sorting file names in, (stackoverflow.com/questions/19366517/)
_nsre = re.compile('([0-9]+)')

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(_nsre, s)]  
    
# define classes
    
class Micrometer:
     '''
     Calibrates angle versus micrometer reading
     Methods list:
     self.fit
     self.calibration_curve
     self.dtheta
     self.d
     self.a
     self.graph_vals
     '''
     
     def __init__(self, zero, step_size):
          '''
          zero: the micrometer reading corresponding to 0 degree angle
          step_size: increments of the angle used in the experiment (e.g every 2 degree)
          
          self.mic: micrometer readings
          self.angle: angle readings
          self.popt, self.popt1: parameter matrices for original and new data, respectively
          self.pcov, self.pcov1: covariance matrices for original and new data, respectively
          self.vals: 2D array containing new data points (micrometer reading vs angle)
          '''
          self.mic = np.array([24.15,20.65,18.53,14.12,10.36,7,3.48,0.56,0], float)
          self.angle = np.array([0,2,4,6,8,10,12,14,15], float)
          self.popt, self.pcov = sc.curve_fit(self.__d, self.mic, self.angle, (1,1))
          self.popt1, self.pcov1 = sc.curve_fit(self.__d, self.angle, self.mic, (1, 1))
          deg = np.arange(0,16, step_size)  # setup is limited to max angle of 15 deg
          self.angle = deg
          self.vals = self.a(zero, deg)
          self.mic = self.vals[:, 1]


     def __d(self, x, a, b):
          '''
          Linear model function
          x: micrometer readings
          a, b: curve fit parameters
          return: float
          '''
          return a*x+ b
     
     
     def fit(self, mic, ang):
          '''
          Overwrites curve fit parameters found with new data
          mic: micrometer readings
          ang: angle readings
          '''
          self.popt, self.pcov = sc.curve_fit(self.__d, mic, ang, (1,1))

     
     def __calibration_curve(self):
          '''
          Displays the original calibration data points and curve fit
          (angle vs micrometer reading)
          '''
          plt.figure(figsize=[8,6])
          plt.scatter(self.mic, self.angle, c='grey')
          plt.plot(self.mic, self.__d(self.mic,*self.popt), c='goldenrod')
          plt.xlabel('micrometer reading (mm)')
          plt.ylabel('angle (degree)')
          plt.title('micrometer calibration curve')
          plt.show()
          
          
     def calibration_curve(self):
          '''
          Displays the calibration data points and curve fit for the new range of angles
          (micrometer readings vs angle)
          '''
          plt.figure(figsize=[8,6])
          plt.scatter(self.angle, self.mic, c='grey')
          plt.plot(self.angle, self.__d(self.angle,*self.popt1), c='goldenrod')
          plt.ylabel('micrometer reading (mm)')
          plt.xlabel('angle (degree)')
          plt.title('micrometer calibration curve')
          plt.show()
     
          
     def dtheta(self, x1, x2):
          '''
          Outputs the change in angle between two micrometer readings
          x1, x2: micrometer readings
          return: float
          '''
          return self.popt[0]*(x2-x1)
     
     
     def d(self, x):
          '''
          Outputs angle values corresponding to micrometer readings
          x: micrometer readings
          return: numpy array
          '''
          return self.popt[0]*x + self.popt[1]
     
     
     def a(self, zero, deg):
          '''
          Outputs micrometer readings for the desired angle values
          zero: micrometer reading corresponding to 0 degree angle
          deg: desired angle values
          return: numpy array
          '''
          a = (np.transpose(np.array([deg])), np.transpose(np.array([self.popt1[0]*deg + zero])))
          return np.hstack(a)
     
     
     def graph_vals(self):
          '''
          Displays new calibration curve
          (micrometer readings vs angle)
          '''
          plt.figure(figsize=[8,6])
          plt.scatter(self.vals[:, 0], self.vals[:, 1], c='grey')
          plt.plot(self.vals[:,0], self.__d(self.vals[:,0],self.popt1[0], self.vals[0,1]), c='goldenrod')
          plt.ylabel('micrometer reading (mm)')
          plt.xlabel('angle (degree)')
          plt.title('new micrometer readings')
          plt.show()



class Signal:
     '''
     Object for individual waveforms for a given transducer
     Methods list:
     self.peaks_list
     self.display
     self.fft
     '''
     
     def __init__(self, xy, threshold, width):
          '''
          xy: numpy array
          threshold: minimum voltage for a peak to be identified
          width: range of x-values around a peak for checking for higher points in vicinity
          
          self.xy: signal as numpy array
          self.name: name of current signal waveform
          self.peak_ind: array indices of peak points
          self.peak_val: values of each peak
          '''
          self.xy = np.copy(xy)  # will be changed by class methods
          self.name = ''
          self.peak_ind, self.peak_val = self.peaks_list(threshold, width)
          
         
     def peaks_list(self, threshold, width):
          '''
          Find the peaks in the signal
          threshold: minimum voltage to detect
          width: domain over which to take the max voltage value
          returns: list, list
          '''
          self.peak_ind = []  # indices of x values where peaks are located
          self.peak_val = []  # y values of each peak
          V = np.abs(self.xy[:,1])  # absolute values of voltages
          count = 0
          while count <= len(self.xy[:,:])-1:
               if V[count] >= threshold and (count-width) >= 0:     
                    if V[count] == max(V[(count-width): (count+width)]):
                         self.peak_ind.append(count)
                         self.peak_val.append(V[count])
                         Lcount = count + width
                         count = Lcount + 1
                    else:
                         count += 1
               else:
                    count += 1
          
          return self.peak_ind, self.peak_val
     
     
     def display(self):
          '''
          Display the current signal
          '''
          plt.figure(figsize=[10,8])
          plt.plot(self.xy[:,0], self.xy[:,1], c='grey')
          plt.scatter(self.xy[self.peak_ind, 0], self.xy[self.peak_ind, 1], c='goldenrod')
          plt.xlabel('time (s)')
          plt.ylabel('voltage (V)')
          plt.title(self.name)
          plt.show()
     
     
     def fft(self):
          '''
          Compute the FFT of the signal
          return: 1D numpy array
          '''
          y = self.xy[:, 1]
          return np.fft.fft(y)
          
     
     
class Transducer:
     '''
     Creates object that contains signal data and methods to analyze it.
     Methods list:
     self.write_all
     self.display_all
     self.graph_h
     self.graph_signal
     self.graph_fft
     self.graph_total
     '''
     def __init__(self, mypath, name):
          '''
          mypath: path leading to \\clean directory
          name: name of this setup
          
          self.mypath: path leading to \\clean directory
          self.name: name of this setup
          self.fnames: name(s) of .csv file(s) in self.mypath directory
          self.signal_data: list of Signal objects
          self.deg: list of angle values measured during the experiment
          self.threshold: minimum voltage to detect
          self.width: domain over which to take the max voltage value
          self.peak_totals: total peak voltage of first reflected wave for each angle  
          '''
          self.mypath = mypath
          self.name = name
          self.fnames = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f[-4:] == '.csv']
          self.signal_data = []
          Micro = Micrometer(24.2, 1)
          self.deg = Micro.angle
          self.threshold = .2
          self.width = 1500
          self.fnames.sort(key=natural_sort_key)
          for i in range(len(self.fnames)):
               xy = np.loadtxt(open(mypath+"\\"+self.fnames[i], "rb"), delimiter=",", skiprows=0)
               sig = Signal(xy, self.threshold, self.width)
               sig.name = "{0}_Transducer_{1}_degrees".format(self.name, self.deg[i])
               self.signal_data.append(sig)
               
          self.peak_totals = []
          self.graph_total(SAVE=False, DISPLAY=False)     
          
          
     def write_all(self):
          '''
          Saves all figures
          '''
          SAVE=True
          DISPLAY=False
          self.graph_fft(SAVE, DISPLAY)      
          self.graph_signal(SAVE, DISPLAY)
          self.graph_h(SAVE, DISPLAY)
          self.graph_total(SAVE, DISPLAY)
              
          
     def display_all(self):
          '''
          Displays all figures
          '''
          SAVE=True
          DISPLAY=False
          self.graph_fft(SAVE, DISPLAY)        
          self.graph_signal(SAVE, DISPLAY)
          self.graph_h(SAVE, DISPLAY)
          self.graph_total(SAVE, DISPLAY)
          
          
     def graph_h(self,i='all', SAVE=False, DISPLAY=True):
          '''
          Creates graph for hilbert envelope for first reflected wave in selected signal(s)
          i: int/list of indices corresponding to which signal to select, or 'all' for all
          SAVE: bool, saves to file if True
          DISPLAY: bool, outputs to screen if True
          '''
          lw = 100
          rw = 100
          plt.ioff()
          folder = self.mypath + "\\hilbert"
          if not isdir(folder):
               mkdir(folder)
          if i=='all':
               for sig in self.signal_data:
                    ind = sig.peak_ind[1]  # index of first reflected wave peak
                    wave = sig.xy[ind-lw:ind+rw, :]
                    c = hilbert(wave[:, 1])
                    fig = plt.figure(figsize=[10,8])
                    plt.plot(wave[:,0], wave[:,1],c='grey', label='signal')
                    plt.plot(wave[:,0], np.abs(c),c='goldenrod', label='hilbert envelope')
                    plt.xlabel('time (s)')
                    plt.ylabel('voltage (V)')
                    plt.title(sig.name)
                    plt.legend()
                    if SAVE is True:
                         plt.savefig(folder + "\\HIL_" +sig.name+".png", dpi=300)
                         
                    if DISPLAY is True:
                         plt.show(fig)
                         
                    elif DISPLAY is False:
                         plt.close(fig)
                         
                        
          elif isinstance(i, int) and (0 <= i < len(self.signal_data)):
               sig = self.signal_peak[i]
               ind = sig.peak_ind[1]
               wave = sig.xy[ind-lw:ind+rw, :]
               c = hilbert(wave[:, 1])
               fig = plt.figure(figsize=[10,8])
               plt.plot(wave[:,0], wave[:,1],c='grey', label='signal')
               plt.plot(wave[:,0], np.abs(c),c='goldenrod', label='hilbert envelope')
               plt.xlabel('time (s)')
               plt.ylabel('voltage (V)')
               plt.title(sig.name)
               plt.legend()
               
          elif isinstance(i, list):
               try:
                    for k in i:
                         sig = self.signal_peak[k]
                         ind = sig.peak_ind[1]
                         wave = sig.xy[ind-lw:ind+rw, :]
                         c = hilbert(wave[:, 1])
                         fig = plt.figure(figsize=[10,8])
                         plt.plot(wave[:,0], wave[:,1],c='grey', label='signal')
                         plt.plot(wave[:,0], np.abs(c),c='goldenrod', label='hilbert envelope')
                         plt.xlabel('time (s)')
                         plt.ylabel('voltage (V)')
                         plt.title(sig.name)
                         plt.legend()
                         
               except TypeError:
                   print('graph_h: index list may be out of bounds')
                    
     
     def graph_signal(self,i='all', SAVE=False, DISPLAY=True):
          '''
          Creates graph for selected signal(s)
          i: int/list of indices corresponding to selected signal, or 'all' for all
          SAVE: bool, saves to file if True
          DISPLAY: bool, outputs to screen if True
          '''
          plt.ioff()
          folder = self.mypath + "\\signals"
          if not isdir(folder):
               mkdir(folder)
          
          if i=='all':
               for sig in self.signal_data:
                    fig = plt.figure(figsize=[10,8])
                    plt.plot(sig.xy[:, 0], sig.xy[:, 1], c='grey')
                    plt.scatter(sig.xy[sig.peak_ind, 0], sig.xy[sig.peak_ind, 1], c='goldenrod', s=25)
                    plt.xlabel('time (s)')
                    plt.ylabel('voltage (V)')
                    plt.title(self.name)
                    if SAVE is True:
                         plt.savefig(folder + "\\SIG_" +sig.name+".png", dpi=300)
                    if DISPLAY is True:
                         plt.show(fig)
                    elif DISPLAY is False:
                         plt.close(fig)
                         
                         
          elif isinstance(i, int) and (0 <= i < len(self.signal_data)):
               sig = self.signal_data[i]
               fig = plt.figure(figsize=[10,8])
               plt.plot(sig.xy[:, 0], sig.xy[:, 1], c='grey')
               plt.scatter(sig.xy[sig.peak_ind, 0], sig.xy[sig.peak_ind, 1], c='goldenrod', s=25)
               plt.xlabel('time (s)')
               plt.ylabel('voltage (V)')
               plt.title(sig.name)
               plt.show(fig)
               
          elif isinstance(i, list):
               try:
                    for k in i:
                         sig = self.signal_data[k]
                         fig = plt.figure(figsize=[10,8])
                         plt.plot(sig.xy[:, 0], sig.xy[:, 1], c='grey')
                         plt.scatter(sig.xy[sig.peak_ind, 0], sig.xy[sig.peak_ind, 1], c='goldenrod', s=25)
                         plt.xlabel('time (s)')
                         plt.ylabel('voltage (V)')
                         plt.title(sig.name)
                         plt.show(fig)
                         
               except TypeError:
                   print('graph_signal: index list may be out of bounds')
                                  
               
     def graph_fft(self,i='all', SAVE=False, DISPLAY=True):
          '''
          Creates graph for FFT of each selected signal(s)
          i: int/list of indices corresponding to which signal to select, or 'all' for all
          SAVE: bool, saves to file if True
          DISPLAY: bool, outputs to screen if True
          '''
          plt.ioff()
          folder = self.mypath + "\\fft"
          if not isdir(folder):
               mkdir(folder)
          if i=='all':
               for sig in self.signal_data:
                    c = sig.fft()
                    fig = plt.figure(figsize=[10,8])
                    plt.plot(abs(c))
                    plt.title(self.name)
                    if SAVE is True:
                         plt.savefig(folder + "\\FFT_" +sig.name+".png", dpi=300)
                         
                    if DISPLAY is True:
                         plt.show(fig)
                         
                    elif DISPLAY is False:
                         plt.close(fig)
                         
                         
          elif isinstance(i,int) and (0 <= i < len(self.signal_data)):
               sig = self.signal_data[i]
               c = sig.fft()
               fig = plt.figure(figsize=[10,8])
               plt.plot(abs(c))
               plt.title(self.name)
               plt.show(fig)
               
          elif isinstance(i, list):
               try:
                    for k in i:
                         sig = self.signal_data[k]
                         c = sig.fft()
                         fig = plt.figure(figsize=[10,8])
                         plt.plot(abs(c))
                         plt.title(self.name)
                         plt.show(fig)
                         
               except TypeError:
                   print('graph_fft: index list may be out of bounds')
                    
          
     def graph_total(self, SAVE=False, DISPLAY=True):
          '''
          Creates graph for peak voltage of first reflected wave vs angle of each signal
          SAVE: bool, saves to file if True
          DISPLAY: bool, outputs to screen if True
          '''
          plt.ioff()
          self.peak_totals = []
          for sig in self.signal_data:
               lst = sig.peak_val
               self.peak_totals.append(lst[1])   
               
          folder = self.mypath + "\\profile"
          if not isdir(folder):
               mkdir(folder)

          fig = plt.figure(figsize=[10,8])
          plt.scatter(self.deg, self.peak_totals, c='goldenrod')
          plt.title(self.name)
          plt.xlabel('angle (degree)')
          plt.ylabel('peak voltage (V)')
          if SAVE is True:
               plt.savefig(folder + "\\TOT_" +self.name+".png", dpi=300)
               
          if DISPLAY is True:
               plt.show(fig)
               
          elif DISPLAY is False:
               plt.close(fig)
               
                   
               
if __name__ == "__main__":
     start = clock()
     flat_path = 'C:\\Users\\dionysius\\Desktop\\PURE\\may28\\FLAT\\clean'
     foc_path = 'C:\\Users\\dionysius\\Desktop\\PURE\\may28\\FOC\\clean'
     flat = Transducer(flat_path, "FLAT_15cm")
     foc = Transducer(foc_path, "FOC_15cm")

     print("Writing completed, {} s!".format(clock()-start))