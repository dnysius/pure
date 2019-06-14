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

global tstep
tstep =  3.999999999997929e-08  ## timestep
# sorting file names for .csv files, (stackoverflow.com/questions/19366517/)
_nsre = re.compile('([0-9]+)')
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(_nsre, s)]  
    
class Peak:
     
     def __init__(self, mypath):
          s = mypath.split(sep='\\')
          self.mypath = mypath
          if s[-1] == '':
               self.title = s[-2]
          else:
               self.title = s[-1]
          
          self.ftype='npy'
          self.fnames = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f[-3:] == self.ftype[-3:]]
          self.fnames.sort(key=natural_sort_key)
          self.signal_data = np.empty(shape=(len(self.fnames), len(self.__loadf(0)[:,0]), 2))
#          lenZ = len(self.signal_data[:, 0, 0])
          lenY = len(self.signal_data[0,:,0])
#          lenX = len(self.signal_data[0,0,:])
          for i in range(len(self.fnames)):
               xy = self.__loadf(i)
               self.signal_data[i, :, :] = xy
          self.signal_data = self.signal_data[:, lenY//2:, :]
               
     def __loadf(self, i):
          if self.ftype=='.csv' or self.ftype=='csv':
               xy = np.loadtxt(open(join(self.mypath,self.fnames[i]), "rb"), delimiter=',', skiprows=0)
          else:
               xy = np.load(open(join(self.mypath,self.fnames[i]), "rb"))
          if self.ftype=='.npz' or self.ftype=='npz':
               xy = xy[xy.files[0]]
                    
          return xy
     
     
if __name__ == '__main__':
     fpath = 'C:\\Users\\dionysius\\Desktop\\PURE\\pure\\data\\3FOC9cm'
     foc3 = Peak(fpath)