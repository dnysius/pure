# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import hilbert
from os import getcwd
from os.path import join, dirname
global graph_title
FOLDER_NAME = "1D-FLAT3in-PURE-testtransducer-lowergain"  # edit this
FILENAME = "varr.pkl"  # and this
graph_title = "FLAT3in"  # and this
if "1D" in FOLDER_NAME:
    par = "1D SCANS"
elif "2D" in FOLDER_NAME:
    par = "2D SCANS"
else:
    par = "ANGLE DEPENDENCE"
path_folder = join(dirname(getcwd()), "data", par, FOLDER_NAME)
path_file = join(path_folder, FILENAME)
path_tarr = join(path_folder, "tarr.pkl")

with open(path_file, "rb") as rd:
    varr = np.load(rd, allow_pickle=True)
    varr = varr[:, 0, :]
with open(path_tarr, "rb") as rd:
    tarr = np.load(rd, allow_pickle=True)
    tarr = tarr[:, 0, :]


def image(varr):
    fig, ax = plt.subplots(figsize=[14, 10])
    plt.imshow(varr, aspect='auto', cmap='gray')
    plt.colorbar()
    plt.show(fig)


def rf_time(t, v):
    fig, ax = plt.subplots(figsize=[18, 12])
    plt.plot(t, v)
    plt.ylabel("voltage (V)")
    plt.xlabel("time (s)")
    plt.title(graph_title)
    plt.show(fig)


def rf_ind(v):
    fig, ax = plt.subplots(figsize=[18, 12])
    plt.plot(v, color='goldenrod', label='raw')
    plt.ylabel("voltage (V)")
    plt.xlabel("index")
    plt.title(graph_title)
    plt.show(fig)


def rf_ind_hil(v):
    fig, ax = plt.subplots(figsize=[18, 12])
    plt.plot(np.imag(hilbert(v)), c='gray', label='Re(hilbert)', ls=':')
    plt.plot(v, color='goldenrod', label='raw')
    plt.ylabel("voltage (V)")
    plt.xlabel("index")
    plt.title(graph_title)
    plt.legend()
    plt.show(fig)


if __name__ == '__main__':
    start = 30000
    end = 35000
    transducer_pos = 80
    rf_ind(varr[start:end, transducer_pos])
#    rf_ind_hil(varr[start:end, transducer_pos])
#    rf_time(tarr[start:end, transducer_pos], varr[start:end, transducer_pos])
