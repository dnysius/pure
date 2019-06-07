# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 12:39:17 2019

@author: dionysius
angle | micrometer reading
0	24.2
1	22.52274209
2	20.84548419
3	19.16822628
4	17.49096838
5	15.81371047
6	14.13645257
7	12.45919466
8	10.78193676
9	9.10467885
10	7.42742095
11	5.75016304
12	4.07290514
13	2.39564723
14	0.71838933
15	-0.95886858
"""
## need to load load_obj, Transducer, obj_folder, or import * for this to work --- why?
## this program doesn't understand the Transducer object when it's loaded from .pkl file?
from analysis import Transducer
from os import listdir
from os.path import join, isfile
import pickle
from time import clock
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from scope import Scope

global obj_folder
global BSCAN_folder
obj_folder = "C:\\Users\\dionysius\\Desktop\\PURE\\Transducer Objects\\"
BSCAN_folder = "C:\\Users\\dionysius\\Desktop\\PURE\\BSCAN\\"

def init():
     start = clock()
     flat15_path = 'C:\\Users\\dionysius\\Desktop\\PURE\\may28\\FLAT\\clean'
     foc15_path = 'C:\\Users\\dionysius\\Desktop\\PURE\\may28\\FOC\\clean'
     flat9_path = 'C:\\Users\\dionysius\\Desktop\\PURE\\may27\\FLAT\\clean'
     foc9_path = 'C:\\Users\\dionysius\\Desktop\\PURE\\may27\\FOC\\clean'
     fpath15 = 'C:\\Users\\dionysius\\Desktop\\PURE\\jun5\\1_5inFOC\\15cm\\clean'
     fpath9 = 'C:\\Users\\dionysius\\Desktop\\PURE\\jun5\\1_5inFOC\\9cm\\clean'
     flat = Transducer(flat15_path, "FLAT_15cm", ftype='npz')
     save_obj(flat)
     foc = Transducer(foc15_path, "3FOC_15cm", ftype='npz')
     save_obj(foc)
     foc2 = Transducer(foc9_path, "3FOC_9cm", ftype='npy')
     save_obj(foc2)
     flat2 = Transducer(flat9_path, "FLAT_9cm", ftype='npy')
     save_obj(flat2)
     foc15 = Transducer(fpath15,"1_5FOC_15cm", param=(4,200))
     save_obj(foc15)
     foc9 = Transducer(fpath9,"1_5FOC_9cm", param=(4,200))
     save_obj(foc9)
     print("Writing completed, {} s!".format(clock()-start))


def BSCAN(signal_data, title='B-Scan', domain=(0, -1), DISPLAY=True, SAVE=False):
     ## signal_data is a list of Signal objects created in the Transducer class
     ## domain is a tuple with start and end points of the signal
     START = domain[0] ## offset the start of the signal; don't want to include transmitted part
     END = domain[1]
     arr = np.abs(signal_data[0].xy[START:END, 1])  ## take abs of first signal
     for i in range(1, len(signal_data)):  ## start from second index
         next_arr = np.abs(signal_data[i].xy[START:END, 1])  ## abs of the next signal
         arr = np.vstack((arr, next_arr))  ## add to previous array
     
     bscan = np.transpose(arr)  ## take transpose, rename variable
     plt.ioff()
     fig = plt.figure(figsize=[12,10])
     plt.title(title)
     plt.imshow(bscan, cmap='gray',origin='upper', aspect='auto', alpha=.8)
     plt.xlabel('angle (degrees)')
     if SAVE == True:
          plt.savefig(BSCAN_folder+title+'.png')
     if DISPLAY == True:
          plt.show(fig)
     elif DISPLAY == False:
          plt.close(fig)
     plt.ion()
     del fig, arr, next_arr, bscan, title, domain


def save_obj(obj, output_folder = obj_folder):
     name = obj.name+".pkl"
     output = join(output_folder, name)

     with open(output, 'wb') as wr:
          pickle.dump(obj, wr, pickle.DEFAULT_PROTOCOL)
          
     print("Done saving: {}".format(name))
     
def load_obj(obj_name, folder = obj_folder):
     if obj_name[-4:] != '.pkl':
          obj_name = obj_name + '.pkl'
          
     output = join(folder,obj_name)
     with open(output, 'rb') as rd:
          transducer = pickle.load(rd)
     return transducer

def graph_totals(title="Angle Dependence", SAVE=False, DISPLAY=True):
     obj_list = [load_obj(f) for f in listdir(obj_folder) if isfile(obj_folder +f) and f[-3:]=="pkl"]
     fig = plt.figure(figsize=[15,14])
     plt.title(title)
     plt.xlabel('angle (degrees)')
     plt.ylabel('relative peak voltages')
     colors = cm.Dark2(np.linspace(0, 1, len(obj_list[0].deg)))
     for i in range(len(obj_list)):
          obj = obj_list[i]
          x = obj.peak_totals
          rescaled = x / max(x) ##(x-min(x))/(max(x)-min(x))
          c = 2 ## this changes the colors used, [1,3]
          plt.scatter(obj.deg, rescaled, color=colors[c*i], alpha=.6, label=obj.name)
          plt.plot(obj.deg, rescaled, color=colors[c*i], ls=":", alpha=.6)
          
     plt.legend()
     if SAVE==True:
          plt.savefig(obj_folder+title+".png", dpi=200)
     if DISPLAY==False:
          plt.close(fig)
     elif DISPLAY==True:
          plt.show(fig)

     
if __name__ == '__main__':
     init()
     graph_totals()
     BSCAN(load_obj("3FOC_15cm.pkl").signal_data, title="3 in Focused 15 cm depth", domain=(24600, 25200))
     