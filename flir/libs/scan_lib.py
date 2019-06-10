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

import aps2bm_lib
import log_lib


def dummy_tomo_fly_scan(global_PVs, variableDict, fname):
    log_lib.Logger(variableDict['LogFileName']).info(' ')
    log_lib.Logger(variableDict['LogFileName']).info('  *** start_scan')

    def cleanup(signal, frame):
        aps2bm_lib.stop_scan(global_PVs, variableDict)
        sys.exit(0)
    signal.signal(signal.SIGINT, cleanup)

    # moved to outer loop in main()
    # pgInit(global_PVs, variableDict)

    # pgSet(global_PVs, variableDict, fname) 

    
def tomo_fly_scan(global_PVs, variableDict, fname):
    log_lib.Logger(variableDict['LogFileName']).info(' ')
    log_lib.Logger(variableDict['LogFileName']).info('  *** start_scan')

    def cleanup(signal, frame):
        aps2bm_lib.stop_scan(global_PVs, variableDict)
        sys.exit(0)
    signal.signal(signal.SIGINT, cleanup)

    if variableDict.has_key('StopTheScan'):
        aps2bm_lib.stop_scan(global_PVs, variableDict)
        return

    # moved to outer loop in main()
    # pgInit(global_PVs, variableDict)

    aps2bm_lib.setPSO(global_PVs, variableDict)

    # fname = global_PVs['HDF1_FileName'].get(as_string=True)
    log_lib.Logger(variableDict['LogFileName']).info('  *** File name prefix: %s' % fname)

    aps2bm_lib.pgSet(global_PVs, variableDict, fname) 

    aps2bm_lib.open_shutters(global_PVs, variableDict)

    # # run fly scan
    theta = aps2bm_lib.pgAcquisition(global_PVs, variableDict)

    theta_end =  global_PVs['Motor_SampleRot_RBV'].get()
    if (0 < theta_end < 180.0):
        # print('\x1b[2;30;41m' + '  *** Rotary Stage ERROR. Theta stopped at: ***' + theta_end + '\x1b[0m')
        log_lib.Logger(variableDict['LogFileName']).error('  *** Rotary Stage ERROR. Theta stopped at: %s ***' % str(theta_end))

    aps2bm_lib.pgAcquireFlat(global_PVs, variableDict)
    aps2bm_lib.close_shutters(global_PVs, variableDict)
    time.sleep(2)

    aps2bm_lib.pgAcquireDark(global_PVs, variableDict)

    aps2bm_lib.checkclose_hdf(global_PVs, variableDict)

    aps2bm_lib.add_theta(global_PVs, variableDict, theta)
