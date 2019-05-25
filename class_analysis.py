# -*- coding: utf-8 -*-
"""
Created on Thu May 23 14:04:23 2019

@author: dionysius

Creates object that contains signal data and methods to analyze it.
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
          self.deg = np.array([0,2,4,6,8,10,12,14,15], float)
          self.pk_dst = []
          for name in self.fnames:
               self.signal_data.append(np.loadtxt(open(mypath+"\\"+name, "rb"), delimiter=",", skiprows=0))
     
     
     def peaks(self, x):
          '''
          find the peaks, output indices and the values of the points
          x - signal as numpy array
          return - list, list
          '''
          V = abs(x[:,1])  # absolute values of voltages
          peak_ind_list = []
          peak_val_list = []
          peak_width = 1500  # in units of indices
          peak_threshold = .1 # volts
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
          return - list
          '''
          peak_averages = []
          for i in range(len(self.signal_data)):
               ind, lst = self.peaks(self.signal_data[i])
               peak_averages.append(np.mean(lst))
          return peak_averages
     
     
     def add_peaks(self):
          '''
          Takes a single signal waveform, and adds together all the peak values
          return - list
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
               plt.figure(figsize=[8,6])
               plt.plot(self.signal_data[i][:, 0], abs(self.signal_data[i][:,1]),c='grey', alpha=.6)
               plt.scatter(self.signal_data[i][ind,0],abs(self.signal_data[i][ind, 1]), s=20, c='goldenrod')
               plt.xlabel('time (s)')
               plt.ylabel('voltage (V)')
               
               
     def pk_avg(self):
          '''
          Plots the average peak values as a function of angle
          '''
          pks = self.peak_average()
          plt.figure(figsize=[8,6])
          plt.plot(self.deg, pks, c='grey')
          plt.title(self.name)
          plt.xlabel('angle (degree)')
          plt.ylabel('average peak voltage (V)')
          
          
     def pk_tot(self):
          '''
          Plots the total peak values as a function of angle
          '''
          pks = self.add_peaks()
          plt.figure(figsize=[8,6])
          plt.plot(self.deg, pks, c='goldenrod')
          plt.title(self.name)
          plt.xlabel('angle (degree)')
          plt.ylabel('total peak voltage (V)')
          
          
     def peak_dist(self):
          '''
          Calculates the distance between the second and third peaks
          (want to get actual dist units)
          '''
          v_water = 1498  # m/s
          for i in range(len(self.signal_data)):
               ind, lst = self.peaks(self.signal_data[i])
               self.pk_dst.append(v_water*(self.signal_data[i][ind[2],0] - self.signal_data[i][ind[1],0])/2)

          plt.figure(figsize=[8,4])
          plt.title('Distance from transducer to sample surface')
          plt.scatter(self.deg, self.pk_dst, c='grey', s=20)
          plt.xlabel('angle (degree)')
          plt.ylabel('distance (m)')
          plt.show()
          
     
     def zoom_peak(self, i, n, width):
          '''
          displays a scaled up plot of a peak waveform
          i: index of angle (which array)
          n: index of peak
          width: zoom index width
          '''
          plt.figure(figsize=[8,6])
          ind, lst = self.peaks(self.signal_data[i])
          Lind = ind[n]-width
          Rind = ind[n]+width
          plt.plot(self.signal_data[i][Lind:Rind,0], self.signal_data[i][Lind:Rind,1], c='goldenrod')
          plt.show()
          
     def get_peak(self, i, n, width):
          '''
          Returns a numpy array that is a scaled up peak waveform
          i: index of angle (which array)
          n: index of peak
          width: zoom index width
          '''
          ind, lst = self.peaks(self.signal_data[i])
          Lind = ind[n]-width
          Rind = ind[n]+width
          return self.signal_data[i][Lind:Rind,:]
     
     def display_signal(self, i):
          plt.figure(figsize=[10,8])
          plt.plot(self.signal_data[i][:,0],self.signal_data[i][:,1], c='goldenrod')
          plt.xlabel('time (s)')
          plt.ylabel('voltage (V)')
          plt.title(self.fnames[i])
          plt.show()
          
if __name__ == "__main__":
     path = "C:\\Users\\dionysius\\Desktop\\PURE\\may24\\FLAT\\clean"
     path1 = "C:\\Users\\dionysius\\Desktop\\PURE\\may24\\FOC\\clean"
     flat = Transducer(path, "Flat Transducer")
     focused = Transducer(path1, "Focused Transducer")
     flat.display_animation()
     flat.zoom_peak(0,1,500)
     flat.get_peak(0,1,500)