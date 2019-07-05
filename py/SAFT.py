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
from time import clock
from tqdm import tqdm
import multiprocessing as mp
global min_step, c_0, DEFAULT_ARR_FOLDER
global xarr, FD, SD, pbar, T, V, L, T_COMPARE, PRE_OUT, POST_OUT, xni
FOLDER_NAME = "1D-15FOC3in"
DEFAULT_ARR_FOLDER = join(dirname(getcwd()), "data", FOLDER_NAME)
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


def SAFT(xi):
    x = xarr[xi]
    ti = 0
    while ti < SD:
        if ti < FD:  # PRE
            z = T[ti]*c_0/2
            ind = np_reshape((2/c_0)*np_sqrt(np_power(x-xarr[xni], 2)
                             + np_power(z, 2)), (L, 1))
            zi = np_argmin(np_abs(T_COMPARE - ind), axis=1)
            PRE_OUT[ti, xi] = np_sum(V[zi, xi])
        elif ti >= FD:  # POST
            z = T[ti]*c_0/2
            ind = np_reshape((2/c_0)*np_sqrt(np_power(x-xarr[xni], 2)
                             + np_power(z, 2)), (L, 1))
            zi = np_argmin(np_abs(T_COMPARE - ind), axis=1)
            POST_OUT[ti-FD, xi] = np_sum(V[zi, xi])
        ti += 1


if __name__ == '__main__':
    start = clock()
    tarr, varr = load_arr()
    tarr = tarr[:, 0, 100:125]
    varr = varr[:, 0, 100:125]
    ZERO = find_nearest(tarr[:, 0], 0)
    T = tarr[ZERO:, 0]  # 1D, time columns all the same
    V = varr[ZERO:, :]  # 2D
    FD = find_nearest(T, 2*FOCAL_DEPTH/c_0)  # focal depth
    # SD = find_nearest(T, 2*SAMPLE_DEPTH/c_0) + 1  # sample depth
    SD = -1
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

    pool = mp.Pool(mp.cpu_count())
    results = pool.map(SAFT, np.arange(0, L, 1))
    pool.close()

    PRE_OUT = np.flip(PRE_OUT, axis=0)
    STITCHED = np.vstack((PRE_OUT, POST_OUT))
    pickle.dump(STITCHED, open(join(dirname(getcwd()), "data",
                               "{}-test.pkl".format(FOLDER_NAME)), "wb"))
    print('total time: {}'.format(clock()-start))
