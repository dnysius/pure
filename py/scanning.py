# -*- coding: utf-8 -*-
import numpy as np
from scope import Scope
from os import listdir, getcwd, remove
from os.path import join, isfile, dirname
import matplotlib.pyplot as plt
import pickle
from scipy.signal import hilbert
from misc.move import d2s, step, move
global TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT
global BSCAN_FOLDER, FILENAME, SCAN_FOLDER
FOLDER_NAME = "1D-15FOC3in"
FILENAME = "scope"
BSCAN_FOLDER = join(dirname(getcwd()), "scans", "BSCAN")
SCAN_FOLDER = join(dirname(getcwd()), "data", FOLDER_NAME)
TOP_LEFT = (0, 0)
TOP_RIGHT = (0, -1)
BOTTOM_LEFT = (-1, 0)
BOTTOM_RIGHT = (-1, -1)


def clear_scan_folder():
    for f in listdir(SCAN_FOLDER):
        if isfile(join(SCAN_FOLDER, f)) and (f[-4:] == ".npy"):
            remove(join(SCAN_FOLDER, f))


def load_arr(output_folder=SCAN_FOLDER):
    ftarr = join(output_folder, "tarr.pkl")
    fvarr = join(output_folder, "varr.pkl")
    with open(ftarr, 'rb') as rd:
        tarr = pickle.load(rd)
    with open(fvarr, 'rb') as rd:
        varr = pickle.load(rd)
    return tarr, varr


def ibscan(i='', folder=SCAN_FOLDER, figsize=[8, 8], start=0, end=-1, y1=0, y2=-1, hil=True, save=False):
    bscan(i=i, folder=folder, figsize=figsize, start=start, end=end, y1=y1, y2=y2, hil=hil, save=save)
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
            ibscan(i=i, folder=folder, figsize=figsize, start=start, end=end, y1=a1, y2=a2, hil=hil, save=False)
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
            ibscan(i=i, folder=folder, figsize=figsize, start=a1, end=a2, y1=y1, y2=y2, hil=hil, save=False)
        except ValueError:
            print('invalid input')
    elif cmd == 'raw' or cmd == 'r':
        ibscan(i=i, folder=folder, figsize=figsize, start=start, end=end, y1=y1, y2=y2, hil=False, save=False)
    elif cmd == 'hil' or cmd == 'h' or cmd == 'hilbert':
        ibscan(i=i, folder=folder, figsize=figsize, start=start, end=end, y1=y1, y2=y2, hil=True, save=False)
    elif cmd == 's':
        ibscan(i=i, folder=folder, figsize=figsize, start=start, end=end, y1=y1, y2=y2, hil=hil, save=True)
    else:
        ibscan(i=i, folder=folder, figsize=figsize, start=start, end=end, y1=y1, y2=y2, hil=hil, save=False)


