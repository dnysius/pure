# -*- coding: utf-8 -*-
## Dionysius Indraatmadja
## Started June 5 2019
'''
Main features:
 - move transducer to desired (y, x) positions using move() interface
 - Create two 3D numpy arrays from scanning a rectangular grid of known dimensions, saved
   as .pkl files (times and voltages) using Scan class.
 - Create b-scan of 3D numpy array loaded from varr.pkl using bscan() function.

'''
import numpy as np
import serial
from scope import Scope  # Scope(save path), to initialize connection to oscilloscope. be sure to close()
from os import listdir, getcwd, remove
from os.path import join, isfile, dirname
import matplotlib.pyplot as plt
import pickle
from time import sleep
import serial.tools.list_ports
global min_step, FILENAME, FOLDER_NAME
#######################################################################################
min_step = 4e-5*10  ## size of motor step in metres
FOLDER_NAME =  "1D-3FOC5in"  ## data directory /pure/py/data/FOLDER_NAME
FILENAME = "scope"  ## name of the saved files
#######################################################################################
### Define constants and functions
global TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT, SCAN_FOLDER, BSCAN_FOLDER
SCAN_FOLDER = join(join(dirname(getcwd()), "data"), FOLDER_NAME)  ## path to save folder
BSCAN_FOLDER = join(dirname(getcwd()), "data\\scans\\BSCAN\\")
ports = list(serial.tools.list_ports.comports())  ## find serial ports being used
arduino = None
for p in ports:
    if "Arduino" in p[1]:  ## search for port connected to the arduino
         arduino = serial.Serial(p[0], 9600)
    
if arduino == None:  ## warn us if arduino was not found
     print("No arduino selected")
     
## positions of grid vertices
TOP_LEFT = (0, 0)
TOP_RIGHT = (0, -1)
BOTTOM_LEFT = (-1, 0)
BOTTOM_RIGHT = (-1, -1)
               
