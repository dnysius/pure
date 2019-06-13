# -*- coding: utf-8 -*-
## Dionysius Indraatmadja
## Started June 5 2019
'''
Need to write code that commands the arduino to move a step along an axis in Scan2D.STEP()

'''
import numpy as np
import serial
from scope import Scope  # Scope(save path), to initialize connection to oscilloscope. be sure to close()
from os import listdir, getcwd, makedirs, remove
from os.path import join, isfile, dirname, exists
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import pickle

#######################################################################################
## Define global constants
try:
#     arduino = serial.Serial('/dev/cu.usbmodem14201', 9600) ## for Macintosh
     arduino = serial.Serial('COM6', 9600)  ## for Windows

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
          if isfile(join(SCAN_FOLDER,f)) and (f[-4:] == ".npy" or f[-4:]==".pkl"):
               remove(join(SCAN_FOLDER,f))
               
FILENAME = "scope"
#######################################################################################
 
#######################################################################################
## Define classes and methods

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
          self.run()
          
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
          if self.START_POS == self.TOP_LEFT or self.START_POS == self.TOP_RIGHT:
               self.VERTICAL_STEP = -999

          elif self.START_POS == self.BOTTOM_LEFT or self.START_POS == self.BOTTOM_RIGHT:
               self.VERTICAL_STEP = 999
               
          else:
               print("Unexpected Error")
          
          arr = np.zeros(SAMPLE_DIMENSIONS)  ## tuple
          if self.START_POS == self.TOP_RIGHT:               
               for y in range(SAMPLE_DIMENSIONS[0]):
                    if (y % 2) == 0:
                         ## odd
                         arr[y, 1:] = -1
                         arr[y, 0] = self.VERTICAL_STEP
                    else:
                         ## even
                         arr[y, 0:-1] = 1
                         arr[y, -1] = self.VERTICAL_STEP
               
               if SAMPLE_DIMENSIONS[0] % 2 != 0:
                    ENDPOS = (-1, 0)
               else:
                    ENDPOS = (-1,-1)
                    
               arr[ENDPOS] = 0
               
          elif self.START_POS == self.TOP_LEFT:
               for y in range(SAMPLE_DIMENSIONS[0]):
                    if (y % 2) == 0:
                         ## even
                         arr[y, 0:-1] = 1
                         arr[y, -1] = self.VERTICAL_STEP
                    else:
                         ## odd
                         arr[y, 1:] = -1
                         arr[y, 0] = self.VERTICAL_STEP
               
               if SAMPLE_DIMENSIONS[0] % 2 == 0:
                    ENDPOS = (-1, 0)
               else:
                    ENDPOS = (-1,-1)
                    
               arr[ENDPOS] = 0
               
          elif self.START_POS == self.BOTTOM_LEFT:
               
               for y in range(SAMPLE_DIMENSIONS[0]):
                    k = SAMPLE_DIMENSIONS[0]-1-y
                    if (y%2) == 0:
                         ## even
                         arr[k, :] = 1
                         arr[k, -1] = self.VERTICAL_STEP
                    else:
                         ## odd
                         arr[k, 1:] = -1
                         arr[k, 0] = self.VERTICAL_STEP
                    
               if SAMPLE_DIMENSIONS[0] % 2 != 0:
                    ENDPOS = (0, -1)
               else:
                    ENDPOS = (0,0)
                    
               arr[ENDPOS] = 0
                              
          elif self.START_POS == self.BOTTOM_RIGHT:
               for y in range(SAMPLE_DIMENSIONS[0]):
                    k = SAMPLE_DIMENSIONS[0]-1-y
                    if (y%2) == 0:
                         ## even
                         arr[k, 1:] = -1
                         arr[k, 0] = self.VERTICAL_STEP
                         
                    else:
                         ## odd
                         arr[k, 0:-1] = 1
                         arr[k, -1] = self.VERTICAL_STEP
                         
               if SAMPLE_DIMENSIONS[0] % 2 == 0:
                    ENDPOS = (0, -1)
               else:
                    ENDPOS = (0,0)
                    
               arr[ENDPOS] = 0
          
          try:
               self.ENDPOS = ENDPOS
          except:
               print("ENDPOS not defined")
               
          self.arr = np.copy(arr)
          del arr
               
                         
     def run(self):
          #####################################################################################
          ## Walk through array and call on STEP_DICT functions to move motor, work on this
          ## each measurement should save to files in SCAN_FOLDER
          self.STEP_PARAM()
          out_arr = np.empty(np.shape(self.arr))
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
                    
          self.out_arr = out_arr
          self.tarr, self.varr = self.sig2arr(self.out_arr)
          self.save_arr()
          return self.tarr, self.varr
     
     def sig2arr(self, out_arr):
          with open(join(SCAN_FOLDER, FILENAME+"_0.npy"), "rb") as f:
               SIGNAL_LENGTH = len(np.load(f)[:,0])  ## find signal length, assume all signals have same length
          
          START = SIGNAL_LENGTH//2  ## start index
          END = SIGNAL_LENGTH ## end index
          tarr = np.empty((END -START, self.SAMPLE_DIMENSIONS[0], self.SAMPLE_DIMENSIONS[1]), dtype=float)  ## create empty array to store signal time axis
          varr = np.empty((END - START, self.SAMPLE_DIMENSIONS[0], self.SAMPLE_DIMENSIONS[1]), dtype=float)  ## ^^ voltage axis
          
          for y in range(self.SAMPLE_DIMENSIONS[0]):
               for x in range(self.SAMPLE_DIMENSIONS[1]):
                    file = FILENAME + "_" + "{}".format(int(out_arr[y, x])) + ".npy"
                    with open(join(SCAN_FOLDER, file), "rb") as npobj:
                         arr = np.load(npobj)
                         tarr[:,y, x] = arr[START:END, 0]  ## origin is at transmitted signal, at t=0
                         varr[:,y, x] = arr[START:END, 1]
                         
          maxV = np.max(np.abs(varr.flatten()))
          varr = np.abs(varr)/maxV
          
          return tarr, varr
     
     def save_arr(self, output_folder = SCAN_FOLDER):
          ## Save numpy binary to .pkl file
          output_tarr = join(output_folder, "tarr.pkl")
          output_varr = join(output_folder, "varr.pkl")
          with open(output_tarr, 'wb') as wr:
               pickle.dump(self.tarr, wr, pickle.DEFAULT_PROTOCOL)
          
          with open(output_varr, 'wb') as wr:
               pickle.dump(self.varr, wr, pickle.DEFAULT_PROTOCOL)
          
          print("Done saving pickles")
     
     def __repr__(self):
          ## String representation of the sample area
          return np.array2string(self.arr)
     

