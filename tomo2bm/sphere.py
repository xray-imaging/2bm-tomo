#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import time
from epics import PV
import h5py
import shutil
import os
import argparse

import traceback
import numpy as np
from datetime import datetime
import pathlib
import signal

from tomo2bm import log
from tomo2bm import flir
from tomo2bm import aps2bm
from tomo2bm import config
from tomo2bm import util

import matplotlib.pylab as pl
import matplotlib.widgets as wdg


from skimage import filters
from skimage.color import rgb2gray  # only needed for incorrectly saved images
from skimage.measure import regionprops
from skimage.feature import register_translation
import numexpr as ne

global variableDict

variableDict = {
        'SampleXIn': 0, 
        'SampleXOut': 4,
        'SampleRotStart': 0.0,
        'SampleRotEnd': 180.0,
        'AxisLocation': 0.0,
        'Roll': 0.0,
        'ScanRange': 2,                     # for focus scan: relative motion in mm
        'NSteps': 20,                       # for focus scan 
        'StabilizeSleep_ms': 250,           # for focus scan 
        # ####################### DO NOT MODIFY THE PARAMETERS BELOW ###################################
        'CCD_Readout': 0.006,               # options: 1. 8bit: 0.006, 2. 16-bit: 0.01
        # 'CCD_Readout': 0.01,                # options: 1. 8bit: 0.006, 2. 16-bit: 0.01
        'Station': '2-BM-A',
        'ExposureTime': 0.1,                # to use this as default value comment the variableDict['ExposureTime'] = global_PVs['Cam1_AcquireTime'].get() line
        'IOC_Prefix': '2bmbSP1:',           # options: 1. PointGrey: '2bmbPG3:', 2. Gbe '2bmbSP1:' 
        'DetectorResolution': 1.0
        }


def find_resolution(params):

    log.info('find resolution')
    global_PVs = aps2bm.init_general_PVs(params)
    aps2bm.user_info_update(global_PVs, params)

    params.file_name = None # so we don't run the flir._setup_hdf_writer 
    resolution = None
    try: 
        detector_sn = global_PVs['Cam1_SerialNumber'].get()
        if ((detector_sn == None) or (detector_sn == 'Unknown')):
            log.info('   *** The Point Grey Camera with EPICS IOC prefix %s is down' % params.camera_ioc_prefix)
            log.info('   *** Failed!')
        else:
            log.info('   *** The Point Grey Camera with EPICS IOC prefix %s and serial number %s is on' \
                        % (params.camera_ioc_prefix, detector_sn))

            flir.init(global_PVs, params)
            flir.set(global_PVs, params) 

            dark_field, white_field = flir.take_dark_and_white(global_PVs, params)

            log.info('  *** First image at X: %f mm' % (params.sample_in_position))
            log.info('  *** acquire first image')
            sphere_0 = normalize(flir.take_image(global_PVs, params), white_field, dark_field)

            second_image_x_position = params.sample_in_position + params.off_axis_position
            log.info('  *** Second image at X: %f mm' % (second_image_x_position))
            global_PVs["Motor_SampleX"].put(second_image_x_position, wait=True, timeout=600.0)
            log.info('  *** acquire second image')
            sphere_1 = normalize(flir.take_image(global_PVs, params), white_field, dark_field)

            # log.info('  *** moving X stage back to %f mm position' % (sample_in_position_start))
            # global_PVs["Motor_SampleX"].put(sample_in_position_start, wait=True, timeout=600.0)

            # # restore params.sample_in_position
            # params.sample_in_position = params_sample_in_position_start
            log.info('  *** moving X stage back to %f mm position' % (params.sample_in_position))
            aps2bm.move_sample_in(global_PVs, params)

            shift = register_translation(sphere_0, sphere_1, 10)

            log.info('  *** shift %f' % shift[1])

            params.resolution =  abs(params.off_axis_position) / np.abs(shift[0][0]) * 1000.0
            
            config.update_sphere(params)

            return params.resolution

    except  KeyError:
        log.error('  *** Some PV assignment failed!')
        pass


