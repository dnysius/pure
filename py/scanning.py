# -*- coding: utf-8 -*-
## Dionysius Indraatmadja
## Started June 5 2019
'''
Need to write code that commands the arduino to move a step along an axis in Scan2D.STEP()

'''
import numpy as np
import serial
from scope import Scope  # Scope(save path), to initialize connection to oscilloscope. be sure to close()
from time import sleep  # might need for giving time to save oscilloscope data, but probbably not
from os import listdir, getcwd, makedirs, remove
from os.path import join, isfile, dirname, exists
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d

#######################################################################################
## Define global constants
try:
     arduino = serial.Serial('/dev/cu.usbmodem14201', 9600) ## for Macintosh
#     arduino = serial.Serial('COM6', 9600)  ## for Windows

except:
#     raise Exception("Can't connect to arduino serial port.")
     print("Can't connect to arduino serial port.")

global TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT, SCAN_FOLDER, FILENAME
TOP_LEFT = (0, 0)
TOP_RIGHT = (0, -1)
BOTTOM_LEFT = (-1, 0)
BOTTOM_RIGHT = (-1, -1)

#######################################################################################
SCAN_FOLDER = join(join(dirname(getcwd()), "data"), "MY_SCAN_FOLDER")  ## EDIT MY_SCAN_FOLDER

def clear_scan_folder():
     for f in listdir(SCAN_FOLDER):
          if f[-4:] == ".npy":
               remove(join(SCAN_FOLDER,f))
               
FILENAME = "scope"
#######################################################################################
 
