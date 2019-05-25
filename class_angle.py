# -*- coding: utf-8 -*-
"""
Created on Fri May 24 14:28:41 2019

@author: dionysius
"""
import scipy.optimize as sc
import matplotlib.pyplot as plt
import numpy as np

class Micrometer:
     '''
     Creates a calibration model object for the micrometer used
     in the angle dependent sample setup.
     '''
     
     def __init__(self, mic, ang):
          '''
          self.mic: micrometer readings
          self.ang: angle readings
          '''
          self.mic = mic
          self.ang = ang
          self.popt, self.pcov = sc.curve_fit(self.__d, self.mic, self.ang, (1,1))


     def __d(self, x, a, b):
          '''
          Model linear function
          '''
          return a*x+ b

     
     def calibration_curve(self):
          '''
          Displays the calibration data points and curve fit
          '''
          plt.figure(figsize=[8,6])
          plt.scatter(self.mic, self.ang, c='grey')
          plt.plot(self.mic, self.__d(self.mic,*self.popt), c='goldenrod')
          plt.xlabel('micrometer reading (mm)')
          plt.ylabel('angle (degree)')
          plt.title('micrometer calibration curve')
          plt.show()
     
     
     def dtheta(self, x1, x2):
          '''
          Outputs the change in angle between two micrometer readings
          '''
          return self.popt[0]*(x2-x1)
     
     
if __name__ == '__main__':
     mc = np.array([24.15,20.65,18.53,14.12,10.36,7,3.48,0.56,0], float)
     deg = np.array([0,2,4,6,8,10,12,14,15], float)
     may22 = Micrometer(mc, deg)
