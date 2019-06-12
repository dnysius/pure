# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 16:32:26 2019

@author: dionysius
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d


S = (4,4)
N = 15
T = np.arange(0, 2*np.pi, .1)
V = np.sin(T)  # same length as time axis
V = (V + np.abs(min(V)))
V /= max(V)
X = np.arange(0, S[1], 1)
Y = np.arange(0, S[0], 1)

xx, yy = np.meshgrid(X, Y)
tarr = np.zeros((len(T),S[0], S[1]))  # time slices, rows, cols
barr = np.zeros((len(T),S[0], S[1]))  # time slices, rows, cols

for y in range(S[0]):
     for x in range(S[1]):
          barr[:,y, x] = V
          tarr[:,y, x] = T
          
fig = plt.figure(figsize=[S[0],S[1]])
ax = plt.axes(projection='3d')
for h in range(len(T)):
     for y in range(S[0]):
          for x in range(S[1]):
               ax.scatter3D(xx[y,x], yy[y,x], tarr[h,y, x], alpha=barr[h, y,x], c='k')
               
ax.set_xticks(X)
ax.set_yticks(Y)