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

from tomo2bm import aps2bm
from tomo2bm import log

global_PVs = {}

def fly_sleep(params):

    tic =  time.time()
    # aps2bm.update_variable_dict(params)
    global_PVsx = aps2bm.init_general_PVs(global_PVs, params)
    try: 
        detector_sn = global_PVs['Cam1_SerialNumber'].get()
        if ((detector_sn == None) or (detector_sn == 'Unknown')):
            log.info('*** The Point Grey Camera with EPICS IOC prefix %s is down' % params.ioc_prefix)
            log.info('  *** Failed!')
        else:
            log.info('*** The Point Grey Camera with EPICS IOC prefix %s and serial number %s is on' \
                        % (params.ioc_prefix, detector_sn))
            
            # calling global_PVs['Cam1_AcquireTime'] to replace the default 'ExposureTime' with the one set in the camera
            params.exposure_time = global_PVs['Cam1_AcquireTime'].get()
            # calling calc_blur_pixel() to replace the default 'SlewSpeed' 
            blur_pixel, rot_speed, scan_time = aps2bm.calc_blur_pixel(global_PVs, params)
            params.slew_speed = rot_speed

            # init camera
            aps2bm.pgInit(global_PVs, params)

            # set sample file name
            fname = str('{:03}'.format(global_PVs['HDF1_FileNumber'].get())) + '_' + global_PVs['Sample_Name'].get(as_string=True)

            scan_lib.tomo_fly_scan(global_PVs, params, fname)

            log.info(' ')
            log.info('  *** Total scan time: %s minutes' % str((time.time() - tic)/60.))
            log.info('  *** Data file: %s' % global_PVs['HDF1_FullFileName_RBV'].get(as_string=True))

            log.info('  *** Moving rotary stage to start position')
            global_PVs["Motor_SampleRot"].put(0, wait=True, timeout=600.0)
            log.info('  *** Moving rotary stage to start position: Done!')

            global_PVs['Cam1_ImageMode'].put('Continuous')

            dm_lib.scp(global_PVs, params)

            log.info('  *** Done!')

    except  KeyError:
        log.error('  *** Some PV assignment failed!')
        pass


def dummy_tomo_fly_scan(global_PVs, params, fname):
    log.info(' ')
    log.info('  *** start_scan')

    def cleanup(signal, frame):
        aps2bm.stop_scan(global_PVs, params)
        sys.exit(0)
    signal.signal(signal.SIGINT, cleanup)

    
def tomo_fly_scan(global_PVs, params, fname):
    log.info(' ')
    log.info('  *** start_scan')

    def cleanup(signal, frame):
        aps2bm.stop_scan(global_PVs, params)
        sys.exit(0)
    signal.signal(signal.SIGINT, cleanup)

    if params.has_key('StopTheScan'):
        aps2bm.stop_scan(global_PVs, params)
        return

    # moved to outer loop in main()
    # pgInit(global_PVs, params)

    aps2bm.setPSO(global_PVs, params)

    # fname = global_PVs['HDF1_FileName'].get(as_string=True)
    log.info('  *** File name prefix: %s' % fname)

    aps2bm.pgSet(global_PVs, params, fname) 

    aps2bm.open_shutters(global_PVs, params)

    # # run fly scan
    theta = aps2bm.pgAcquisition(global_PVs, params)

    theta_end =  global_PVs['Motor_SampleRot_RBV'].get()
    if (0 < theta_end < 180.0):
        # print('\x1b[2;30;41m' + '  *** Rotary Stage ERROR. Theta stopped at: ***' + theta_end + '\x1b[0m')
        log.error('  *** Rotary Stage ERROR. Theta stopped at: %s ***' % str(theta_end))

    aps2bm.pgAcquireFlat(global_PVs, params)
    aps2bm.close_shutters(global_PVs, params)
    time.sleep(2)

    aps2bm.pgAcquireDark(global_PVs, params)

    aps2bm.checkclose_hdf(global_PVs, params)

    aps2bm.add_theta(global_PVs, params, theta)
