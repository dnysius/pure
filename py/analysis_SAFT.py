# -*- coding: utf-8 -*-
import pickle
import numpy as np
from os.path import join, dirname, isfile
import matplotlib.pyplot as plt
from os import getcwd, listdir
from scipy.signal import hilbert
global tarr, varr, saft, SCAN_FOLDER, BSCAN_FOLDER
SCAN_FOLDER = join(dirname(getcwd()), "data", "1D-15FOC3in")
BSCAN_FOLDER = join(dirname(getcwd()), "scans", "BSCAN", "1D")


def ibscan(i='', figsize=[8, 8], start=0, end=-1, y1=0, y2=-1, hil=True, save=False):
    bscan(i=i, figsize=figsize, start=start, end=end, y1=y1, y2=y2, hil=hil, save=save)
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
            ibscan(i=i, figsize=figsize, start=start, end=end, y1=a1, y2=a2, hil=hil, save=False)
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
            ibscan(i=i, figsize=figsize, start=a1, end=a2, y1=y1, y2=y2, hil=hil, save=False)
        except ValueError:
            print('invalid input')
    elif cmd == 'raw' or cmd == 'r':
        ibscan(i=i, figsize=figsize, start=start, end=end, y1=y1, y2=y2, hil=False, save=False)
    elif cmd == 'hil' or cmd == 'h' or cmd == 'hilbert':
        ibscan(i=i, figsize=figsize, start=start, end=end, y1=y1, y2=y2, hil=True, save=False)
    elif cmd == 's':
        ibscan(i=i, figsize=figsize, start=start, end=end, y1=y1, y2=y2, hil=hil, save=True)
    else:
        ibscan(i=i, figsize=figsize, start=start, end=end, y1=y1, y2=y2, hil=hil, save=False)


def bscan(i="", figsize=[8, 8], start=0, end=-1, y1=0, y2=-1, save=False, hil=True):
    onlyfiles = [f for f in listdir(SCAN_FOLDER) if isfile(join(SCAN_FOLDER, f))]
    for file in onlyfiles:
        with open(join(SCAN_FOLDER, file), "rb") as rd:
            if 'tarr' in file:
                tarr = pickle.load(rd)
                print(np.shape(tarr))
            elif 'varr' in file:
#                varr = pickle.load(rd)
                pass
            else:
                saft = pickle.load(rd)
    if figsize == [0, 0]:
        fig = plt.figure()
    else:
        fig = plt.figure(figsize=figsize)
    if y2 == -1:
        y2 = len(saft[start:end, 0]) - 1
    if i == '':
        b = saft[:, :]
    else:
        b = saft[:, :]
#    if hil is True:
#        b = np.log10(np.abs(hilbert(b, axis=0)))
    plt.imshow(b[start:end, :], aspect='auto', cmap='gray', vmin=0)
    plt.axhline(y=y1, label='{}'.format(y1+start))
    plt.axhline(y=y2, label='{}'.format(y2+start))
    dt = np.mean(tarr[y2+start, 0, :]) - np.mean(tarr[y1+start, 0, :])
    v_w = 1498
    v_m = 6420
    dw = v_w*dt/2
    dm = v_m*dt/2
    tstep = np.mean(tarr[1, 0, :]) - np.mean(tarr[0, 0, :])
    plt.axhline(y=0, label='water: {}'.format(dw), alpha=0)
    plt.axhline(y=0, label='aluminum: {}'.format(dm), alpha=0)
    plt.title("{0}".format("test"))
    plt.legend()
#    if save is True:
#        plt.savefig(join(BSCAN_FOLDER, "1D", "test"), dpi=300)
#        with open(join(SCAN_FOLDER, "results.txt"), 'w') as wr:
#            wr.write("Timestep (s): {0}\ntime between ({1}, {2}): {3}"
#                     .format(tstep, y1+start, y2+start, dt))
    plt.xlabel("x axis")
    plt.ylabel("y axis")
    plt.show(fig)


if __name__ == '__main__':
    bscan()