def d2s(dist):
     ## Converts distance in metres to number of steps
     return int(dist//min_step)
     
def step(command):
     ## Sends bytes to arduino to signal step motor movement
     ## command:
     ## 1: top motor forward -- black tape side Y axis
     ## 2: top motor backward
     ## 3: bottom motor backward
     ## 4: bottom motor forward -- black tape side X axis
     sleep(.75)
     try:
          arduino.write(str.encode("{}".format(command)))
     except:
          raise TypeError("Command is not 1-4")
          
def move():
     ## Initializes environment in which to move the transducer freely without grabbing
     ## oscilloscope screen
     ## example usage:
     ## 'x -.01' - moves 1 cm in -x direction
     ## 'y 1' - moves 1 metre in y direction
     ## 'esc' - exits program
     done = False
     while not done:
          cmd = input('//\t')
          if cmd =='':
               pass
          elif cmd == 'esc' or cmd == 'exit' or cmd=='done':
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
                    
def load_arr(output_folder = SCAN_FOLDER):
     ## loads numpy arrays tarr and varr in the scan folder
     ftarr = join(output_folder,"tarr.pkl")
     fvarr = join(output_folder,"varr.pkl")
     with open(ftarr, 'rb') as rd:
          tarr = pickle.load(rd)
          
     with open(fvarr, 'rb') as rd:
          varr = pickle.load(rd)
          
     return tarr, varr

def bscan(i='',folder = SCAN_FOLDER, figsize=[0,0]):
     ## Plots b-scan from .pkl files in a folder
     ## when applicable, i is a chosen slice of the 2D scan
     tarr, varr = load_arr(folder)
     if figsize==[0,0]:
          fig = plt.figure()
     else:
          fig = plt.figure(figsize=figsize)
          
     if i =='':
          b = np.transpose(varr)[0,:, :]
          b = np.transpose(bscan)
          plt.imshow(b[2000: 5000, 0:], aspect='auto', cmap='gray')  ## bscan[axial, lateral]
          plt.title(FOLDER_NAME)
          plt.savefig(join(BSCAN_FOLDER, FOLDER_NAME), dpi=300)
          plt.show(fig)
          plt.imshow(np.transpose(varr), cmap="gray", aspect='auto')
     else:
          plt.imshow(varr[i], cmap="gray", aspect='auto')
          
     plt.xlabel("x axis")
     plt.ylabel("y axis")
     plt.show(fig)
     
#######################################################################################
## Define classes and methods          
class Scan:
     #####################################################################################
     ## Calculate dimensions by (floor) dividing the total length & width by the step size
     ## the motor moves. The step size in x may be different from that in y.
     ## This represents 2D scanning in a rectangular area.
     def __init__(self, DIMENSIONS=(.01,.01), START_POS=""):
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
          if DIMENSIONS[0]==0 and DIMENSIONS[1] !=0:
               self.SAMPLE_DIMENSIONS = (1, d2s(DIMENSIONS[1])) 
          elif DIMENSIONS[0]!=0 and DIMENSIONS[1] ==0:
               self.SAMPLE_DIMENSIONS = (d2s(DIMENSIONS[0]), 1)               
          else:               
               self.SAMPLE_DIMENSIONS= (d2s(DIMENSIONS[0]), d2s(DIMENSIONS[1]))  ## (rows, columns)
               
          self.START_POS = POS_DICT[START_POS]  ## starting position of transducer
          self.scope = Scope(SCAN_FOLDER, filename = FILENAME)
          self.run()
          
     def STEP(self, DIRECTION='+x'):
          #####################################################################################
          ## Command arduino to move motor, work on this
          #####################################################################################
          try:
               if DIRECTION == 'x' or DIRECTION == 'X' or DIRECTION == '+x' or DIRECTION == '+X':
                    ## move "right"  forward bottom motor
                    step(4)
                    
               elif DIRECTION == '-x' or DIRECTION == '-X':
                    ## move "left"
                    step(3)
                    
               elif DIRECTION == 'y' or DIRECTION == 'Y' or DIRECTION == '+y' or DIRECTION == '+Y':
                    ## move "up"  PUT ARDUINO CODE HERE
                    step(1)
                    
               elif DIRECTION == '-y' or DIRECTION == '-Y':
                    ## move "down"  PUT ARDUINO CODE HERE
                    step(2)
                    
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
     

if __name__ == '__main__':
#     Scan(DIMENSIONS=(.15,0), START_POS="bottom left")
#     plot3d([0, 1000, 50])
     tarr, varr = load_arr()
     b = np.transpose(varr)[0,:, :]
     b = np.transpose(bscan)
     fig = plt.figure(figsize=[10,10])
     plt.imshow(b[2000: 5000, 0:], aspect='auto', cmap='gray')  ## bscan[axial, lateral]
     plt.title("1D-3FOC5in")
     plt.savefig(join("C:\\Users\\dionysius\\Desktop\\PURE\\pure\\scans\\BSCAN\\","1D-3FOC5in.png"), dpi=300)
     plt.show(fig)
     
#######################################################################################
## Notes     
## step should be less than half the wavelength (.34mm wavelength)
##
##
##     
##
#######################################################################################
## Appendix
#######################################################################################
#from mpl_toolkits import mplot3d
#try:
##     arduino = serial.Serial('/dev/cu.usbmodem14201', 9600) ## for Macintosh
#     arduino = serial.Serial('COM6', 9600)  ## for Windows
#
#except:
##     raise Exception("Can't connect to arduino serial port.")
#     print("Can't connect to arduino serial port.")

#def grid_test():
#     ## print direction grid to ensure they are set up properly
#     ## add more test cases
#     print("\n2x4 bot left\n", Scan(DIMENSIONS=(2,4), START_POS="bottom left"), "\n")
#     print("\n3x4 bot left\n", Scan(DIMENSIONS=(3,4), START_POS="bottom left"), "\n")
#     print("\n2x4 bot right\n", Scan(DIMENSIONS=(2,4), START_POS="bottom right"), "\n")
#     print("\n3x4 bot right\n", Scan(DIMENSIONS=(3,4), START_POS="bottom right"), "\n")
#     print("\n2x4 top left\n", Scan(DIMENSIONS=(2,4), START_POS="top left"), "\n")
#     print("\n3x4 top left\n", Scan(DIMENSIONS=(3,4), START_POS="top left"), "\n")
#     print("\n2x4 top right\n", Scan(DIMENSIONS=(2,4), START_POS="top right"), "\n")
#     print("\n3x4 top right\n", Scan(DIMENSIONS=(3,4), START_POS="top right"), "\n")
#
#def plot3d(DOMAIN=[0,-1, 50],folder = SCAN_FOLDER, figsize=[0,0]):
#     tarr, varr = load_arr(folder)
#     
#     '''
#     Plotting 3D scatter
#     
#     '''
#     if figsize==[0,0]:
#          fig = plt.figure()
#     else:
#          fig = plt.figure(figsize=figsize)
#          
#     ax = plt.axes(projection='3d')
#     X = np.arange(0, len(tarr[0,0,:]), 1)
#     Y = np.arange(0, len(tarr[0,:,0]), 1)
#     xx, yy = np.meshgrid(X, Y)
#     
#     START = DOMAIN[0]
#     END = DOMAIN[1] ## max time to plot
#     EVERY = DOMAIN[2]  # plot every EVERY
#     for h in range(START, END, EVERY): 
#          for y in range(len(tarr[0,:,0])):
#               for x in range(len(tarr[0,0,:])):
#                    ax.scatter3D(xx[y,x],yy[y,x], tarr[h, y,x], alpha=varr[h, y,x], c='k')
#     
#     ax.scatter3D(xx[0,0], yy[0,0], tarr[:,0,0],c='k')
#     ax.set_zlim(0,.0001)
#     ax.set_xlim(0,3)
#     ax.set_ylim(0,3)
#     plt.xlabel("x axis")
#     plt.ylabel("y axis")
#     plt.show(fig)
#
#def clear_scan_folder():
#     for f in listdir(SCAN_FOLDER):
#          if isfile(join(SCAN_FOLDER,f)) and (f[-4:] == ".npy" or f[-4:]==".pkl"):
#               remove(join(SCAN_FOLDER,f))
     