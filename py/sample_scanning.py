# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 16:43:45 2019

@author: dionysius
"""

import numpy as np
from tqdm import trange, tqdm
from time import sleep

class Scan():
     #####################################################################################
     ## Calculate dimensions by (floor) dividing the total length & width by the step size
     ## the motor moves. The step size in x may be different from that in y.
     ## This represents 2D scanning in a rectangular area.
     ######################################################################################
     
     def __init__(self):
          #####################################################################################
          ## Define constants
          self.X_STEP_SIZE = 100
          self.Y_STEP_SIZE = 50
          self.TOP_LEFT = (0, 0)
          self.TOP_RIGHT = (0, -1)
          self.BOTTOM_LEFT = (-1, 0)
          self.BOTTOM_RIGHT = (-1, -1)
          self.left = -1
          self.right = 1
          self.up = 999
          self.down = -999
          self.STEP_DICT = {self.left: "-x", self.right: "x",self.up:"+y", self.down:"-y"}
          self.arr = np.array([])
          self.SAMPLE_DIMENSIONS= (5,5)  ## (rows, columns)...  EDIT THIS
          self.START_POS = self.TOP_RIGHT  ## EDIT THIS
          self.STEP_PARAM()  # INITIALIZE SETUP
          
          #for y in range(SAMPLE_DIMENSIONS[0]):
          #     pbar = tqdm(range(SAMPLE_DIMENSIONS[1]))
          #     for x in pbar:
          #          sleep(.2)
          #          pbar.set_description("Row: {0} Column: {1}".format(y, x))
    
     def STEP_PARAM(self):
          ## If starting from top, then we want all zeros except for the END POSITION to signal to go down
          ## If starting from top... signal to go up
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
               
          if self.START_POS == self.TOP_RIGHT:
               arr = np.zeros(SAMPLE_DIMENSIONS)  ## tuple
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
          
          elif self.START_POS == self.TOP_LEFT:
               arr = np.zeros(SAMPLE_DIMENSIONS)  ## tuple
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
               #     for x in range(SAMPLE_DIMENSIONS[1]):
               arr[self.END_POS] = 0
          
          elif self.START_POS == self.BOTTOM_LEFT:
               pass  ## work on this
          elif self.START_POS == self.BOTTOM_RIGHT:
               pass  ## work on this
               
          self.arr = np.copy(arr)
          del arr, PHASE
     
     def start(self):
          ## Walk through array and call on STEP_DICT functions to move motor
          pos = self.START_POS
          while self.arr[pos] != 0:
               V = self.arr[pos]
               ## take measurement
               print('.')
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
                    print('.')
                    print('done')
                                   
          del pos, V
          
          
     def STEP(self, DIRECTION='+x'):
               ## Command arduino to move motor
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