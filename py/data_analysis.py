# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 13:08:45 2019

@author: dionysius
"""
from scipy.signal import hilbert
import scipy.optimize as sc
import numpy as np
import matplotlib.pyplot as plt
from os import listdir, mkdir
from os.path import isfile, isdir, join, dirname
import os.path
import re
import scipy.signal as signal
from time import sleep
global tstep, BSCAN_FOLDER
BSCAN_folder = "C:\\Users\\dionysius\\Desktop\\PURE\\pure\\scans\\BSCAN\\"
tstep =  3.999999999997929e-08  ## timestep
# sorting file names for .csv files, (stackoverflow.com/questions/19366517/)
_nsre = re.compile('([0-9]+)')
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(_nsre, s)]
    
def indw2time(indw):
     ## indw is the index difference between the top surface peak and the bottom surface
     ## peak, or just index of a peak
     ## outputs the time conversion
     v_m = 6420  ## aluminum speed of soudn
     return v_m*indw*tstep/2

class Peak:
     def __init__(self, mypath):
          s = mypath.split(sep='\\')
          self.mypath = mypath
          if s[-1] == '':
               self.title = s[-2]
          else:
               self.title = s[-1]
               
          self.folder = join(mypath, "analysis/")
          if not isdir(join(mypath, "analysis/")):
               mkdir(join(mypath, "analysis/"))
               
          self.ftype='npy'
          self.fnames = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f[-3:] == self.ftype[-3:]]
          self.fnames.sort(key=natural_sort_key)
          self.angles = np.linspace(0, 30,len(self.fnames))
          self.angle_step = 30/len(self.fnames)
          self.signal_data = np.empty(shape=(len(self.fnames), len(self.__loadf(0)[:,0]), 2))
          lenY = len(self.signal_data[0,:,0])
          for i in range(len(self.fnames)):
               xy = self.__loadf(i)
               self.signal_data[i, :, :] = xy
          self.signal_data = self.signal_data[:, lenY//2:, :]  ## take the latter half of the signals
               
     def __loadf(self, i):
          if self.ftype=='.csv' or self.ftype=='csv':
               xy = np.loadtxt(open(join(self.mypath,self.fnames[i]), "rb"), delimiter=',', skiprows=0)
          else:
               xy = np.load(open(join(self.mypath,self.fnames[i]), "rb"))
          if self.ftype=='.npz' or self.ftype=='npz':
               xy = xy[xy.files[0]]
                    
          return xy


     def plot_peak(self, i, start, width, x1=0, x2=-1):
          ## angle dependence
          if x2 == -1:
               x2 = width-1
               
          end = start + width
          y = np.abs(self.signal_data[i,start:end,1])
          self.fig = plt.figure(figsize=[15,13])
          plt.plot(y, c='goldenrod', ls='--', alpha=.7, label='signal')
          plt.axvline(x=x1,c='grey', label="x1={}".format(x1))
          plt.axvline(x=x2,c='grey', label='x2={}'.format(x2))
          plt.title('{0}deg, {1}m, ({2}, {3})'.format(self.angles[i], round(indw2time(x2-x1), 6), start, width))
          plt.xlabel('time (s)')
          plt.ylabel('voltage (V)')
          plt.legend()
          plt.show(self.fig)

     def analyze_peak(self, i, start, width, x1=0, x2=-1):
          self.plot_peak(i, start,width, x1, x2)
          cmd = input("//\t")
          if cmd == 's':
               ## save fig
               self.fig.savefig(join(self.folder, "{0}.png".format(i)))
               print('done saving')
               
          elif cmd == 'z' or cmd=='':
               ## zoom
               sind = input("\nstart (default {0}): \t".format(start))
               wind = input("\nwidth (default {0}): \t".format(width))
               try:
                    if sind =='':
                         pass     
                    else:
                         start = int(sind)
                         
                    if wind == '':
                         pass
                    else:
                         width= int(wind)
                         
                    self.analyze_peak(i, start, width, x1, x2)
                    
               except:
                    print("ERROR must enter an integer, or integer entered may be out of range")
                    
          elif cmd == 'c' or cmd=='cursor':
               ## move cursors
               nx1 = input("x1 (current {})\t".format(x1))
               nx2 = input("x2 (current {})\t".format(x2))
               if nx1 == '':
                    pass
               else:
                    x1 = int(nx1)
               if nx2 =='':
                    pass
               else:
                    x2 = int(nx2)
                    
               self.analyze_peak(i, start, width, x1, x2)
          elif cmd=='esc' or cmd=='exit' or cmd=='x':
               print("Exit")
          else:
               print("invalid input")
               self.analyze_peak(i, start, width, x1, x2)
          
     def ang_bscan(self, domain=(0, -1), DISPLAY=True, SAVE=True, vmin=0, vmax=1):
          ## Performs B-scan for given set of angles
          ## domain is a tuple with start and end points of the signal
          ## vmin/vmax is min/max of color range for imshow()
          START = domain[0] ## offset the start of the signal; don't want to include transmitted part
          END = domain[1]
          if END == -1:
               END = len(self.signal_data[0, :, 1]) - 1
          else:
               pass
          print()
          y = np.abs(self.signal_data[:,START:END, 1]) / np.max(np.abs(self.signal_data[:,START:END, 1]).flatten())
          bscan = np.transpose(y)  ## take transpose, rename variable
          plt.ioff()
          fig = plt.figure(figsize=[14,8])
          ax = fig.add_subplot(1, 1, 1)
          ax.set_title(self.title)
          major_ticks = np.arange(tstep*START, tstep*END, tstep*((END-START)//10))
          minor_ticks = np.arange(tstep*START, tstep*END, tstep*((END-START)//50))
          ax.imshow(bscan, cmap='gray',origin='upper', aspect='auto', alpha=.9, extent=[0, 35, tstep*END, tstep*START], vmin = vmin, vmax = vmax)
          ax.set_xlabel('angle (degrees)')
          ax.set_ylabel('time (s)')
          ax.set_yticks(major_ticks)
          ax.set_yticks(minor_ticks, minor=True)
          ax.grid(True, axis='y', which="major", alpha=.5)
          ax.grid(True, axis='y', which="minor", alpha=.2, linestyle="--")
          ax.grid(True, axis='x', which="major", alpha=.2, linestyle="--")
          if SAVE == True:
               plt.savefig(join(BSCAN_folder, self.title+'.png'), dpi=300)
          if DISPLAY == True:
               plt.show(fig)
          elif DISPLAY == False:
               plt.close(fig)
          plt.ion()
     
     
if __name__ == '__main__':
     fpath = "C:\\Users\\dionysius\\Desktop\\PURE\\pure\\data\\30deg\\3FOC5in"
     foc = Peak(fpath)
     plt.figure(figsize=[10,8])
     plt.plot(foc.signal_data[-1,:,1])
     plt.show()
#     foc3.analyze_peak(0,0,-1)
     """
     Simplest way is to have x1 x2 axvlines() (moveable via interactive matplotlib)
     and these two x positions are printed ON the plot itself, as well as the corresponding y values.
     
     
     sin(\alpha / 2)=.514c/fD --> calculate surface area covered for flat transducer
     focused trans: find alpha/2 using DIAMETER and the focal depth (3in for ex).
     """
          