def normalize(arr, flat, dark, cutoff=None, out=None):
    """
    Normalize raw projection data using the flat and dark field projections.

    Parameters
    ----------
    arr : ndarray
        2D of projections.
    flat : ndarray
        2D flat field data.
    dark : ndarray
        2D dark field data.
    cutoff : float, optional
        Permitted maximum vaue for the normalized data.
    out : ndarray, optional
        Output array for result. If same as arr,
        process will be done in-place.

    Returns
    -------
    ndarray
        Normalized 2D tomographic data.
    """
    arr = util.as_float32(arr)
    l = np.float32(1e-5)
    log.info('  *** image size: [%d, %d]' % (flat.shape[0], flat.shape[1]))
    # flat = np.mean(flat, axis=0, dtype=np.float32)
    # dark = np.mean(dark, axis=0, dtype=np.float32)
    flat = flat.astype('float32')
    dark = dark.astype('float32')

    denom = ne.evaluate('flat')
    # denom = ne.evaluate('flat-dark')
    ne.evaluate('where(denom<l,l,denom)', out=denom)
    out = ne.evaluate('arr', out=out)
    # out = ne.evaluate('arr-dark', out=out)
    ne.evaluate('out/denom', out=out, truediv=True)
    if cutoff is not None:
        cutoff = np.float32(cutoff)
        ne.evaluate('where(out>cutoff,cutoff,out)', out=out)
    return out


def find_roll_and_rotation_axis_location(params):

    global_PVs = aps2bm.init_general_PVs(params)

    params.file_name = None # so we don't run the flir._setup_hdf_writer 
    rotation_axis_location = None
    roll = None

    try: 
        detector_sn = global_PVs['Cam1_SerialNumber'].get()
        if ((detector_sn == None) or (detector_sn == 'Unknown')):
            log.info('*** The Point Grey Camera with EPICS IOC prefix %s is down' % params.camera_ioc_prefix)
            log.info('  *** Failed!')
        else:
            log.info('*** The Point Grey Camera with EPICS IOC prefix %s and serial number %s is on' \
                        % (params.camera_ioc_prefix, detector_sn))

            flir.init(global_PVs, params)
            flir.set(global_PVs, params) 

            sphere_0, sphere_180 = take_sphere_0_180(global_PVs, params)

            cmass_0 = center_of_mass(sphere_0)
            cmass_180 = center_of_mass(sphere_180)

            rotation_axis_location = (cmass_180[1] + cmass_0[1]) / 2.0
            log.info('  *** shift (center of mass): [%f, %f]' % ((cmass_180[0] - cmass_0[0]) ,(cmass_180[1] - cmass_0[1])))
            # log.info('  *** difference horizontal center of mass %f' % (cmass_180[1] - cmass_0[1]))
            # log.info('  *** ratio %f' % ((cmass_180[0] - cmass_0[0]) / (cmass_180[1] - cmass_0[1])))

            roll = np.rad2deg(np.arctan((cmass_180[0] - cmass_0[0]) / (cmass_180[1] - cmass_0[1])))
            log.info("  *** roll:%f" % (roll))
            # plot(sphere_0)
            # plot(sphere_180)
            # plot(sphere_180[:,::-1])
            
            
            # shift = register_translation(sphere_0, sphere_180[:,::-1], 10)
            # print(shift)
            # log.info('  *** shift (cross correlation): [%f, %f]' % (shift[0][1],shift[0][0]))
            # log.info('  *** rotation axis location: %f' % (sphere_0.shape[0][1]/2.0 +(shift[0][1]/2)))
            # log.info('  *** rotation axis offset: %f' % (shift[0][1]/2))
            # rotation_axis_location = (sphere_0.shape[0][1]/2.0 + (shift[0][1]/2))
            # roll = np.rad2deg(np.arctan(shift[0][0]/shift[0][1]))
            # log.info("  *** new roll:%f" % (roll))


            # shift = register_translation(sphere_0, sphere_180, 1000, return_error=False)
            # roll = np.rad2deg(np.arctan(shift[0]/shift[1]))
            # log.info("new roll2:%f" % (roll))

        return rotation_axis_location, roll
    except  KeyError:
        log.error('  *** Some PV assignment failed!')
        pass


