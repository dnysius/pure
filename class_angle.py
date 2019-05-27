# -*- coding: utf-8 -*-
"""
Created on Fri May 24 14:28:41 2019

@author: dionysius

Creates a calibration model object for the micrometer used
in the angle dependent sample setup.
"""
import scipy.optimize as sc
import matplotlib.pyplot as plt
import numpy as np

class Micrometer:
     '''
     self.mic: micrometer readings
     self.ang: angle readings
     '''
     
     def __init__(self, zero, step_size):
          '''
          mic: micrometer readings
          ang: angle readings
          '''
          self.mic = np.array([24.15,20.65,18.53,14.12,10.36,7,3.48,0.56,0], float)
          self.angle = np.array([0,2,4,6,8,10,12,14,15], float)
          self.popt, self.pcov = sc.curve_fit(self.__d, self.mic, self.angle, (1,1))
          self.popt1, self.pcov1 = sc.curve_fit(self.__d, self.angle, self.mic, (1, 1))
          deg = np.arange(0,16, step_size)
          self.vals = self.a(zero, deg)

     def __d(self, x, a, b):
          '''
          Model linear function
          x: micrometer readings
          a, b: curve fit parameters
          return: float
          '''
          return a*x+ b
     
     def fit(self, mic, ang):
          '''
          Overwrites curve fit parameters found with new data
          '''
          self.popt, self.pcov = sc.curve_fit(self.__d, mic, ang, (1,1))

     
     def __calibration_curve(self):
          '''
          Displays the calibration data points and curve fit
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
          Displays the calibration data points and curve fit
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
          x: numpy array corresponding to new micrometer readings
          outputs numpy array for corresponding angle values
          '''
          return self.popt[0]*x + self.popt[1]
     
     def a(self, zero, deg):
          '''
          Outputs micrometer readings for the desired angle values
          '''
          a = (np.transpose(np.array([deg])), np.transpose(np.array([self.popt1[0]*deg + zero])))
          return np.hstack(a)
     
     def graph_vals(self):
          plt.figure(figsize=[8,6])
          plt.scatter(self.vals[:, 0], self.vals[:, 1], c='grey')
          plt.plot(self.vals[:,0], self.__d(self.vals[:,0],self.popt1[0], self.vals[0,1]), c='goldenrod')
          plt.ylabel('micrometer reading (mm)')
          plt.xlabel('angle (degree)')
          plt.title('new micrometer readings')
          plt.show()


Micro = Micrometer(24.20, 1)

if __name__ == '__main__':  
     print(Micro.vals)
     
else:
     pass