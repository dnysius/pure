# -*- coding: utf-8 -*-
import numpy as np
import threading
from numpy import \
    power as np_power, \
    sqrt as np_sqrt, \
    sum as np_sum
from os import getcwd
from os.path import join, dirname
import pickle
from tqdm import tqdm
import matplotlib.pyplot as plt
global min_step, c_0, DEFAULT_ARR_FOLDER
global xarr,yarr, FD, SD, T, V, PRE_OUT, POST_OUT, zi
FOLDER_NAME = "1D-3FOC3in"
DEFAULT_ARR_FOLDER = join(dirname(getcwd()), "data", FOLDER_NAME)
FOCAL_DEPTH = 0.0381*2  # 1.5 inch in metres
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
ZERO = find_nearest(tarr[:, 0, 0], 0)
T = tarr[ZERO:, 0, 0]  # 1D, time columns all the same
V = varr[ZERO:, :, :]  # 3D
tstep = np.mean(T[1:]-T[:-1])
FD = find_nearest(T, 2*FOCAL_DEPTH/c_0)  # focal depth
SD = len(T)-1
LY = np.shape(V)[1]
LX = np.shape(V)[2]
PRE = np.flip(V[:FD, :, :], axis=0)
PRE_T = np.flip(T[:FD], axis=0)
PRE_OUT = np.empty(np.shape(PRE))
POST = V[FD:SD, :, :]
POST_T = T[FD:SD]
POST_OUT = np.empty(np.shape(POST))
xarr = np.linspace(-LX/2, LX/2, LX)*min_step
xni = np.arange(0, LX, 1)
yarr = (np.linspace(0, LY, LY)-LY/2)*min_step
yni = np.arange(0, LY, 1)
xx, yy = np.meshgrid(xni, yni)
tni = np.arange(0, SD, 1)


def main(yi, xi):
    x = xarr[xi]
    y = 0
    for ti in tni:
        for i in range(len(yni)):
            z2 = np_power(T[ti]*c_0/2, 2)
            zi = ((2/c_0)*np_sqrt(np_power(x-xarr[xx[i, :]], 2)
                                  + np_power(y-yarr[yy[i, :]], 2) + z2)/tstep).astype(int)
            if ti < FD:
                PRE_OUT[ti, yi, xi] = np_sum(V[zi, i, :])
            elif ti >= FD:
                POST_OUT[ti-FD, yi, xi] = np_sum(V[zi, i, :])


if __name__ == '__main__':
    jobs = []
    pbar1 = tqdm(total=LY*LX)
    pbar1.set_description("Creating job list: ")
    for y in range(LY):
        for x in range(LX):
            pbar1.update(1)
            jobs.append(threading.Thread(target=main, args=(y, x)))
    pbar1.close()
    pbar2 = tqdm(total=LY*LX)
    pbar2.set_description("Starting jobs: ")
    for job in jobs:
        pbar2.update(1)
        job.start()
    pbar2.close()
    pbar3 = tqdm(total=LY*LX)
    pbar3.set_description("Joining jobs: ")
    for job in jobs:
        pbar3.update(1)
        job.join()
    pbar3.close()
    PRE_OUT = np.flip(PRE_OUT, axis=0)
    STITCHED = np.vstack((PRE_OUT, POST_OUT))
    pickle.dump(STITCHED, open(join(DEFAULT_ARR_FOLDER,
                               "SAFT-{}-3D.pkl".format(FOLDER_NAME)), "wb"))
    print("\nDone")

fig = plt.figure(figsize=[10, 10])
plt.imshow(STITCHED[:, 0, :], aspect='auto', cmap='hot')
plt.colorbar()
plt.show()