def take_sphere_0_180(global_PVs, params):


    dark_field, white_field = flir.take_dark_and_white(global_PVs, params)

    log.info('  *** moving rotary stage to %f deg position' % float(params.sample_rotation_start))
    global_PVs["Motor_SampleRot"].put(float(params.sample_rotation_start), wait=True, timeout=600.0)
    
    log.info('  *** acquire sphere at %f deg position' % float(params.sample_rotation_start))
    sphere_0 = normalize(flir.take_image(global_PVs, params), white_field, dark_field)
 
    log.info('  *** moving rotary stage to %f deg position' % float(params.sample_rotation_end))
    global_PVs["Motor_SampleRot"].put(float(params.sample_rotation_end), wait=True, timeout=600.0)
    
    log.info('  *** acquire sphere at %f deg position' % float(params.sample_rotation_end))
    sphere_180 = normalize(flir.take_image(global_PVs, params), white_field, dark_field)

    log.info('  *** moving rotary stage back to %f deg position' % float(params.sample_rotation_start))
    global_PVs["Motor_SampleRot"].put(float(params.sample_rotation_start), wait=True, timeout=600.0)
    
    return sphere_0, sphere_180


def center_of_mass(image):
    
    threshold_value = filters.threshold_otsu(image)
    log.info("threshold_value: %f" % (threshold_value))
    labeled_foreground = (image < threshold_value).astype(int)
    properties = regionprops(labeled_foreground, image)
    return properties[0].weighted_centroid
    # return properties[0].centroid


def center_rotation_axis(global_PVs, params):

    nCol = global_PVs['Cam1_SizeX_RBV'].get()
    
    log.info(' ')
    log.info('  *** centering rotation axis')

    current_axis_position = global_PVs["Motor_SampleX"].get()
    log.info('  *** current axis position: %f' % current_axis_position)
    time.sleep(.5)
    correction = (((nCol / 2.0) - variableDict['AxisLocation']) * variableDict['DetectorResolution'] / 1000.0) + current_axis_position
    log.info('  *** correction: %f' % correction)

    log.info('  *** moving to: %f (mm)' % correction)
    global_PVs["Motor_SampleX"].put(correction, wait=True, timeout=600.0)

    log.info('  *** re-setting position from %f (mm) to 0 (mm)' % correction)
    global_PVs["Motor_SampleX_SET"].put(1, wait=True, timeout=5.0)
    time.sleep(.5)
    global_PVs["Motor_SampleX"].put(0, wait=True, timeout=5.0)
    time.sleep(.5)
    global_PVs["Motor_SampleX_SET"].put(0, wait=True, timeout=5.0)


# def main():
#     home = os.path.expanduser("~")
#     logs_home = home + '/logs/'
#     # make sure logs directory exists
#     if not os.path.exists(logs_home):
#         os.makedirs(logs_home)

#     lfname = logs_home + 'auto.log'
#     # lfname = logs_home + datetime.strftime(datetime.now(), "%Y-%m-%d_%H:%M:%S") + '.log'
#     log.setup_logger(lfname)

#     # # create the top-level parser
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--res', action="store_true", default=False, help='measure the image resolution (μm/pixel)')
#     parser.add_argument('--axis', action="store_true", default=False, help='find the rotation axis location')
#     parser.add_argument('--roll', action="store_true", default=False, help='measure the rotation axis roll')
#     parser.add_argument('--pitch', action="store_true", default=False, help='measure the rotation axis pitch')
#     parser.add_argument('--focus', action="store_true", default=False, help='focus the scintillator screen')

#     args = parser.parse_args()

#     aps2bm.update_variable_dict(variableDict)
#     aps2bm.init_general_PVs(global_PVs, params)

#     try:
#         detector_sn = global_PVs['Cam1_SerialNumber'].get()
#         if ((detector_sn == None) or (detector_sn == 'Unknown')):
#             Logger("log").error('*** The Point Grey Camera with EPICS IOC prefix %s is down' % variableDict['IOC_Prefix'])
#             Logger("log").error('  *** Failed!')
#         else:
#             log.info('*** The Point Grey Camera with EPICS IOC prefix %s and serial number %s is on' \
#                 % (variableDict['IOC_Prefix'], detector_sn))
 
#             if args.res:
#                 log.info('  *** measuring the image resolution (μm/pixel)')
#                 variableDict['DetectorResolution'] = find_resolution(params)

