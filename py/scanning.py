# -*- coding: utf-8 -*-
## Dionysius Indraatmadja
## Started June 5 2019

import numpy as np
import serial
from scope import Scope
#####################################################################################
## Define global constants
#####################################################################################
global TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT, SCAN_FOLDER
TOP_LEFT = (0, 0)
TOP_RIGHT = (0, -1)
BOTTOM_LEFT = (-1, 0)
BOTTOM_RIGHT = (-1, -1)
SCAN_FOLDER = "C:\\Users\\dionysius\\Desktop\\PURE\\pure\\scans\\sample1"
class Scan2D():
     #####################################################################################
     ## Calculate dimensions by (floor) dividing the total length & width by the step size
     ## the motor moves. The step size in x may be different from that in y.
     ## This represents 2D scanning in a rectangular area.
     ######################################################################################
     
     def __init__(self, DIMENSIONS=(3,3), START_POS=""):
          #####################################################################################
          ## Define class constants
          #####################################################################################
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
          #####################################################################################
          ## EDIT THESE PARAMETERS
          self.SAMPLE_DIMENSIONS= DIMENSIONS  ## (rows, columns)
          self.START_POS = POS_DICT[START_POS]  ## starting position of transducer
          self.X_STEP_SIZE = 100  ## step along a row
          self.Y_STEP_SIZE = 50  ## step along a column
#          self.scope = Scope(SCAN_FOLDER)
    
     def STEP_PARAM(self):
          #####################################################################################
          ## Determine start and end positions
          #####################################################################################
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
               
     
     def STEP(self, DIRECTION='+x'):
          #####################################################################################
          ## Command arduino to move motor, work on this
          #####################################################################################
          try:
               if DIRECTION == 'x' or DIRECTION == 'X' or DIRECTION == '+x' or DIRECTION == '+X':
                    ## move "right"
                    print('right')
                    
               elif DIRECTION == 'x' or DIRECTION == 'X' or DIRECTION == '-x' or DIRECTION == '-X':
                    ## move "left"
                    print('left')
                    
               elif DIRECTION == 'y' or DIRECTION == 'Y' or DIRECTION == '+y' or DIRECTION == '+Y':
                    ## move "up"
                    print("up")
                    
               elif DIRECTION == 'y' or DIRECTION == 'Y' or DIRECTION == '-y' or DIRECTION == '-Y':
                    ## move "down"
                    print("down")
                    
          except:
               raise ValueError("DIRECTION is not type str")
                    
     def run(self):
          #####################################################################################
          ## Walk through array and call on STEP_DICT functions to move motor, work on this
          ## each measurement should save to files in SCAN_FOLDER
          #####################################################################################
          self.STEP_PARAM()
          pos = self.START_POS
          while self.arr[pos] != 0:
               V = self.arr[pos]
               ## take measurement
               print("measure")
#               self.scope.grab()
               self.STEP(self.STEP_DICT[V])  ## Tell arduino to move the step motor
               if V == self.left:
                    pos = (pos[0], pos[1] - 1)
               elif V == self.right:
                    pos = (pos[0], pos[1] + 1)
               elif V == self.up:
                    pos = (pos[0] - 1, pos[1])
               elif V == self.down:
                    pos = (pos[0] + 1, pos[1])
               if self.arr[pos] == 0:
                    ## take one last measurement if at final position
#                    self.scope.grab()
                    print('measure')

          del pos, V
          
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
#          self.scope = Scope(SCAN_FOLDER)
          self.START_POS = START_POS
          self.STEP_DICT = {-1: "-x", 1: "x", 0:"0"}

     def STEP(self, DIRECTION='+x'):
          #####################################################################################
          ## Command arduino to move motor, work on this
          #####################################################################################
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
               self.STEP(self.STEP_DICT[V])  ## Tell arduino to MOVE the step motor
               pos += V
#          self.scope.grab()  ## grab one last measurement at final position
                    
                    
if __name__ == '__main__':
#     pass
#     trial = Scan2D(DIMENSIONS=(2, 2), START_POS="bottom left")
#     trial.run()
     one = Scan1D(LENGTH=1000, START_POS=0)
     one.run()
     print(one.arr)
     