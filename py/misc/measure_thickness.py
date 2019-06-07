# -*- coding: utf-8 -*-
"""
Created on Mon May 27 12:36:42 2019

@author: dionysius
1 m/s = .001 mm/microsecond
1 m/s = .0001 cm/microsecond
aluminum speed of sound: 6420 m/s
1 second = 1e6 microsecond | 1 microsecond = 1e-6 seconds
"""

dt = 2.6e-6
v_m = 6420  # m/s in aluminum
print(v_m*.001)
print(v_m*dt/2*100, 'cm')