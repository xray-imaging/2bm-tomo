'''
    Tomo Scan Lib for Sector 2-BM  using Point Grey Grasshooper3 or FLIR Oryx cameras
    
'''
from __future__ import print_function

import sys
import json
import time
from epics import PV
import h5py
import shutil
import os
import imp
import traceback
import math
import signal
import logging
import numpy as np

from pg_lib import *


LOG = logging.getLogger(__name__)


def dummy_tomo_fly_scan(global_PVs, variableDict, fname):
    Logger("log").info(' ')
    Logger("log").info('  *** start_scan')

    def cleanup(signal, frame):
        stop_scan(global_PVs, variableDict)
        sys.exit(0)
    signal.signal(signal.SIGINT, cleanup)


    pgInit(global_PVs, variableDict)

    # pgSet(global_PVs, variableDict, fname) 

    
def tomo_fly_scan(global_PVs, variableDict, fname):
    Logger("log").info(' ')
    Logger("log").info('  *** start_scan')

    def cleanup(signal, frame):
        stop_scan(global_PVs, variableDict)
        sys.exit(0)
    signal.signal(signal.SIGINT, cleanup)

    if variableDict.has_key('StopTheScan'):
        stop_scan(global_PVs, variableDict)
        return

    # moved to outer loop in main()
    # pgInit(global_PVs, variableDict)

    setPSO(global_PVs, variableDict)

    # fname = global_PVs['HDF1_FileName'].get(as_string=True)
    Logger("log").info('  *** File name prefix: %s' % fname)

    pgSet(global_PVs, variableDict, fname) 

    open_shutters(global_PVs, variableDict)

    # # run fly scan
    theta = pgAcquisition(global_PVs, variableDict)

    theta_end =  global_PVs['Motor_SampleRot_RBV'].get()
    if (theta_end < 180.0):
        # print('\x1b[2;30;41m' + '  *** Rotary Stage ERROR. Theta stopped at: ***' + theta_end + '\x1b[0m')
        Logger("log").error('  *** Rotary Stage ERROR. Theta stopped at: %s ***' % str(theta_end))

    pgAcquireFlat(global_PVs, variableDict)
    close_shutters(global_PVs, variableDict)
    time.sleep(2)

    pgAcquireDark(global_PVs, variableDict)

    checkclose_hdf(global_PVs, variableDict)

    add_theta(global_PVs, variableDict, theta)