class Scan:
    def __init__(self, DIMENSIONS=(.01, .01), FOLDER=SCAN_FOLDER, START_POS=""):
        self.SCAN_FOLDER = join(dirname(getcwd()), "data", FOLDER)
        self.TOP_LEFT = (0, 0)
        self.TOP_RIGHT = (0, -1)
        self.BOTTOM_LEFT = (-1, 0)
        self.BOTTOM_RIGHT = (-1, -1)
        self.left = -1
        self.right = 1
        self.up = 999
        self.down = -999
        self.STEP_DICT = {self.left: "-x", self.right: "x", self.up: "+y",
                          self.down: "-y"}
        POS_DICT = {"top left": TOP_LEFT, "top right": TOP_RIGHT,
                    "bottom left": BOTTOM_LEFT, "bottom right": BOTTOM_RIGHT}
        self.arr = np.array([])
        self.out_arr = np.array([], dtype=int)
        if DIMENSIONS[0] == 0 and DIMENSIONS[1] != 0:
            self.SAMPLE_DIMENSIONS = (1, d2s(DIMENSIONS[1])+1)
        elif DIMENSIONS[0] != 0 and DIMENSIONS[1] == 0:
            self.SAMPLE_DIMENSIONS = (d2s(DIMENSIONS[0])+1, 1)
        else:
            self.SAMPLE_DIMENSIONS = (d2s(DIMENSIONS[0])+1, d2s(DIMENSIONS[1])+1)
        self.START_POS = POS_DICT[START_POS]
        self.scope = Scope(SCAN_FOLDER, filename=FILENAME)
        clear_scan_folder()
        self.tstep = 0
        self.run()
        clear_scan_folder()

    def STEP(self, DIRECTION='+x'):
        try:
            if DIRECTION in ['x', 'X', '+x', '+X']:
                step(4)
            elif DIRECTION in ['-x', '-X']:
                step(3)
            elif DIRECTION in ['y', 'Y', '+y', '+Y']:
                step(1)
            elif DIRECTION in ['-y', '-Y']:
                step(2)
        except ValueError:
            print("DIRECTION is not type str")

    def STEP_PARAM(self):
        SAMPLE_DIMENSIONS = self.SAMPLE_DIMENSIONS
        if self.START_POS == self.TOP_LEFT or self.START_POS == self.TOP_RIGHT:
            self.VERTICAL_STEP = -999
        elif self.START_POS == self.BOTTOM_LEFT or self.START_POS == self.BOTTOM_RIGHT:
            self.VERTICAL_STEP = 999
        else:
            print("Unexpected Error")
        arr = np.zeros(SAMPLE_DIMENSIONS)
        if self.START_POS == self.TOP_RIGHT:
            for y in range(SAMPLE_DIMENSIONS[0]):
                if (y % 2) == 0:
                    arr[y, 1:] = -1
                    arr[y, 0] = self.VERTICAL_STEP
                else:
                    arr[y, 0:-1] = 1
                    arr[y, -1] = self.VERTICAL_STEP
                if SAMPLE_DIMENSIONS[0] % 2 != 0:
                    ENDPOS = (-1, 0)
                else:
                    ENDPOS = (-1, -1)
            arr[ENDPOS] = 0
        elif self.START_POS == self.TOP_LEFT:
            for y in range(SAMPLE_DIMENSIONS[0]):
                if (y % 2) == 0:
                    arr[y, 0:-1] = 1
                    arr[y, -1] = self.VERTICAL_STEP
                else:
                    arr[y, 1:] = -1
                    arr[y, 0] = self.VERTICAL_STEP
                if SAMPLE_DIMENSIONS[0] % 2 == 0:
                    ENDPOS = (-1, 0)
                else:
                    ENDPOS = (-1, -1)
            arr[ENDPOS] = 0
        elif self.START_POS == self.BOTTOM_LEFT:
            for y in range(SAMPLE_DIMENSIONS[0]):
                k = SAMPLE_DIMENSIONS[0]-1-y
                if (y % 2) == 0:
                    arr[k, :] = 1
                    arr[k, -1] = self.VERTICAL_STEP
                else:
                    arr[k, 1:] = -1
                    arr[k, 0] = self.VERTICAL_STEP
                if SAMPLE_DIMENSIONS[0] % 2 != 0:
                    ENDPOS = (0, -1)
                else:
                    ENDPOS = (0, 0)
            arr[ENDPOS] = 0
        elif self.START_POS == self.BOTTOM_RIGHT:
            for y in range(SAMPLE_DIMENSIONS[0]):
                k = SAMPLE_DIMENSIONS[0]-1-y
                if (y % 2) == 0:
                    arr[k, 1:] = -1
                    arr[k, 0] = self.VERTICAL_STEP
                else:
                    arr[k, 0:-1] = 1
                    arr[k, -1] = self.VERTICAL_STEP
                if SAMPLE_DIMENSIONS[0] % 2 == 0:
                    ENDPOS = (0, -1)
                else:
                    ENDPOS = (0, 0)
            arr[ENDPOS] = 0
        try:
            self.ENDPOS = ENDPOS
        except NameError:
            print("ENDPOS not defined")
        self.arr = np.copy(arr)

    def run(self):
        self.STEP_PARAM()
        out_arr = np.empty(np.shape(self.arr))
        pos = self.START_POS
        i = 0
        while self.arr[pos] != 0:
            V = self.arr[pos]
            self.scope.grab()
            out_arr[pos] = i
            self.STEP(self.STEP_DICT[V])
            if V == self.left:
                pos = (pos[0], pos[1] - 1)
            elif V == self.right:
                pos = (pos[0], pos[1] + 1)
            elif V == self.up:
                pos = (pos[0] - 1, pos[1])
            elif V == self.down:
                pos = (pos[0] + 1, pos[1])
            i += 1
            if self.arr[pos] == 0:
                self.scope.grab()
                out_arr[pos] = i
        self.out_arr = out_arr
        self.tarr, self.varr = self.sig2arr(self.out_arr)
        self.save_arr()
        self.tstep = self.tarr[1, 0, 0] - self.tarr[0, 0, 0]
        return self.tarr, self.varr

    def sig2arr(self, out_arr):
        with open(join(SCAN_FOLDER, "{}_0.npy".format(FILENAME)), "rb") as f:
            SIGNAL_LENGTH = len(np.load(f)[:, 0])
            START = SIGNAL_LENGTH//2
            END = SIGNAL_LENGTH
            tarr = np.empty((END - START, self.SAMPLE_DIMENSIONS[0],
                             self.SAMPLE_DIMENSIONS[1]), dtype=float)
            varr = np.empty((END - START, self.SAMPLE_DIMENSIONS[0],
                             self.SAMPLE_DIMENSIONS[1]), dtype=float)
            for y in range(self.SAMPLE_DIMENSIONS[0]):
                for x in range(self.SAMPLE_DIMENSIONS[1]):
                    file = "{0}_{1}.npy".format(FILENAME, int(out_arr[y, x]))
                    with open(join(SCAN_FOLDER, file), "rb") as npobj:
                        arr = np.load(npobj)
                        tarr[:, y, x] = arr[START:END, 0]
                        varr[:, y, x] = arr[START:END, 1]
        return tarr, varr

    def save_arr(self, output_folder=SCAN_FOLDER):
        output_tarr = join(output_folder, "tarr.pkl")
        output_varr = join(output_folder, "varr.pkl")
        with open(output_tarr, 'wb') as wr:
            pickle.dump(self.tarr, wr, pickle.DEFAULT_PROTOCOL)
        with open(output_varr, 'wb') as wr:
            pickle.dump(self.varr, wr, pickle.DEFAULT_PROTOCOL)
        print("Done saving pickles")


