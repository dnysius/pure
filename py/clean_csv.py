     # -*- coding: utf-8 -*-
"""
Created on Tue May 21 14:22:22 2019

@author: dionysius
Takes directory full of csv files and creates copies into a target
directory with the first two rows of data (which are text) discarded.
"""

import csv
from os import listdir, mkdir
from os.path import isfile, join, isdir, isabs
import numpy as np

'''
mypath is the directory with .csv files.
copypath is the directory at which we want to create the new csv files.

if the target directory already contains .csv files of the same name(s),
this script will overwrite them.
'''
def clean(mypath, skip=2, inp='.csv',ext='.npy'):
     copypath = join(mypath,"clean")
     if not isdir(copypath):
          mkdir(copypath)
          
     onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and (inp in f)]
     for i in range(len(onlyfiles)):
          arr = []
          if 'csv' in inp:
               with open(join(mypath, onlyfiles[i]), newline='') as f:
                    reader = csv.reader(f)
                    skipped = 0
                    for row in reader:
                         if skipped >= skip:
                              row[0], row[1] = float(row[0]), float(row[1])
                              arr.append(row)
                         else:
                              skipped += 1
                         
                    a = np.array(arr)
          else:
               a = np.load(join(mypath, onlyfiles[i]))
               
          if ext[-3:]=='npy':
               np.save(join(copypath, onlyfiles[i][0:-4]+'.npy'), a)
          elif ext[-3:]=='npz':
               np.savez_compressed(join(copypath, onlyfiles[i][0:-4]+'.npz'), a)
          elif ext[-3:]=='csv':
               np.savetxt(join(copypath,onlyfiles[i]), a, delimiter=",")
                    
     print('Cleaning done --> ', copypath)
     
if __name__=='__main__':
     print(isabs('C:/Users/dionysius/Desktop/PURE/pure/data/3FOC9cm'))
     print(isabs(r'C:\Users\dionysius\Desktop\PURE\pure\data\3FOC9cm'))  ## use string literal r" " for paths