# -*- coding: utf-8 -*-
import numpy as np
from os.path import join

#default_path = r"C:\Users\dionysius\Desktop\PURE\pure\data"
def to_csv(path):
     with open(join(path, "varr.pkl"), 'rb') as rd:
          arr = np.load(rd)
          
     t,one,sig =np.shape(arr)
     csv = np.empty(shape=(t,sig), dtype=float)
     csv[:,:] = arr[:,0,:]
     with open(join(path,"voltages.csv"), 'w+') as cs:
          np.savetxt(cs, csv, delimiter=',')

if __name__=='__main__':
#     to_csv("1D-15FOC7in")
     