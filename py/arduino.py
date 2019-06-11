# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 11:34:18 2019

@author: jitongchen
"""

import serial 
import time

arduino = serial.Serial('/dev/cu.usbmodem14201', 9600)

def step(command = 1):
#  command = int(input("Type something..: (1/2)"));
  if command ==1:
      time.sleep(1)
      arduino.write(str.encode('H'))
  elif command ==2:
      time.sleep(1) 
      arduino.write(str.encode('L'))


for i in range(40):
    if i % 2 ==0:
        step(1)
    else:
        step(2)