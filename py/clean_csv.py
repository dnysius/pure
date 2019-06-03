     # -*- coding: utf-8 -*-
"""
Created on Tue May 21 14:22:22 2019

@author: dionysius
Takes directory full of csv files and creates copies into a target
directory with the first two rows of data (which are text) discarded.
"""

import csv
from os import listdir, mkdir, getcwd
from os.path import isfile, join, isdir
import numpy as np

'''
mypath is the directory with .csv files.
copypath is the directory at which we want to create the new csv files.

if the target directory already contains .csv files of the same name(s),
this script will overwrite them.
'''

def clean(mypath, skip=2):
     '''
     skip: how many rows to skip
     '''
     copypath = mypath + "\\clean"
     if not isdir(copypath):
          mkdir(copypath)
          
     onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f[-4:] == '.csv']
#     print(listdir(mypath))
     for i in range(len(onlyfiles)):
          arr = []
          with open(mypath + "\\"+ onlyfiles[i], newline='') as f:
               
               reader = csv.reader(f)
               skipped = 0
               for row in reader:
                    if skipped >= skip:
                         row[0], row[1] = float(row[0]), float(row[1])
                         arr.append(row)
                    else:
                         skipped += 1
                    
               a = np.array(arr)
#               np.savetxt(copypath + "\\" + onlyfiles[i], a, delimiter=",")
               np.save(copypath + "\\" + onlyfiles[i][0:-3]+'npy', a)
               
     print('Cleaning done --> ', copypath)


if __name__ == '__main__':
     mypath = 'C:\\Users\\dionysius\\Desktop\\PURE\\may28\\FOC'
     clean(mypath, 2)
