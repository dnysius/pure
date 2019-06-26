# -*- coding: utf-8 -*-
'''
Main features:
 - move transducer to desired (y, x) positions using move() interface
 - Create two 3D numpy arrays from scanning a rectangular grid of known dimensions, saved
   as .pkl files (times and voltages) using Scan class.
 - Create b-scan of 3D numpy array loaded from varr.pkl using bscan() function.
'''
global min_step, FILENAME, SCAN_FOLDER
## Edit these parameters if necessary
FOLDER_NAME =  "1D-FLAT5in"  ## data directory /pure/py/data/FOLDER_NAME
## These parameters are optional
min_step = 4e-4  ## size of motor step in metres
FILENAME = "scope"  ## name of the saved files
#######################################################################################
import numpy as np  ## array operations
import serial  ## handle serial connection to arduino
import serial.tools.list_ports
from scope import Scope  ## Scope(save path), to initialize connection to oscilloscope. be sure to close()
from os import listdir, getcwd, remove
from os.path import join, isfile, dirname
import matplotlib.pyplot as plt  ## plottingf
import pickle  ## saving arrays/objects to .pkl file
from time import sleep
from scipy.signal import hilbert

### Define constants and functions
global TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT, BSCAN_FOLDER, arduino
BSCAN_FOLDER = join(join(dirname(getcwd()), "scans"), "BSCAN")
SCAN_FOLDER = join(join(dirname(getcwd()), "data"), FOLDER_NAME)
## positions of grid vertices
TOP_LEFT = (0, 0)
TOP_RIGHT = (0, -1)
BOTTOM_LEFT = (-1, 0)
BOTTOM_RIGHT = (-1, -1)

try:
     ports = list(serial.tools.list_ports.comports())  ## find serial ports being used
     for p in ports:
          if "Arduino" in p[1]:
               arduino = serial.Serial(p[0], 9600)
except:
     pass

def clear_scan_folder():
     for f in listdir(SCAN_FOLDER):
          if isfile(join(SCAN_FOLDER,f)) and (f[-4:] == ".npy"):
               remove(join(SCAN_FOLDER,f))
               
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
     sleep(1.5)
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


     
def ibscan(i='', folder=SCAN_FOLDER, figsize=[8,8], start=0, end=-1, y1=0, y2=-1, hil=False, save=False):
     bscan(i=i,folder = folder, figsize=figsize,start=start,end=end, y1=y1, y2=y2,hil=hil,save=save)
     cmd = input('//\t')
     if cmd =='x':
          print('Exit')
          pass
     elif cmd == 'c':
          try:
               a1 = input('y1 (default {}):\t'.format(y1))
               a2 = input('y2 (default {}):\t'.format(y2))
               if a1 =='':
                    a1 = y1
               else:
                    a1 = int(a1)
                    
               if a2 =='':
                    a2 = y2
               else:
                    a2 = int(a2)
                    
               ibscan(i=i,folder = folder, figsize=figsize,start=start,end=end, y1=a1, y2=a2, hil=hil,save=save)
          
          except:
               raise TypeError('invalid input')
               
     elif cmd == 'z':
          try:
               a1 = input('start (default {}):\t'.format(start))
               a2 = input('end (default {}):\t'.format(end))
               if a1 =='':
                    a1 = start
               else:
                    a1 = int(a1)
                    
               if a2 =='':
                    a2 = end
               else:
                    a2 = int(a2)
                    
               ibscan(i=i,folder = folder, figsize=figsize,start=a1,end=a2,  y1=y1, y2=y2,hil=hil,save=save)
          
          except:
               raise TypeError('invalid input')
     
     elif cmd == 'raw' or cmd=='r':
          ibscan(i=i,folder = folder, figsize=figsize,start=start,end=end, y1=y1, y2=y2, hil=False,save=save)
     elif cmd == 'hil' or cmd=='h' or cmd == 'hilbert':
          ibscan(i=i,folder = folder, figsize=figsize,start=start,end=end, y1=y1, y2=y2, hil=True,save=save)
     elif cmd=='s':
          bscan(i=i,folder = folder, figsize=figsize,start=start,end=end, y1=y1, y2=y2, hil=hil, save=True)
          print('\nsaved\n')
          ibscan(i=i,folder = folder, figsize=figsize,start=start,end=end, y1=y1, y2=y2, hil=hil, save=False)
     else:
          ibscan(i=i,folder = folder, figsize=figsize,start=start,end=end, y1=y1, y2=y2, hil=hil,save=save)



