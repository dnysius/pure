# -*- coding: utf-8 -*-
"""
Created on Sat May 25 10:27:21 2019

@author: dionysius
"""
import numpy as np
import matplotlib.pyplot as plt

class Signal:
     
     def __init__(self, xy):
          '''
          xy: numpy array
          '''
          self.xy = np.copy(xy)  # will be changed by class methods
          self.__xy = np.copy(xy)  # will be constant
          self.peak_ind = []  # indices of x values where peaks are located
          self.peak_val = []  # y values of each peak
          self.name = ''
     
     def zoom_peak(self, n, threshold, width):
          '''
          displays a scaled up plot of a peak waveform
          i: index of angle (which array)
          n: index of peak
          width: zoom index width
          '''
          ind, lst = self.peaks_list(threshold, width)
          Lind = ind[n]-width
          Rind = ind[n]+width
          self.xy = self.xy[Lind:Rind, :]
          
          
     def reset_view(self):
          self.xy = np.copy(self.__xy)
          
          
     def peaks_list(self, threshold, width):
          '''
          threshold: minimum voltage to detect
          width: domain over which to take the max voltage value
          '''
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
          plt.plot(self.xy[:,0], self.xy[:,1], c='goldenrod')
          plt.xlabel('time (s)')
          plt.ylabel('voltage (V)')
          plt.title(self.name)
          plt.show()
     
     
if __name__ == '__main__':
     