import numpy as np
from os import getcwd
from os.path import join, dirname
import pickle
from time import clock
from tqdm import tqdm
import gc
global min_step, c_0
FOLDER_NAME = "1D-15FOC3in"
FOCAL_DEPTH = 0.0381  # 1.5 inch in metres
SAMPLE_DEPTH = 2*FOCAL_DEPTH
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


def SAFT(tarr, varr):
    tarr = tarr[:, 0, 100:125]
    varr = varr[:, 0, 100:125]
    ZERO = find_nearest(tarr[:, 0], 0)
    T = tarr[ZERO:, 0]  # 1D, time columns all the same
    V = varr[ZERO:, :]  # 2D
    FD = find_nearest(T, 2*FOCAL_DEPTH/c_0)  # focal depth
    SD = find_nearest(T, 2*SAMPLE_DEPTH/c_0) + 1  # sample depth
    L = np.shape(V)[1]
    T_COMPARE = np.empty((L, len(T)))
    for l in range(L):
        T_COMPARE[l, :] = T[:]
    xarr = np.arange(0, L, 1)

    PRE = np.flip(V[:FD, :], axis=0)
    PRE_T = T[:FD]
    PRE_OUT = np.empty(np.shape(PRE))
    POST = V[FD:SD, :]
    POST_T = T[FD:SD]
    POST_OUT = np.empty(np.shape(POST))

    pbar = tqdm(total=np.size(PRE)+np.size(POST))
    pbar.set_description("Progress:\t")
    xni = np.arange(0, L, 1)
    xi = 0
    while xi < len(xarr):
        x = xarr[xi]*min_step
        ti = 0
        while ti < SD:
            pbar.update(1)
            if ti < FD:  # PRE
                z = PRE_T[ti]*c_0/2
                ind = np.reshape((2/c_0)*np.sqrt(np.power(x-xni, 2)
                                 + np.power(z, 2)), (L, 1))
                zi = np.argmin(np.abs(T_COMPARE - ind), axis=1)
                PRE_OUT[ti, xi] = np.sum(V[zi, xi])
            elif FD <= ti < SD:  # POST
                z = POST_T[ti-FD]*c_0/2
                ind = np.reshape((2/c_0)*np.sqrt(np.power(x-xni, 2)
                                 + np.power(z, 2)), (L, 1))
                zi = np.argmin(np.abs(T_COMPARE - ind), axis=1)
                POST_OUT[ti-FD, xi] = np.sum(V[zi, xi])
            ti += 1

        gc.collect()
        xi += 1
    pbar.close()
    PRE_OUT = np.flip(PRE_OUT, axis=0)
    STITCHED = np.vstack((PRE_OUT, POST_OUT))

    return STITCHED


start = clock()
tarr, varr = load_arr()
STITCHED = SAFT(tarr, varr)
pickle.dump(STITCHED, open(join(dirname(getcwd()), "data",
                           "{}.pkl".format(FOLDER_NAME)), "wb"))
print('total time: {}'.format(clock()-start))
