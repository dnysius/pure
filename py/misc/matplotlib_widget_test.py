# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 19:12:17 2019

@author: dionysius
"""
#import numpy as np
#import matplotlib.pyplot as plt
#from matplotlib.widgets import Slider, Button, RadioButtons,SpanSelector
#
#fig = plt.figure(figsize=(8, 6))
#ax = fig.add_subplot(211, facecolor='#FFFFCC')
#
#x = np.arange(0.0, 5.0, 0.01)
#y = np.sin(2*np.pi*x) + 0.5*np.random.randn(len(x))
#
#ax.plot(x, y, '-')
#ax.set_ylim(-2, 2)
#ax.set_title('Press left mouse button and drag to test')
#
#ax2 = fig.add_subplot(212, facecolor='#FFFFCC')
#line2, = ax2.plot(x, y, '-')
#
#
#def onselect(xmin, xmax):
#    indmin, indmax = np.searchsorted(x, (xmin, xmax))
#    indmax = min(len(x) - 1, indmax)
#
#    thisx = x[indmin:indmax]
#    thisy = y[indmin:indmax]
#    print('xmin: {0}, xmax:{1}\nymin:{2}, ymax: {3}'.format(x[indmin], x[indmax],y[indmin], y[indmax]))
#    line2.set_data(thisx, thisy)
#    ax2.set_xlim(thisx[0], thisx[-1])
#    ax2.set_ylim(thisy.min(), thisy.max())
#    fig.canvas.draw()
#
## set useblit True on gtkagg for enhanced performance
#span = SpanSelector(ax, onselect, 'horizontal', useblit=True,
#                    rectprops=dict(alpha=0.5, facecolor='red'))
#
#
#plt.show()
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor


def select_mvc(data):
    fig = plt.figure(figsize=(11, 7))
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(data)
    plt.ylabel('Force (V)')
    plt.xlabel('Sample')
    cursor = Cursor(ax, useblit=True, color='k', linewidth=1)
    zoom_ok = False
    print('\nZoom or pan to view, \npress spacebar when ready to click:\n')
    while not zoom_ok:
        zoom_ok = plt.waitforbuttonpress()
    print('Click once to select MVC force: ')
    val = plt.ginput(1)
    # print('Selected values: ', val)
    plt.close()
    open('index_mvc.txt', 'w').close()
    with open('index_mvc.txt', 'a') as file:
        file.write('index value\n')
        file.write(str(int(val[0][0])) + ' ' + str(val[0][1]) + '\n')

# read in force data
infile = open('mvc.lvm', 'r')
line = infile.readlines()[23:]
infile.close()
data = [row.strip().split(',') for row in line]
force = np.array([float(row[1]) for row in data])

# select the maximal force
select_mvc(force)