# -*- coding: utf-8 -*-
"""
Created on Tue May 21 14:22:22 2019

@author: dionysius
Takes directory full of csv files and creates copies into a target
directory with the first two rows of data (which are text) discarded.
"""

import csv
from os import listdir, mkdir, getcwd
from os.path import isfile, join
import numpy as np

mypath = "D:\\"
copypath = getcwd()+ "\\copies"
#mkdir(copypath)
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
N = len(onlyfiles)
scopedict = {}
print(listdir())
for i in range(N):
     arr = []
     with open(mypath + onlyfiles[i], newline='') as f:
          
          reader = csv.reader(f)
          skip = 0
          for row in reader:
               if skip > 1:
                    row[0], row[1] = float(row[0]), float(row[1])
               else:
                    skip += 1
               arr.append(row)
          a = np.array(arr[2:])
          np.savetxt(copypath + "\\" + onlyfiles[i], a, delimiter=",")
          scopedict[onlyfiles[i]] = a

print(scopedict)