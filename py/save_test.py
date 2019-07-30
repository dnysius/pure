# -*- coding: utf-8 -*-
"""
save test
"""
from threading import Thread
from os import getcwd, makedirs
from os.path import join, exists
import numpy as np
from time import sleep


def save_arr(i):
    arr = np.random.random((20000, 2))
    folder = join(getcwd(), "test")
    if not exists(folder):
        makedirs(folder)
    with open(join(folder, "file{}.npy".format(i)), 'wb') as filehandle:
        np.save(filehandle, arr)

for i in range(6000):
    t1 = Thread(target=save_arr, args=(i,))
    t1.start()
    t1.join()
    print(i)
