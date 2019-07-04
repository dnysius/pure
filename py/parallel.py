import numpy as np
from os import getcwd
from os.path import join, dirname
import pickle
import multiprocessing as mp
from time import clock
from tqdm import tqdm
global min_step, c_0
FOLDER_NAME = "1D-15FOC3in"
FOCAL_DEPTH = 0.0381  # 1.5 inch in metres
SAMPLE_DEPTH = 2*FOCAL_DEPTH + .03
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


def SAFT(T, V):
    xarr = np.arange(0, np.shape(V)[1], 1)*min_step
    finarr = np.empty(np.shape(V))
    tot = len(xarr)*np.shape(V)[0]
    pbar = tqdm(total=tot)
    time_sum_arr = [np.sum(T[:i]) for i in range(1, len(T))]
    for xi in range(len(xarr)):
        x = xarr[xi]
        for ti in range(np.shape(V)[0]):
            z = T[ti]*c_0/2
            dt = delay_t(x, z)
            vals = np.empty((len(xarr),), dtype=float)
            for xni in range(len(xarr)):
                xn = xarr[xni]
                vals[xni] = V[find_nearest(time_sum_arr, dt(xn)), xi]
            finarr[ti, xi] = np.sum(vals)
            pbar.update(1)
    pbar.close()
    return finarr
#    return np.asarray([smm(xi, T, V, xarr) for xi in range(len(xarr))])


start = clock()
tarr, varr = load_arr()
tarr = tarr[:, 0, :]
varr = varr[:, 0, :]

# Split data into pre and post focal depth
time_sum_arr = [np.sum(tarr[:i, 0]) for i in range(1, len(tarr[:, 0]))]
FD = find_nearest(time_sum_arr, 2*FOCAL_DEPTH/c_0)
SD = find_nearest(time_sum_arr, 2*SAMPLE_DEPTH/c_0)
PRE_V = np.flip(varr[:FD, :], axis=0)
PRE_T = np.flip(tarr[:FD, 0], axis=0)

PRE_s = SAFT(PRE_T, PRE_V)
PRE = np.flip(PRE_s, axis=0)
pickle.dump(PRE, open("{}-pre.pkl".format(FOLDER_NAME), "wb"))

POST_V = varr[FD:SD, :]
POST_T = tarr[FD:SD, 0]
POST = SAFT(POST_T, POST_V)
pickle.dump(POST, open("{}-post.pkl".format(FOLDER_NAME), "wb"))

stitched = np.vstack((PRE, POST))
pickle.dump(stitched, open("{}-stitched.pkl".format(FOLDER_NAME), "wb"))

print('total time: {}'.format(clock()-start))
