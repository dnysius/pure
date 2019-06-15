# -*- coding: utf-8 -*-
"""
Created on Mon May 27 12:36:42 2019

@author: dionysius
1 m/s = .001 mm/microsecond
1 m/s = .0001 cm/microsecond
aluminum speed of sound: 6420 m/s
1 second = 1e6 microsecond | 1 microsecond = 1e-6 seconds
"""
import numpy as np
global tstep
tstep = 3.999999999997929e-08
dt = 2.6e-6  ## change in time
v_m = 6420  # m/s in aluminum
#print(v_m*.001)
#print(v_m*dt/2*100, 'cm')

def dist_ind(dist):
     ## distance in water
     v_w = 1498
     t = 2*dist/v_w
     ind = t//tstep
     return int(ind), t

def ind_thick(w):
     ## w is thickness of sample (aluminum)
     ## returns index, time
     v_m = 6420
     t = 2*w/v_m
     ind = t//tstep
     return int(ind), t

def thickness(dt):
     ## metres
     v_m = 6420
     return v_m*dt/2

## How many indices wide are the reflected signals coming from the surfaces?
print(thickness(np.array([tstep*75, tstep*5])))