#######################################################################################
## Define classes and methods
class Scan2D:
     #####################################################################################
     ## Calculate dimensions by (floor) dividing the total length & width by the step size
     ## the motor moves. The step size in x may be different from that in y.
     ## This represents 2D scanning in a rectangular area.
     
     def __init__(self, DIMENSIONS=(3,3), START_POS=""):
          #####################################################################################
          ## Define class constants
          self.TOP_LEFT = (0, 0)
          self.TOP_RIGHT = (0, -1)
          self.BOTTOM_LEFT = (-1, 0)
          self.BOTTOM_RIGHT = (-1, -1)
          self.left = -1
          self.right = 1
          self.up = 999
          self.down = -999
          self.STEP_DICT = {self.left: "-x", self.right: "x",self.up:"+y", self.down:"-y"}
          POS_DICT = {"top left": TOP_LEFT, "top right": TOP_RIGHT, 
                      "bottom left": BOTTOM_LEFT, "bottom right": BOTTOM_RIGHT}                      
          self.arr = np.array([])
          self.out_arr = np.array([], dtype=int)
          #####################################################################################
          ## EDIT THESE PARAMETERS
          self.SAMPLE_DIMENSIONS= DIMENSIONS  ## (rows, columns)
          self.START_POS = POS_DICT[START_POS]  ## starting position of transducer
          self.X_STEP_SIZE = 100  ## step along a row
          self.Y_STEP_SIZE = 50  ## step along a column
          self.scope = Scope(SCAN_FOLDER, filename = FILENAME)
          
     def STEP(self, DIRECTION='+x'):
          #####################################################################################
          ## Command arduino to move motor, work on this
          #####################################################################################
          try:
               if DIRECTION == 'x' or DIRECTION == 'X' or DIRECTION == '+x' or DIRECTION == '+X':
                    ## move "right"  PUT ARDUINO CODE HERE
                    print('right')
                    
               elif DIRECTION == 'x' or DIRECTION == 'X' or DIRECTION == '-x' or DIRECTION == '-X':
                    ## move "left"  PUT ARDUINO CODE HERE
                    print('left')
                    
               elif DIRECTION == 'y' or DIRECTION == 'Y' or DIRECTION == '+y' or DIRECTION == '+Y':
                    ## move "up"  PUT ARDUINO CODE HERE
                    print("up")
                    
               elif DIRECTION == 'y' or DIRECTION == 'Y' or DIRECTION == '-y' or DIRECTION == '-Y':
                    ## move "down"  PUT ARDUINO CODE HERE
                    print("down")
                    
          except:
               raise ValueError("DIRECTION is not type str")
    
     def STEP_PARAM(self):
          #####################################################################################
          ## Determine start and end positions
          SAMPLE_DIMENSIONS = self.SAMPLE_DIMENSIONS
          if self.START_POS == self.TOP_LEFT:
               self.VERTICAL_STEP = -999
               if SAMPLE_DIMENSIONS[0] % 2 != 0:
                    self.END_POS = self.BOTTOM_RIGHT
               elif SAMPLE_DIMENSIONS[0] % 2 == 0:
                    self.END_POS = self.BOTTOM_LEFT
                    
          elif self.START_POS == self.TOP_RIGHT:
               self.VERTICAL_STEP = -999
               if SAMPLE_DIMENSIONS[0] % 2 != 0:
                    self.END_POS = self.BOTTOM_LEFT
               elif SAMPLE_DIMENSIONS[0] % 2 == 0:
                    self.END_POS = self.BOTTOM_RIGHT
                    
          elif self.START_POS == self.BOTTOM_LEFT:
               self.VERTICAL_STEP = 999
               if SAMPLE_DIMENSIONS[0] % 2 != 0:
                    self.END_POS = self.TOP_RIGHT
               elif SAMPLE_DIMENSIONS[0] % 2 == 0:
                    self.END_POS = self.TOP_LEFT
                    
          elif self.START_POS == self.BOTTOM_RIGHT:
               self.VERTICAL_STEP = 999
               if SAMPLE_DIMENSIONS[0] % 2 != 0:
                    self.END_POS = self.TOP_LEFT
               elif SAMPLE_DIMENSIONS[0] % 2 == 0:
                    self.END_POS = self.TOP_RIGHT
                    
          else:
               print("Unexpected Error")
          
          arr = np.zeros(SAMPLE_DIMENSIONS)  ## tuple
          if self.START_POS == self.TOP_RIGHT:
               
               PHASE = 1
               for y in range(SAMPLE_DIMENSIONS[0]):
                    if (y % 2) == 0:
                         ## odd
                         arr[y, 1:] = (-1)**(y + PHASE)
                         arr[y, 0] = self.VERTICAL_STEP
                    else:
                         ## even
                         arr[y, 0:-1] = (-1)**(y + PHASE)
                         arr[y, -1] = self.VERTICAL_STEP
               
               arr[self.END_POS]= 0
               del PHASE
               
          elif self.START_POS == self.TOP_LEFT:
               PHASE = 0
               for y in range(SAMPLE_DIMENSIONS[0]):
                    if (y % 2) == 0:
                         ## even
                         arr[y, 0:-1] = (-1)**(y + PHASE)
                         arr[y, -1] = self.VERTICAL_STEP
                    else:
                         ## odd
                         arr[y, 1:] = (-1)**(y + PHASE)
                         arr[y, 0] = self.VERTICAL_STEP
               arr[self.END_POS] = 0
               del PHASE
               
          elif self.START_POS == self.BOTTOM_LEFT:
               PHASE = 0
               for y in range(SAMPLE_DIMENSIONS[0]):
                    if (y%2) == 0:
                         ## even
                         arr[y, 0:-1] = (-1)**(y+PHASE)
                         arr[y, -1] = self.VERTICAL_STEP
                    else:
                         ## odd
                         arr[y, 1:] = (-1)**(y+PHASE)
                         arr[y, 0] = self.VERTICAL_STEP
               arr[self.END_POS] = 0
               del PHASE
               
          elif self.START_POS == self.BOTTOM_RIGHT:
               PHASE = 1
               for y in range(SAMPLE_DIMENSIONS[0]):
                    if (y%2) == 0:
                         ## even
                         arr[y, 1:] = (-1)**(y+PHASE)
                         arr[y, 0] = self.VERTICAL_STEP
                         
                    else:
                         ## odd
                         arr[y, 0:-1] = (-1)**(y+PHASE)
                         arr[y, -1] = self.VERTICAL_STEP
               arr[self.END_POS] = 0
               del PHASE
               
          self.arr = np.copy(arr)
          del arr
               
                         
     def run(self):
          #####################################################################################
          ## Walk through array and call on STEP_DICT functions to move motor, work on this
          ## each measurement should save to files in SCAN_FOLDER
          self.STEP_PARAM()
          out_arr = np.copy(self.arr)
          pos = self.START_POS
          i = 0
          while self.arr[pos] != 0:
               V = self.arr[pos]
               ## take measurement
               self.scope.grab()
               out_arr[pos] = i
               self.STEP(self.STEP_DICT[V])  ## Tell arduino to move the step motor
               if V == self.left:
                    pos = (pos[0], pos[1] - 1)
               elif V == self.right:
                    pos = (pos[0], pos[1] + 1)
               elif V == self.up:
                    pos = (pos[0] - 1, pos[1])
               elif V == self.down:
                    pos = (pos[0] + 1, pos[1])
               
               i += 1
               if self.arr[pos] == 0:
                    ## take one last measurement if at final position
                    self.scope.grab()
                    out_arr[pos] = i

          del pos, V
          self.out_arr = out_arr
          xy = self.sig2arr(self.out_arr)
          return xy
     
     def sig2arr(self, out_arr):
          xy = np.empty(self.SAMPLE_DIMENSIONS, dtype=object)  ## create empty array to store signals
          for y in range(self.SAMPLE_DIMENSIONS[0]):
               for x in range(self.SAMPLE_DIMENSIONS[1]):
                    file = FILENAME + "_" + "{}".format(int(out_arr[y, x])) + ".npy"
                    with open(join(SCAN_FOLDER, file), "rb") as npobj:
                         xy[y, x] = np.load(npobj)
          
          return xy
     
     def __repr__(self):
          ## String representation of the sample area
          return np.array2string(self.arr)
     

