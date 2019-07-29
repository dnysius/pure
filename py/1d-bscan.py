# -*- coding: utf-8 -*-
import numpy as np
import pickle
from scipy.signal import hilbert
import matplotlib.pyplot as plt
from os import getcwd
from os.path import join, dirname
min_step = 4e-4
FOLDER_NAME = "1D-15FOC7in"
FILENAME = "scope"
BSCAN_FOLDER = join(dirname(getcwd()), "scans", "BSCAN")
if FOLDER_NAME[:2] == "2D":
    par = "2D SCANS"
elif FOLDER_NAME[:2] == "1D":
    par = "1D SCANS"
else:
    par = "ANGLE DEPENDENCE"
SCAN_FOLDER = join(dirname(getcwd()), "data", par, FOLDER_NAME)


def load_arr(output_folder=SCAN_FOLDER):
    ftarr = join(output_folder, "tarr.pkl")
    fvarr = join(output_folder, "varr.pkl")
    with open(ftarr, 'rb') as rd:
        tarr = pickle.load(rd)
    with open(fvarr, 'rb') as rd:
        varr = pickle.load(rd)
    return tarr, varr


def bscan(i="", folder=SCAN_FOLDER, figsize=[0, 0], start=0, end=-1, y1=0, y2=-1, hil=True):
    tarr, varr = load_arr(folder)
    if figsize == [0, 0]:
        fig = plt.figure()
    else:
        fig = plt.figure(figsize=figsize)
    if y2 == -1:
        y2 = len(varr[start:end, 0]) - 1
    if i == '':
        b = varr[:, 0, :]
    else:
        b = varr[:,i,:]
    if hil is True:
        b = np.log10(np.abs(hilbert(b, axis=0)))

    plt.imshow(b[start:end, :], aspect='auto', cmap='gray')
    plt.axhline(y=y1, label='{}'.format(y1+start))
    plt.axhline(y=y2, label='{}'.format(y2+start))
    dt = np.mean(tarr[y2+start, :, :]) - np.mean(tarr[y1+start, :, :])
    v_w = 1498
    v_m = 6420
    dw = v_w*dt/2
    dm = v_m*dt/2
    plt.axhline(y=0, label='water: {}'.format(dw), alpha=0)
    plt.axhline(y=0, label='aluminum: {}'.format(dm), alpha=0)
    plt.title("{0}".format(FOLDER_NAME))
    plt.legend()
    plt.xlabel("x axis")
    plt.ylabel("y axis")
    plt.show(fig)


def ibscan(i='', folder=SCAN_FOLDER, figsize=[8, 8], start=0, end=-1, y1=0, y2=-1, hil=True):
    bscan(i=i, folder=folder, figsize=figsize, start=start, end=end, y1=y1, y2=y2, hil=hil)
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
            ibscan(i=i, folder=folder, figsize=figsize, start=start, end=end, y1=a1, y2=a2, hil=hil)
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
            ibscan(i=i, folder=folder, figsize=figsize, start=a1, end=a2, y1=y1, y2=y2, hil=hil)
        except ValueError:
            print('invalid input')
    elif cmd == 'raw' or cmd == 'r':
        ibscan(i=i, folder=folder, figsize=figsize, start=start, end=end, y1=y1, y2=y2, hil=False)
    elif cmd == 'hil' or cmd == 'h' or cmd == 'hilbert':
        ibscan(i=i, folder=folder, figsize=figsize, start=start, end=end, y1=y1, y2=y2, hil=True)
    else:
        ibscan(i=i, folder=folder, figsize=figsize, start=start, end=end, y1=y1, y2=y2, hil=hil)


if __name__ == '__main__':
    ibscan()