#             if args.axis:
#                 log.info('  *** finding the rotation axis location')
#                 variableDict['AxisLocation'], variableDict['Roll'] = find_roll_and_rotation_axis_location(params)
#                 variableDict['DetectorResolution'] = find_resolution(params)
#                 center_rotation_axis(global_PVs, params) 

#             if args.roll:
#                 log.info('  *** measuring the rotation axis roll')
#                 log.warning('  *** not implemented')

#             if args.pitch:
#                 log.info('  *** measuring the rotation axis pitch')
#                 log.warning('  *** not implemented')
        
#             if args.focus:
#                 log.info('  *** focusing the scintillator screen')
#                 log.warning('  *** not implemented')
#                 # focus_scan(global_PVs, params)

#         log.info('  *** moving rotary stage to 0 deg position')
#         global_PVs["Motor_SampleRot"].put(0, wait=True, timeout=600.0)
#         log.info('  *** Done!')

#     except  KeyError:
#         Logger("log").error('  *** Some PV assignment failed!')
#         pass


# if __name__ == '__main__':
#     main()


# def focus_scan(global_PVs, params):
#     Logger("log").info(' ')

#     def cleanup(signal, frame):
#         stop_scan(global_PVs, params)
#         sys.exit(0)
#     signal.signal(signal.SIGINT, cleanup)

#     if variableDict.has_key('StopTheScan'):
#         stop_scan(global_PVs, params)
#         return

#     pgInit(global_PVs, params)
#     pgSet(global_PVs, params) 
#     open_shutters(global_PVs, params)

#     Logger("log").info('  *** start focus scan')
#     # Get the CCD parameters:
#     nRow = global_PVs['Cam1_SizeY_RBV'].get()
#     nCol = global_PVs['Cam1_SizeX_RBV'].get()
#     image_size = nRow * nCol

#     Motor_Name = global_PVs['Motor_Focus_Name'].get()
#     Logger("log").info('  *** Scanning ' + Motor_Name)

#     Motor_Start_Pos = global_PVs['Motor_Focus'].get() - float(variableDict['ScanRange']/2)
#     Motor_End_Pos = global_PVs['Motor_Focus'].get() + float(variableDict['ScanRange']/2)
#     vector_pos = numpy.linspace(Motor_Start_Pos, Motor_End_Pos, int(variableDict['NSteps']))
#     vector_std = numpy.copy(vector_pos)

#     global_PVs['Cam1_FrameType'].put(FrameTypeData, wait=True)
#     global_PVs['Cam1_NumImages'].put(1, wait=True)
#     global_PVs['Cam1_TriggerMode'].put('Off', wait=True)
#     wait_time_sec = int(variableDict['ExposureTime']) + 5

#     cnt = 0
#     for sample_pos in vector_pos:
#         Logger("log").info('  *** Motor position: %s' % sample_pos)
#         # for testing with out beam: comment focus motor motion
#         global_PVs['Motor_Focus'].put(sample_pos, wait=True)
#         time.sleep(float(variableDict['StabilizeSleep_ms'])/1000)
#         time.sleep(1)
#         global_PVs['Cam1_Acquire'].put(DetectorAcquire, wait=True, timeout=1000.0)
#         time.sleep(0.1)
#         if wait_pv(global_PVs['Cam1_Acquire'], DetectorIdle, wait_time_sec) == False: # adjust wait time
#             global_PVs['Cam1_Acquire'].put(DetectorIdle)
        
#         # Get the image loaded in memory
#         img_vect = global_PVs['Cam1_Image'].get(count=image_size)
#         #img = np.reshape(img_vect,[nRow, nCol])
#         vector_std[cnt] = numpy.std(img_vect)
#         Logger("log").info('  ***   *** Standard deviation: %s ' % str(vector_std[cnt]))
#         cnt = cnt + 1

#     # # move the lens to the focal position:
#     # max_std = numpy.max(vector_std)
#     # focal_pos = vector_pos[numpy.where(vector_std == max_std)]
#     # Logger("log").info('  *** Highest standard deviation: ', str(max_std))
#     # Logger("log").info('  *** Move piezo to ', str(focal_pos))
#     # global_PVs[Motor_Focus].put(focal_pos, wait=True)

#     # # Post scan:
#     # close_shutters(global_PVs, params)
#     # time.sleep(2)
#     # pgInit(global_PVs, params)
    
#     return