def bscan(i="", folder=SCAN_FOLDER, figsize=[0, 0], start=0, end=-1, y1=0, y2=-1, save=False, hil=True):
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
#        for i in range(np.shape(b)[1]):
        b = np.log10(np.abs(hilbert(b, axis=0)))

    plt.imshow(b[start:end, :], aspect='auto', cmap='gray', vmin=0)
    plt.axhline(y=y1, label='{}'.format(y1+start))
    plt.axhline(y=y2, label='{}'.format(y2+start))
    dt = np.mean(tarr[y2+start, :, :]) - np.mean(tarr[y1+start, :, :])
    v_w = 1498
    v_m = 6420
    dw = v_w*dt/2
    dm = v_m*dt/2
    tstep = np.mean(tarr[1, :, :]) - np.mean(tarr[0, :, :])
    plt.axhline(y=0, label='water: {}'.format(dw), alpha=0)
    plt.axhline(y=0, label='aluminum: {}'.format(dm), alpha=0)
    plt.title("{0}".format(FOLDER_NAME))
    plt.legend()
    if save is True:
        plt.savefig(join(BSCAN_FOLDER, "1D", FOLDER_NAME), dpi=300)
        with open(join(SCAN_FOLDER, "results.txt"), 'w') as wr:
            wr.write("Timestep (s): {0}\ntime between ({1}, {2}): {3}"
                     .format(tstep, y1+start, y2+start, dt))
    plt.xlabel("x axis")
    plt.ylabel("y axis")
    plt.show(fig)


if __name__ == '__main__':
    #    pass
#        foc = Scan(DIMENSIONS=(0, 0.10), START_POS="top left")
    fsarr = join(SCAN_FOLDER, "SAFT-1D-15FOC3in-test.pkl")
    with open(fsarr, 'rb') as rd:
        sarr = pickle.load(rd)
    
#    ibscan(figsize=[8, 8])
