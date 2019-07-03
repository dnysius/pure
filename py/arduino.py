# -*- coding: utf-8 -*-
import serial
import time
arduino = serial.Serial('/dev/cu.usbmodem14201', 9600)


def step(command=1):
    if command == 1:
        time.sleep(1)
        arduino.write(str.encode('H'))
    elif command == 2:
        time.sleep(1)
        arduino.write(str.encode('L'))


for i in range(40):
    if i % 2 == 0:
        step(1)
    else:
        step(2)
