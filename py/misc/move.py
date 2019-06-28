# -*- coding: utf-8 -*-
from time import sleep
import serial
import serial.tools.list_ports
global min_step, ArduinoNotFoundError
min_step = 4e-4
ports = list(serial.tools.list_ports.comports())
for p in ports:
    if "Arduino" in p[1]:
        arduino = serial.Serial(p[0], 9600)
try:
    arduino
except NameError:
    ArduinoNotFoundError = True
else:
    ArduinoNotFoundError = False


def d2s(dist):
    # Converts distance in metres to number of steps
    return int(dist//min_step)


def step(command):
    # Sends bytes to arduino to signal step motor movement
    # 1: top motor forward -- black tape side Y axis
    # 2: top motor backward
    # 3: bottom motor backward
    # 4: bottom motor forward -- black tape side X axis
    sleep(1.5)
    try:
        arduino.write(str.encode("{}".format(command)))
    except TypeError:
        print("Command is not 1-4")
    except:
        if ArduinoNotFoundError is True:
            print("ArduinoNotFoundError: cannot call step()")
        else:
            print("Unexpected Error")


def move():
    # 'x -.01' - moves 1 cm in -x direction
    # 'y 1' - moves 1 metre in y direction
    # 'esc' - exits program
    done = ArduinoNotFoundError
    if ArduinoNotFoundError is True:
        print("ArduinoNotFoundError: cannot call move()")
    while not done:
        cmd = input('//\t')
        if cmd == '':
            pass
        elif cmd == 'esc' or cmd == 'exit' or cmd == 'done':
            done = True
        else:
            splt = cmd.split(sep=' ')
            try:
                if splt[0] == 'x':
                    if splt[1][0] == '-':
                        for i in range(int(d2s(float(splt[1][1:])))):
                            step(3)
                    else:
                        for i in range(int(d2s(float(splt[1])))):
                            step(4)
                    elif splt[0] == 'y':
                        if splt[1][0] == '-':
                            for i in range(int(d2s(float(splt[1][1:])))):
                                step(2)
                        else:
                            for i in range(int(d2s(float(splt[1])))):
                                step(1)
            except:
                raise TypeError("invalid input")


if __name__ == '__main__':
    move()
