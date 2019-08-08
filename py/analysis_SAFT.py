# -*- coding: utf-8 -*-
import pickle
import numpy as np
from os.path import join, dirname, isfile
import matplotlib.pyplot as plt
from scipy.signal import hilbert
from os import getcwd, listdir
global tarr, varr, SCAN_FOLDER, BSCAN_FOLDER, FOLDER_NAME
FOLDER_NAME = "1D-3FOC7in"
if FOLDER_NAME[:2] == "1D":
    dim = "1D"
    par = "1D SCANS"
else:
    dim = "2D"
    par = "2D SCANS"
SCAN_FOLDER = join(dirname(getcwd()), "data", par, FOLDER_NAME)
BSCAN_FOLDER = join(dirname(getcwd()), "scans", "SAFT", dim)


def ibscan(figsize=[8, 8], start=0, end=-1, y1=0, y2=-1, sa=True):
    bscan(figsize=figsize, start=start, end=end, y1=y1, y2=y2, sa=sa)
    cmd = input('//\t')
    if cmd == 'x':
        print('Exit')
        pass
    elif cmd == 'c':
        try:
            a1 = input('y1 (default {}):\t'.format(y1))
            a2 = input('y2 (default {}):\t'.format(y2))
            if a1 == '':
                a1 = y1
            else:
                a1 = int(a1)
            if a2 == '':
                a2 = y2
            else:
                a2 = int(a2)
            ibscan(figsize=figsize, start=start,
                   end=end, y1=a1, y2=a2, sa=sa)
        except ValueError:
            print("Invalid input")
    elif cmd == 'z':
        try:
            a1 = input('start (default {}):\t'.format(start))
            a2 = input('end (default {}):\t'.format(end))
            if a1 == '':
                a1 = start
            else:
                a1 = int(a1)
            if a2 == '':
                a2 = end
            else:
                a2 = int(a2)
            ibscan(figsize=figsize, start=a1, end=a2, y1=y1, y2=y2, sa=sa)
        except ValueError:
            print('invalid input')
    elif cmd == 'raw' or cmd == 'r':
        ibscan(figsize=figsize, start=start,
               end=end, y1=y1, y2=y2, sa=False)
    elif cmd == 'sa' or cmd == 'saft':
        ibscan(figsize=figsize, start=start,
               end=end, y1=y1, y2=y2, sa=True)
    elif cmd == 's':
        ibscan(figsize=figsize, start=start, end=end, y1=y1, y2=y2, sa=sa)
    else:
        ibscan(figsize=figsize, start=start, end=end, y1=y1, y2=y2, sa=sa)


def bscan(figsize=[8, 8], start=0, end=-1, y1=0, y2=-1, sa=True):
    onlyfiles = [f for f in listdir(SCAN_FOLDER)
                 if isfile(join(SCAN_FOLDER, f))]
    for file in onlyfiles:
        with open(join(SCAN_FOLDER, file), "rb") as rd:
            if 'tarr' in file:
                tarr = pickle.load(rd)
            elif not sa and 'varr' in file:
                b = pickle.load(rd)
            elif sa and 'SAFT' in file:
                b = pickle.load(rd)
    if figsize == [0, 0]:
        fig = plt.figure()
    else:
        fig = plt.figure(figsize=figsize)
    if y2 == -1:
        y2 = len(b[start:end, 0]) - 1
    b = b[:, :]
    b = np.abs(hilbert(b[start:end, :], axis=0))
    b = 20*np.log10(b/np.max(b.flatten()))
    plt.imshow(b, aspect='auto', cmap='gray', vmin=-60)
    plt.colorbar()
    plt.axhline(y=y1)
    plt.axhline(y=y2)
    dt = np.mean(tarr[y2+start, 0, :]) - np.mean(tarr[y1+start, 0, :])
    v_w = 1498
    v_m = 6420
    dw = v_w*dt/2
    dm = v_m*dt/2
    plt.axhline(y=0, label='water: {}'.format(dw), alpha=0)
    plt.axhline(y=0, label='aluminum: {}'.format(dm), alpha=0)
    if sa:
        plt.title("{0} {1}".format(FOLDER_NAME, "SAFT"))
    elif not sa:
        plt.title("{0} {1}".format(FOLDER_NAME, "BSCAN"))
    plt.legend()
    plt.xlabel("lateral")
    plt.ylabel("axial")
    plt.show(fig)


if __name__ == '__main__':
    ibscan()
