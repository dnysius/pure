# -*- coding: utf-8 -*-
## Dionysius Indraatmadja
## Started June 5 2019

import numpy as np
#####################################################################################
## Define global constants
#####################################################################################
global TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT
TOP_LEFT = (0, 0)
TOP_RIGHT = (0, -1)
BOTTOM_LEFT = (-1, 0)
BOTTOM_RIGHT = (-1, -1)
class Scan():
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
                         ## odd
                         arr[y, 0:-1] = (-1)**(y + PHASE)
                         arr[y, -1] = self.VERTICAL_STEP
                    else:
                         ## even
                         arr[y, 1:] = (-1)**(y + PHASE)
                         arr[y, 0] = self.VERTICAL_STEP
               arr[self.END_POS] = 0
               del PHASE
               
          elif self.START_POS == self.BOTTOM_LEFT:
               pass  ## work on this
          elif self.START_POS == self.BOTTOM_RIGHT:
               pass  ## work on this
               
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
                    
     def start(self):
          #####################################################################################
          ## Walk through array and call on STEP_DICT functions to move motor, work on this
          #####################################################################################
          self.STEP_PARAM()
          pos = self.START_POS
          while self.arr[pos] != 0:
               V = self.arr[pos]
               ## take measurement
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
                    print('final measurement')

          del pos, V
          
     def __repr__(self):
          ## String representation of the sample area
          return np.array2string(self.arr)
                    
if __name__ == '__main__':
     trial = Scan(DIMENSIONS=(200, 100), START_POS="top left")
     