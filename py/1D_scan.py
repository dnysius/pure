# -*- coding: utf-8 -*-
import numpy as np
import pickle
from scipy.signal import hilbert
import matplotlib.pyplot as plt
from os import getcwd
from os.path import join, dirname
from matplotlib.ticker import FixedFormatter
global min_step, FILENAME
min_step = 4e-4
FOLDER_NAME = "1D-3FOC5in-80um"  # edit this
FILENAME = "SAFT-1D-3FOC5in-80um.pkl"  # and this
if FOLDER_NAME[:2] == "2D":
    par = "2D SCANS"
elif FOLDER_NAME[:2] == "1D":
    par = "1D SCANS"
else:
    par = "ANGLE DEPENDENCE"
BSCAN_FOLDER = join(dirname(getcwd()), "scans", "BSCAN")
SCAN_FOLDER = join(dirname(getcwd()), "data", par, FOLDER_NAME)


def load_arr(output_folder=SCAN_FOLDER):
    ftarr = join(output_folder, "tarr.pkl")
    fvarr = join(output_folder, FILENAME)
    with open(ftarr, 'rb') as rd:
        tarr = pickle.load(rd)
    with open(fvarr, 'rb') as rd:
        varr = pickle.load(rd)
    return tarr, varr


def bscan(tarr, varr, start=0, end=-1, y1=0, y2=-1):
    v_w = 1498
    v_m = 6420
    dt = np.mean(tarr[y2+start, :, :]) - np.mean(tarr[y1+start, :, :])
    dw = v_w*dt/2
    dm = v_m*dt/2
    timestep = np.mean(tarr[1:, :, :] - tarr[:-1, :, :])  # get avg timestep
    fig, ax1 = plt.subplots(1, 1, figsize=(14, 10))
    if y2 == -1:
        y2 = len(varr[start:end, 0]) - 1
    b = np.abs(hilbert(varr, axis=0))  # b = varr[:, 0, :]
    b = 20*np.log10(b/np.max(b.flatten()))
    b = b[start:end, :]
    im0 = plt.imshow(b, aspect='auto', cmap='gray', vmin=-60, vmax=0, interpolation='none', alpha=0)
    ax1.set_xticklabels(np.round(ax1.get_xticks()*100*min_step, 4))
    ax1.set_yticklabels((ax1.get_yticks()).astype(int))
    plt.title("{0}".format(FOLDER_NAME))
    ax2 = ax1.twinx()  # second scale on same axes
    im1 = ax2.imshow(b, aspect='auto', cmap='gray', vmin=-60, vmax=0, interpolation='none', alpha=1)
    fig.colorbar(im1, orientation='vertical', pad=0.08)
    plt.axhline(y=y1, label='{}'.format(y1+start))
    plt.axhline(y=y2, label='{}'.format(y2+start))
    plt.axhline(y=0, label='water: {} m'.format(np.round(dw, 5)), alpha=0)
    plt.axhline(y=0, label='aluminum: {} m'.format(np.round(dm, 5)), alpha=0)
    y_formatter = FixedFormatter(np.round((ax2.get_yticks()+start)*100*timestep*1498/2, 2))
    ax2.yaxis.set_major_formatter(y_formatter)
    ax1.set_xlabel("lateral distance (cm)")
    ax1.set_ylabel("index")
    ax2.set_ylabel("axial distance (cm)")
    plt.legend()
    plt.show(fig)


def ibscan(tarr, varr, start=0, end=-1, y1=0, y2=-1):
    bscan(tarr, varr, start=start, end=end, y1=y1, y2=y2)
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
            ibscan(tarr, varr, start=start, end=end, y1=a1, y2=a2)
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
            ibscan(tarr, varr, start=a1, end=a2, y1=y1, y2=y2)
        except ValueError:
            print('invalid input')
    else:
        ibscan(tarr, varr, start=start, end=end, y1=y1, y2=y2)


if __name__ == '__main__':
    tarr, varr = load_arr(SCAN_FOLDER)
    ibscan(tarr, varr)
