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
          self.xy = xy