class Scan1D:
     
     def __init__(self, LENGTH, START_POS=0):
          left_str = ["left", "l", "L", "start", "first", 0]
          right_str = ["right", "r", "R", "end", "last", -1]
          self.arr = np.ones(LENGTH, dtype=int)
          if START_POS in left_str:
               self.arr[-1] = 0
               START_POS = 0
          elif START_POS in right_str:
               self.arr *= -1
               self.arr[0] = 0
               START_POS = len(self.arr) -1 
          self.scope = Scope(SCAN_FOLDER)
          self.START_POS = START_POS
          self.STEP_DICT = {-1: "-x", 1: "x", 0:"0"}

     def STEP(self, DIRECTION='+x'):
          #####################################################################################
          ## Command arduino to move motor, work on this
          try:
               if DIRECTION == 'x' or DIRECTION == 'X' or DIRECTION == '+x' or DIRECTION == '+X':
                    ## move "right"
                    print('right')
                    
               elif DIRECTION == 'x' or DIRECTION == 'X' or DIRECTION == '-x' or DIRECTION == '-X':
                    ## move "left"
                    print('left')
               elif DIRECTION == "0":
                    ## do nothing
                    pass
                    
          except:
               raise ValueError("DIRECTION is not type str")
               
     def run(self):
          pos = self.START_POS
          while self.arr[pos] != 0:
               V = self.arr[pos]
               ## grab measurement
               self.scope.grab()
               self.STEP(self.STEP_DICT[V])  ## Tell arduino to move a step in the right direction
               pos += V
          self.scope.grab()  ## grab one last measurement at final position
                    

#clear_scan_folder()
if __name__ == '__main__':
#     two = Scan2D(DIMENSIONS=(3,3), START_POS="bottom left")
#     xy = two.run()
     
     absxy = np.abs(xy)  # 3D
     MX = 0
     for row in absxy:
          for vert in row:
               new_max = np.max(vert[:, 1])
               if new_max > MX:
                    MX = new_max
          
     HEIGHT = len(xy[0,0][:,0])
     s = np.shape(xy)
                         
     xx = np.arange(0, s[1], 1)  # 1D
     yy = np.arange(0, s[0], 1)  # 1D
     
     tarr = [] # time
     barr = []  # brightness
     for h in range(3):
          zz = np.empty(s)
          zb = np.empty(s)
     
          for y in range(s[0]):
               for x in range(s[1]):
                    zz[y, x] = xy[y, x][h, 0]  ## access the Voltage axis of each array in xy grid
                    zb[y, x] = np.abs(xy[y, x][h, 1])/MX
                              
          tarr.append(zz)  ## list
          barr.append(zb)  ## list
          del zb, zz
          
     '''
     Plotting 3D scatter
     
     '''
#     fig = plt.figure()
#     ax = plt.axes(projection='3d')
#     for h in range(3):
#          ax.scatter3D(xx, yy, tarr[h], alpha=barr[h], c='k')  # will alpha=type<array> work?
#          
#     plt.show()
     
     ## imshow for each level
     plt.figure()
     for h in range(3):
          plt.imshow(barr[h], aspect='auto', origin='upper', cmap='gray',alpha=.8, vmin=0, vmax=1)
     plt.show()