# -*- coding: utf-8 -*-
"""
Created on Thu May 23 14:04:23 2019

@author: dionysius
"""

import numpy as np
import matplotlib.pyplot as plt
from os import listdir, mkdir, getcwd
from os.path import isfile, join
from angle import angle_change
# get names of files in target directory
mypath = "C:\\Users\\dionysius\\Desktop\\PURE\\may24\\FLAT\\clean"
fnames = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f[-4:] == '.csv']

signal_data = []
for name in fnames:
     signal_data.append(np.loadtxt(open(mypath+"\\"+name, "rb"), delimiter=",", skiprows=0))
     

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
     peak_width = 2000  # in units of indices
     peak_threshold = .5 # volts
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

def add_peaks(sdata):
     peak_totals = []
     for i in range(len(sdata)):
          ind, lst = peaks(sdata[i])
          peak_totals.append(np.sum(lst))  # ADD ALL? OR JUST FIRST TWO: lst[0:2]
     return peak_totals
     
def display_animation(signal_data):
     for i in range(len(signal_data)):
          ind, lst = peaks(signal_data[i])
          plt.plot(signal_data[i][:, 0], abs(signal_data[i][:,1]))
          plt.scatter(signal_data[i][ind,0],abs(signal_data[i][ind, 1]), s=10, c='goldenrod')
          plt.pause(.5)
          plt.clf()

          

def pk_avg():
     pks = peak_average(signal_data)
     deg = np.array([0,2,4,6,8,10,12,14,15], float)
     plt.plot(deg, pks)

     
def pk_tot():
     pks = add_peaks(signal_data)
     deg = np.array([0,2,4,6,8,10,12,14,15], float)
     plt.plot(deg, pks)
     
     
def plot_sdata():
     for i in range(len(signal_data)):
          plt.figure()
          plt.plot(signal_data[i][:,0], signal_data[i][:,1])

#pk_tot()  # check the total added peak values against angle
display_animation()  # check if peaks are correctly identified