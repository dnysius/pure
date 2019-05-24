# -*- coding: utf-8 -*-
"""
Created on Thu May 23 14:04:23 2019

@author: dionysius
"""

import numpy as np
import matplotlib.pyplot as plt
from os import listdir
from os.path import isfile, join


class Transducer:
     '''
     fnames: name of csv files in working directory
     signal_data: python list consisting of csv files as numpy arrays
     '''
     def __init__(self, mypath, name):
          self.name = name
          self.fnames = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f[-4:] == '.csv']
          self.signal_data = []
          for name in self.fnames:
               self.signal_data.append(np.loadtxt(open(mypath+"\\"+name, "rb"), delimiter=",", skiprows=0))
     
     
     def peaks(self, x):
          '''
          find the peaks, output indices and the values of the points
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
     
     
     def peak_average(self):
          '''
          Takes a single signal waveform, output the mean of the peak values
          '''

          peak_averages = []
          for i in range(len(self.signal_data)):
               ind, lst = self.peaks(self.signal_data[i])
               peak_averages.append(np.mean(lst))
          return peak_averages
     
     
     def add_peaks(self):
          '''
          Takes a single signal waveform, and adds together all the peak values
          '''
          peak_totals = []
          for i in range(len(self.signal_data)):
               ind, lst = self.peaks(self.signal_data[i])
               peak_totals.append(np.sum(lst))  # ADD ALL? OR JUST FIRST TWO: lst[0:2]
          return peak_totals
     
          
     def display_animation(self):
          '''
          Displays the plots of each waveform stored in signal_data, along
          with the identified peaks.
          '''
          for i in range(len(self.signal_data)):
               ind, lst = self.peaks(self.signal_data[i])
               plt.figure()
               plt.plot(self.signal_data[i][:, 0], abs(self.signal_data[i][:,1]),c='grey')
               plt.scatter(self.signal_data[i][ind,0],abs(self.signal_data[i][ind, 1]), s=10, c='goldenrod')
               plt.xlabel('time (s)')
               plt.ylabel('voltage (V)')
               
               
     def pk_avg(self):
          '''
          Plots the average peak values as a function of angle 
          '''
          pks = self.peak_average()
          deg = np.array([0,2,4,6,8,10,12,14,15], float)
          plt.figure(figsize=[8,6])
          plt.plot(deg, pks, c='grey')
          plt.title(self.name)
          plt.xlabel('angle (degree)')
          plt.ylabel('average peak voltage (V)')
          
          
     def pk_tot(self):
          '''
          Plots the total peak values as a function of angle
          '''
          pks = self.add_peaks()
          deg = np.array([0,2,4,6,8,10,12,14,15], float)
          plt.figure(figsize=[8,6])
          plt.plot(deg, pks, c='goldenrod')
          plt.title(self.name)
          plt.xlabel('angle (degree)')
          plt.ylabel('total peak voltage (V)')


if __name__ == "__main__":
     path = "C:\\Users\\dionysius\\Desktop\\PURE\\may24\\FLAT\\clean"
     path1 = "C:\\Users\\dionysius\\Desktop\\PURE\\may24\\FOC\\clean"
     flat = Transducer(path, "Flat Transducer")
     focused = Transducer(path1, "Focused Transducer")
     flat.pk_tot()
     focused.pk_tot()
     flat.pk_avg()
     focused.pk_avg()
