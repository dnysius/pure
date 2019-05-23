# -*- coding: utf-8 -*-
"""
Created on Thu May 23 14:04:23 2019

@author: dionysius
"""

import scipy as sc
import numpy as np
import matplotlib.pyplot as plt
from os import listdir, mkdir, getcwd
from os.path import isfile, join
from time import sleep

# get names of files in target directory
mypath = "D:\\"
fnames = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f[-4:] == '.csv']

signal_data = []
for name in fnames:
     signal_data.append(np.loadtxt(open(name, "rb"), delimiter=",", skiprows=0))
     

"""
finding peaks
"""
def peaks(x):
     '''
     x - signal as numpy array
     '''
     V = abs(x[:,1])  # absolute values of voltages
     peak_ind_list = []
     peak_val_list = []
     peak_width = 50  # in units of indices
     peak_threshold = 1.4  # volts
     Lcount = 0
     count = 1
     while count <= len(x[:,:])-1:
          if V[count] >= peak_threshold:
               if V[count] == max(V[Lcount: (count+peak_width)]):
                    peak_ind_list.append(count)
                    peak_val_list.append(V[count])
                    Lcount = count + peak_width
                    count = Lcount + 1
               else:
                    count += 1
          else:
               count += 1

     return peak_ind_list, peak_val_list


def peak_average(sdata):
     peak_averages = []
     for i in range(len(sdata)):
          ind, lst = peaks(sdata[i])
          peak_averages.append(np.mean(lst))
     return peak_averages
          
     
def display_animation(sdata):
     for i in range(len(sdata)):
          ind, lst = peaks(sdata[i])
          plt.plot(sdata[i][:, 0], abs(sdata[i][:,1]))
          plt.scatter(sdata[i][ind,0],abs(sdata[i][ind, 1]), s=10)
          plt.pause(.5)
          plt.clf()

          
pks = peak_average(signal_data)