def grid_test():
     ## print direction grid to ensure they are set up properly
     ## add more test cases
     print("\n2x4 bot left\n", Scan2D(DIMENSIONS=(2,4), START_POS="bottom left"), "\n")
     print("\n3x4 bot left\n", Scan2D(DIMENSIONS=(3,4), START_POS="bottom left"), "\n")
     print("\n2x4 bot right\n", Scan2D(DIMENSIONS=(2,4), START_POS="bottom right"), "\n")
     print("\n3x4 bot right\n", Scan2D(DIMENSIONS=(3,4), START_POS="bottom right"), "\n")
     print("\n2x4 top left\n", Scan2D(DIMENSIONS=(2,4), START_POS="top left"), "\n")
     print("\n3x4 top left\n", Scan2D(DIMENSIONS=(3,4), START_POS="top left"), "\n")
     print("\n2x4 top right\n", Scan2D(DIMENSIONS=(2,4), START_POS="top right"), "\n")
     print("\n3x4 top right\n", Scan2D(DIMENSIONS=(3,4), START_POS="top right"), "\n")
     
def load_arr(output_folder = SCAN_FOLDER):
     ## loads tarr and varr from the scan folder
     ftarr = join(output_folder,"tarr.pkl")
     fvarr = join(output_folder,"varr.pkl")
     with open(ftarr, 'rb') as rd:
          tarr = pickle.load(rd)
          
     with open(fvarr, 'rb') as rd:
          varr = pickle.load(rd)
          
     return tarr, varr

def plot3d(DOMAIN=[0,-1, 50],folder = SCAN_FOLDER, figsize=[0,0]):
     tarr, varr = load_arr(folder)
     
     '''
     Plotting 3D scatter
     
     '''
     if figsize==[0,0]:
          fig = plt.figure()
     else:
          fig = plt.figure(figsize=figsize)
          
     ax = plt.axes(projection='3d')
     X = np.arange(0, len(tarr[0,0,:]), 1)
     Y = np.arange(0, len(tarr[0,:,0]), 1)
     xx, yy = np.meshgrid(X, Y)
     
     START = DOMAIN[0]
     END = DOMAIN[1] ## max time to plot
     EVERY = DOMAIN[2]  # plot every EVERY
     for h in range(START, END, EVERY): 
          for y in range(len(tarr[0,:,0])):
               for x in range(len(tarr[0,0,:])):
                    ax.scatter3D(xx[y,x], yy[y,x], tarr[h, y, x], alpha=varr[h, y, x], c='k')
     plt.xlabel("x axis")
     plt.ylabel("y axis")
     plt.show(fig)
     
def zbscan(i,folder = SCAN_FOLDER, figsize=[0,0]):
     tarr, varr = load_arr(folder)
     
     '''
     z bscan
     '''
     if figsize==[0,0]:
          fig = plt.figure()
     else:
          fig = plt.figure(figsize=figsize)
          
     plt.imshow(varr[i], cmap="gray", aspect='auto')
     plt.xlabel("x axis")
     plt.ylabel("y axis")
     plt.show(fig)
     

clear_scan_folder()  ## deletes files in scan folder
Scan2D(DIMENSIONS=(10,10), START_POS="top right")  ## runs the scan
if __name__ == '__main__':
     pass
#     grid_test()
#     plot3d([0, 10000, 100])
#     zbscan(100, figsize=[2,14])