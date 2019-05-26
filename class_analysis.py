# -*- coding: utf-8 -*-
"""
Created on Thu May 23 14:04:23 2019

@author: dionysius

Creates object that contains signal data and methods to analyze it.
"""

import numpy as np
import matplotlib.pyplot as plt
from os import listdir, mkdir
from os.path import isfile, isdir, join
from class_angle import Micro

class Signal:
     '''
     Object for individual waveforms for a given transducer
     '''
     
     def __init__(self, xy, threshold, width):
          '''
          xy: numpy array
          '''
          self.xy = np.copy(xy)  # will be changed by class methods
          self.__xy = np.copy(xy)  # will be constant
          self.name = ''
          self.peak_ind, self.peak_val = self.peaks_list(threshold, width)
     
#     def zoom_peak(self, n, threshold, width):
#          '''
#          displays a scaled up plot of a peak waveform
#          i: index of angle (which array)
#          n: index of peak
#          width: zoom index width
#          '''
#          ind, lst = self.peaks_list(threshold, width)
#          Lind = ind[n]-width
#          Rind = ind[n]+width
#          self.xy = self.xy[Lind:Rind, :]
          
          
     def reset(self):
          self.xy = np.copy(self.__xy)
          
          
     def peaks_list(self, threshold, width):
          '''
          threshold: minimum voltage to detect
          width: domain over which to take the max voltage value
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
          y = self.xy[:, 1]
          return np.fft.fft(y)
          
     
     
class Transducer:
     '''
     fnames: name of csv files in working directory
     signal_data: python list consisting of csv files as numpy arrays
     '''
     def __init__(self, mypath, name):
          self.mypath = mypath
          self.name = name
          self.fnames = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f[-4:] == '.csv']
          self.signal_data = []
          self.deg = Micro.angle
          self.threshold = .5
          self.width = 1500
          self.pk_dst = []
          for i in range(len(self.fnames)):
               xy = np.loadtxt(open(mypath+"\\"+self.fnames[i], "rb"), delimiter=",", skiprows=0)
               sig = Signal(xy, self.threshold, self.width)
               sig.name = "{0}_Transducer_{1}_degrees".format(self.name, self.deg[i])
               self.signal_data.append(sig)
          # initiating methods to find values for totals, averages, and to display totals
          self.peak_totals = self.add_peaks()
          self.peak_averages = self.peak_average()
          self.display_total()
          self.display_average()
          self.display_fft()
          self.display_signal()
          
     
     def peak_average(self):
          '''
          Takes a single signal waveform, output the mean of the peak values
          return - list
          '''
          self.peak_averages = []
          for sig in self.signal_data:
               lst = sig.peak_val
               self.peak_averages.append(np.mean(lst))
               
          return self.peak_averages
     
     
     def add_peaks(self):
          '''
          Takes a single signal waveform, and adds together all the peak values
          return - list
          '''
          self.peak_totals = []
          for sig in self.signal_data:
               lst = sig.peak_val
               self.peak_totals.append(np.sum(lst))
               
          return self.peak_totals
     
          
     def display_animation(self):
          '''
          Displays the plots of each waveform stored in signal_data, along
          with the identified peaks.
          '''
          for i in range(len(self.signal_data)):
               ind, lst = self.peaks(self.signal_data[i])
               plt.figure(figsize=[8,6])
               plt.plot(self.signal_data[i].xy[:, 0], np.abs(self.signal_data[i].xy[:,1]),c='grey', alpha=.6)
               plt.scatter(self.signal_data[i].xy[ind,0],np.abs(self.signal_data[i].xy[ind, 1]), s=20, c='goldenrod')
               plt.xlabel('time (s)')
               plt.ylabel('voltage (V)')
               
               
     def display_average(self):
          '''
          Plots the average peak values as a function of angle
          '''        
          plt.ioff()
          folder = self.mypath + "\\profile"
          if not isdir(folder):
               mkdir(folder)
               
          fig = plt.figure(figsize=[10,8])
          plt.scatter(self.deg, self.peak_averages, c='grey')
          plt.title(self.name)
          plt.xlabel('angle (degree)')
          plt.ylabel('average peak voltage (V)')
          plt.savefig(folder + "\\AVG_" +self.name+".png", dpi=300)
          plt.close(fig)
               
          plt.ion()
          
          
     def display_total(self):
          '''
          Plots the total peak values as a function of angle
          '''
          plt.ioff()
          folder = self.mypath + "\\profile"
          if not isdir(folder):
               mkdir(folder)
               
          fig = plt.figure(figsize=[10,8])
          plt.scatter(self.deg, self.peak_totals, c='goldenrod')
          plt.title(self.name)
          plt.xlabel('angle (degree)')
          plt.ylabel('total peak voltage (V)')
          plt.savefig(folder + "\\TOT_" +self.name+".png", dpi=300)
          plt.close(fig)
               
          plt.ion()
          
          
          
#     def peak_dist(self):
#          '''
#          Calculates the distance between the second and third peaks
#          (want to get actual dist units)
#          '''
#          v_water = 1498  # m/s
#          for i in range(len(self.signal_data)):
#               ind = self.signal_data[i].peak_ind
#               self.pk_dst.append(v_water*(self.signal_data[i].xy[ind[2],0] - self.signal_data[i].xy[ind[1],0])/2)
#
#          plt.figure(figsize=[8,4])
#          plt.title('Distance from transducer to sample surface')
#          plt.scatter(self.deg, self.pk_dst, c='grey', s=20)
#          plt.xlabel('angle (degree)')
#          plt.ylabel('distance (m)')
#          plt.show()
          
     
     def zoom_peak(self, i, n, threshold, width):
          '''
          displays a scaled up plot of a peak waveform
          i: index of angle (which array)
          n: index of peak
          width: zoom index width
          '''
          plt.figure(figsize=[8,6])
          self.signal_data[i].zoom_peak(n, threshold, width)
          self.signal_data[i].display()
          self.signal_data[i].reset()
          
          
     def get_peak(self, i, n, width):
          '''
          Returns a numpy array that is a scaled up peak waveform
          i: index of angle (which array)
          n: index of peak
          width: zoom index width
          return: scaled array
          '''
          ind = self.signal_data[i].peak_ind
          Lind = ind[n]-width
          Rind = ind[n]+width
          return self.signal_data[i].xy[Lind:Rind,:]
     
     
     def display_signal(self):
          plt.ioff()
          folder = self.mypath + "\\signals"
          if not isdir(folder):
               mkdir(folder)
               
          for sig in self.signal_data:
               fig = plt.figure(figsize=[10,8])
               plt.plot(sig.xy[:, 0], sig.xy[:, 1], c='grey')
               plt.scatter(sig.xy[sig.peak_ind, 0], sig.xy[sig.peak_ind, 1], c='goldenrod', s=25)
               plt.xlabel('time (s)')
               plt.ylabel('voltage (V)')
               plt.title(self.name)
               plt.savefig(folder + "\\SIG_" +sig.name+".png", dpi=300)
               plt.close(fig)
               
          plt.ion()
       

     def display_fft(self):
          plt.ioff()
          folder = self.mypath + "\\fft"
          if not isdir(folder):
               mkdir(folder)
               
          for sig in self.signal_data:
               c = sig.fft()
               fig = plt.figure(figsize=[10,8])
               plt.plot(abs(c))
               plt.title(self.name)
               plt.savefig(folder + "\\FFT_" +sig.name+".png", dpi=300)
               plt.close(fig)
               
          plt.ion()
               
               
if __name__ == "__main__":
     path = "C:\\Users\\dionysius\\Desktop\\PURE\\may24\\FLAT\\clean"
     path1 = "C:\\Users\\dionysius\\Desktop\\PURE\\may24\\FOC\\clean"
     flat = Transducer(path, "Flat Transducer")
     focused = Transducer(path1, "Focused Transducer")