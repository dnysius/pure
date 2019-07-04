import numpy as np
from os import getcwd
from os.path import join, dirname
import pickle
import multiprocessing as mp
from time import clock
from tqdm import tqdm
global min_step, c_0
FOLDER_NAME = "1D-3FOC3in"
FOCAL_DEPTH = 0.0381  # 1.5 inch in metres
SAMPLE_DEPTH = 2*FOCAL_DEPTH + .02
min_step = 4e-4
c_0 = 1498  # water


def load_arr(output_folder=join(dirname(getcwd()), "data", FOLDER_NAME)):
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


def delay_t(x, z):
    return lambda xn: (2/c_0)*np.sqrt((x-xn)**2+z**2)


def smm(xi, T, V, xarr):
    x = xarr[xi]  # metres
    col = np.empty(np.shape(V)[0])
    time_sum_arr = [np.sum(T[:i]) for i in range(1, len(T))]
    for ti in range(np.shape(V)[0]):
        z = T[ti]*c_0/2  # metres
        dt = delay_t(x, z)  # anon function dependent on xn
        vals = np.empty((len(xarr),), dtype=float)
        for xni in range(len(xarr)):
            xn = xarr[xni]
            delayed = dt(xn)
            tind = find_nearest(time_sum_arr, delayed)
            vals[xni] = V[tind, xi]

        col[ti, xi] = np.sum(vals)

    return col


def S(T, V, xarr, xi, L):
    return lambda xi, dt: [V[find_nearest(T, dt(xarr[xni]*min_step)), xi]
                           for xni in range(L)]


def SAFT(T, V):
    FD = find_nearest(T[:, 0], 2*FOCAL_DEPTH/c_0)  # focal depth
    SD = find_nearest(T[:, 0], 2*SAMPLE_DEPTH/c_0) + 1  # sample depth
    L = np.shape(V)[1]
    xarr = np.arange(0, L, 1)

    PRE = np.flip(V[:FD, :], axis=0)
    PRE_T = T[:FD]
    PRE_OUT = np.empty(np.shape(PRE))
    POST = V[FD:SD, :]
    POST_T = T[FD:SD]
    POST_OUT = np.empty(np.shape(POST))

    for xi in range(len(xarr)):
        x = xarr[xi]*min_step
        s = S(T, V, xarr, xi, L)
        for ti in range(SD):
            if ti < FD:  # PRE
                z = PRE_T[ti]*c_0/2
                dt = delay_t(x, z)
                PRE_OUT[ti, xi] = np.sum(s(xi, dt))
            elif FD <= ti < SD:
                z = POST_T[ti-FD]*c_0/2
                dt = delay_t(x, z)
                POST_OUT[ti-FD, xi] = np.sum(s(xi, dt))


start = clock()
tarr, varr = load_arr()
tarr = tarr[:, 0, :]
varr = varr[:, 0, :]
ZERO = find_nearest(tarr[:, 0], 0)
T = tarr[ZERO:, 0]  # 1D, time columns all the same
V = varr[ZERO:, :]  # 2D

## Split data into pre and post focal depth
## time_sum_arr = [np.sum(tarr[:i, 0]) for i in range(1, len(tarr[:, 0]))]
FD = find_nearest(tarr[:, 0], 2*FOCAL_DEPTH/c_0)
SD = find_nearest(tarr[:, 0], 2*SAMPLE_DEPTH/c_0)
#PRE_V = np.flip(varr[:FD, :], axis=0)
#PRE_T = np.flip(tarr[:FD, 0], axis=0)
#
#PRE_s = SAFT(PRE_T, PRE_V)
#PRE = np.flip(PRE_s, axis=0)
#pickle.dump(PRE, open("{}-pre.pkl".format(FOLDER_NAME), "wb"))
#
#POST_V = varr[FD:SD, :]
#POST_T = tarr[FD:SD, 0]
#POST = SAFT(POST_T, POST_V)
#pickle.dump(POST, open("{}-post.pkl".format(FOLDER_NAME), "wb"))
#
#stitched = np.vstack((PRE, POST))
#pickle.dump(stitched, open("{}-stitched.pkl".format(FOLDER_NAME), "wb"))

print('total time: {}'.format(clock()-start))
#    time_sum_arr = [np.sum(T[:i]) for i in range(1, len(T))]
