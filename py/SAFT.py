# -*- coding: utf-8 -*-
import numpy as np
from numpy import \
    reshape as np_reshape, \
    power as np_power, \
    sqrt as np_sqrt, \
    argmin as np_argmin, \
    abs as np_abs, \
    sum as np_sum
from os import getcwd
from os.path import join, dirname
import pickle
from tqdm import tqdm
from time import clock
global min_step, c_0, DEFAULT_ARR_FOLDER
global xarr, FD, SD, pbar, T, V, L, T_COMPARE, PRE_OUT, POST_OUT, xni
FOLDER_NAME = "1D-15FOC3in"
#DEFAULT_ARR_FOLDER = join(dirname(getcwd()), "data", FOLDER_NAME)
DEFAULT_ARR_FOLDER = getcwd()
FOCAL_DEPTH = 0.0381  # 1.5 inch in metres
SAMPLE_DEPTH = 15000
min_step = 4e-4
c_0 = 1498  # water


def load_arr(output_folder=DEFAULT_ARR_FOLDER):
    ftarr = join(output_folder, "tarr.pkl")
    fvarr = join(output_folder, "varr.pkl")
    with open(ftarr, 'rb') as rd:
        tarr = pickle.load(rd)
    with open(fvarr, 'rb') as rd:
        varr = pickle.load(rd)
    return tarr, varr


def find_nearest(array, value):
    array = np.asarray(array, dtype=float)
    return (np.abs(array - value)).argmin()


tarr, varr = load_arr()
tarr = tarr[:, 0, :]
varr = varr[:, 0, :]
ZERO = find_nearest(tarr[:, 0], 0)
T = tarr[ZERO:, 0]  # 1D, time columns all the same
V = varr[ZERO:, :]  # 2D
FD = find_nearest(T, 2*FOCAL_DEPTH/c_0)  # focal depth
# SD = find_nearest(T, 2*SAMPLE_DEPTH/c_0) + 1  # sample depth
SD = len(T)-1
L = np.shape(V)[1]
T_COMPARE = np.empty((L, len(T)))
for l in range(L):
    T_COMPARE[l, :] = T[:]
xarr = np.linspace(-L/2, L/2, L)*min_step
PRE = np.flip(V[:FD, :], axis=0)
PRE_T = np.flip(T[:FD], axis=0)
PRE_OUT = np.empty(np.shape(PRE))
POST = V[FD:SD, :]
POST_T = T[FD:SD]
POST_OUT = np.empty(np.shape(POST))
xni = np.arange(0, L, 1)
xi = 0
pbar = tqdm(total=SD*L)
tstep = np.mean(T[1:]-T[:-1])
start = 0
while xi < 1:
    x = xarr[xi]
    ti = 0
    while ti < SD:
        pbar.update(1)
        pbar.set_description('xi {0}, ti {1}, speed {2}:\t'.format(xi, ti,
                             clock()-start))
        z = T[ti]*c_0/2
        # one iteration of this loop takes 0.1 s... BORING!
        start = clock()
        if ti < FD:  # PRE
            ind = ((2/c_0)*np_sqrt(np_power(x-xarr[xni], 2)
                   + np_power(z, 2))).reshape((L, 1))
#            zi = np_abs(T_COMPARE - ind).argmin(axis=1)  # more accurate
            # less accurate, computationally efficient
            zi = np.floor(ind/tstep).astype(int)
            PRE_OUT[ti, xi] = np_sum(V[zi, xi])
        elif ti >= FD:  # POST
            ind = ((2/c_0)*np_sqrt(np_power(x-xarr[xni], 2)
                   + np_power(z, 2))).reshape((L, 1))
#            zi = np_abs(T_COMPARE - ind).argmin(axis=1)  # more accurate
            # less accurate, computationally efficient
            zi = np.floor(ind/tstep).astype(int)
            POST_OUT[ti-FD, xi] = np_sum(V[zi, xi])
        ti += 1
    xi += 1

pbar.close()

PRE_OUT = np.flip(PRE_OUT, axis=0)
STITCHED = np.vstack((PRE_OUT, POST_OUT))
pickle.dump(STITCHED, open(join(getcwd(),"{}-test.pkl".format(FOLDER_NAME))
                           , "wb"))