#######################################################################################
## Define classes and methods          
class Scan:
     #####################################################################################
     ## Calculate dimensions by (floor) dividing the total length & width by the step size
     ## the motor moves. The step size in x may be different from that in y.
     ## This represents 2D scanning in a rectangular area.
     def __init__(self, DIMENSIONS=(.01,.01), FOLDER = SCAN_FOLDER, START_POS=""):
          #####################################################################################
          ## Define class constants
          self.SCAN_FOLDER = join(join(dirname(getcwd()), "data"), FOLDER)  ## path to save folder
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
          
          if DIMENSIONS[0]==0 and DIMENSIONS[1] !=0:
               self.SAMPLE_DIMENSIONS = (1, d2s(DIMENSIONS[1])) 
          elif DIMENSIONS[0]!=0 and DIMENSIONS[1] ==0:
               self.SAMPLE_DIMENSIONS = (d2s(DIMENSIONS[0]), 1)               
          else:               
               self.SAMPLE_DIMENSIONS= (d2s(DIMENSIONS[0]), d2s(DIMENSIONS[1]))  ## (rows, columns)
          self.START_POS = POS_DICT[START_POS]  ## starting position of transducer
          self.scope = Scope(SCAN_FOLDER, filename = FILENAME)
          clear_scan_folder()
          self.tstep = 0
          self.run()
          clear_scan_folder()

          
     def STEP(self, DIRECTION='+x'):  ## Command arduino to move motor
          try:
               if DIRECTION == 'x' or DIRECTION == 'X' or DIRECTION == '+x' or DIRECTION == '+X':
                    ## move "right"
                    step(4)
                    
               elif DIRECTION == '-x' or DIRECTION == '-X':
                    ## move "left"
                    step(3)
                    
               elif DIRECTION == 'y' or DIRECTION == 'Y' or DIRECTION == '+y' or DIRECTION == '+Y':
                    ## move "up"
                    step(1)
                    
               elif DIRECTION == '-y' or DIRECTION == '-Y':
                    ## move "down"
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
          
          arr = np.zeros(SAMPLE_DIMENSIONS)  ## shape as tuple
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
          self.tstep = self.tarr[1,0,0] - self.tarr[0,0,0]
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
                         
#          maxV = np.max(np.abs(varr.flatten()))  ## normalize the data
#          varr = varr/maxV
          
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
     
def bscan(i='',folder = SCAN_FOLDER, figsize=[0,0],start=0,end=-1, y1=0, y2=-1, save=False, hil = False):
     ## Plots b-scan from .pkl files in a folder
     ## when applicable, i is a chosen slice of the 2D scan
     tarr, varr = load_arr(folder)
     
     if figsize==[0,0]:
          fig = plt.figure()
     else:
          fig = plt.figure(figsize=figsize)
     if y2==-1:
          y2 = len(varr[start:end,0])-1
     if i =='':
          b = varr[:,0, :]
          if hil == True:
               for i in range(np.shape(b)[1]):
                    b[:,i] = np.abs(hilbert(b[:,i]))
               
          plt.imshow(b[start:end, :], aspect='auto', cmap='gray')  ## bscan[axial, lateral]
          plt.axhline(y=y1, label='{}'.format(y1+start))
          plt.axhline(y=y2, label='{}'.format(y2+start))
          dt = np.mean(tarr[y2+start, :,:]) - np.mean(tarr[y1+start,:,:])
          v_w = 1498  ## speed of sound in water, m/s
          v_m = 6420 ## speed of sound in aluminum, m/s
          dw = v_w*dt/2 ## distance between cursors for water
          dm = v_m*dt/2## distance between cursors of aluminum
          tstep = np.mean(tarr[1,:,:]) - np.mean(tarr[0,:,:])
          plt.axhline(y=0, label='water: {}'.format(dw), alpha=0)
          plt.axhline(y=0, label='aluminum: {}'.format(dm), alpha=0)
          plt.title("{0}".format(FOLDER_NAME))
          plt.legend()
          if save == True:
               plt.savefig(join(BSCAN_FOLDER,"1D", FOLDER_NAME), dpi=300)
          
          with open(join(SCAN_FOLDER, "results.txt"), 'w') as wr:
               wr.write("Timestep (s): {0}\ntime between ({1}, {2}): {3}".format(tstep,y1+start,y2+start, dt))
     else:
          plt.imshow(varr[i], cmap="gray", aspect='auto')
          
     plt.xlabel("x axis")
     plt.ylabel("y axis")
     plt.show(fig)
     
     
if __name__ == '__main__':
#     pass
#     foc = Scan(DIMENSIONS=(0,0.115), START_POS="top right")
#     ibscan()
     ibscan(figsize=[8,8])
