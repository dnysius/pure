# -*- coding: utf-8 -*-
"""
Created on Fri May 24 14:28:41 2019

@author: dionysius
"""
import scipy.optimize as sc
import matplotlib.pyplot as plt
import numpy as np
mc = np.array([24.15,20.65,18.53,14.12,10.36,7,3.48,0.56,0], float)
deg = np.array([0,2,4,6,8,10,12,14,15], float)

def d(x, a, b):
     return a*x+ b

popt, pcov = sc.curve_fit(d, mc, deg, (1,1))


def calibration_curve():
     plt.scatter(mc, deg)
     plt.plot(mc, d(mc,*popt))
     plt.xlabel('micrometer reading')
     plt.ylabel('degree')
     plt.title('micrometer calibration curve')
     plt.show()

def angle_change(x1, x2):
     return popt[0]*(x2-x1)