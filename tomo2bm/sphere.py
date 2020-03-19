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


def adjust(params):
    global_PVs = aps2bm.init_general_PVs(params)

    params.file_name = None # so we don't run the flir._setup_hdf_writer 

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

            dark_field, white_field = flir.take_dark_and_white(global_PVs, params)

            if (params.resolution=='True'):
                find_resolution(global_PVs,params, dark_field, white_field, angle_shift = -0.7)            
            if (params.focus=='True'):
                adjust_focus(global_PVs,params)
            if (params.center=='True'):
                adjust_center(global_PVs,params, dark_field, white_field)
            if(params.roll=='True'):
                adjust_roll(global_PVs,params, dark_field, white_field, angle_shift = -0.7)
            if(params.pitch=='True'):                
                adjust_pitch(global_PVs,params, dark_field, white_field, angle_shift = -0.7)
            if(params.roll=='True' or params.pitch=='True'):
                # align center again for higher accuracy            
                adjust_center(global_PVs,params, dark_field, white_field)

    except  KeyError:
        log.error('  *** Some PV assignment failed!')
        pass

def adjust_center(global_PVs,params,dark_field,white_field):
    log.warning(' *** Adjusting center ***')              
    for ang in [10,45]: 
        log.info('  *** take 3 spheres with angular step %f deg ***' % float(ang))

        #sphere 0
        log.info('  *** moving rotary stage to %f deg position ***' % float(0))
        global_PVs["Motor_SampleRot"].put(float(0), wait=True, timeout=600.0)            
        log.info('  *** acquire sphere at %f deg position ***' % float(0))                                
        sphere_0 = normalize(flir.take_image(global_PVs, params), white_field, dark_field)    

        #sphere 1
        log.info('  *** moving rotary stage to %f deg position ***' % float(ang))                
        global_PVs["Motor_SampleRot"].put(float(ang), wait=True, timeout=600.0)
        log.info('  *** acquire sphere at %f deg position ***' % float(ang))                                 
        sphere_1 = normalize(flir.take_image(global_PVs, params), white_field, dark_field)
        
        #sphere 2
        log.info('  *** moving rotary stage to %f deg position ***' % float(2*ang))                                
        global_PVs["Motor_SampleRot"].put(float(2*ang), wait=True, timeout=600.0)
        log.info('  *** acquire sphere at %f deg position ***' % float(2*ang))                                                 
        sphere_2 = normalize(flir.take_image(global_PVs, params), white_field, dark_field)

        # find shifts
        shift0 = register_translation(sphere_1, sphere_0, 100)[0][1]
        shift1 = register_translation(sphere_2, sphere_1, 100)[0][1]
        a = ang*np.pi/180
        # x=-(1/4) (d1+d2-2 d1 Cos[a]) Csc[a/2]^2,
        x = -(1/4)*(shift0+shift1-2*shift0*np.cos(a))*1/np.sin(a/2)**2
        # r = 1/2 Csc[a/2]^2 Csc[a] Sqrt[(d1^2+d2^2-2 d1 d2 Cos[a]) Sin[a/2]^2]
        r = 1/2*1/np.sin(a/2)**2*1/np.sin(a)*np.sqrt(np.abs((shift0**2+shift1**2-2*shift0*shift1*np.cos(a))*np.sin(a/2)**2))
        # g = ArcCos[((-d1-d2+2 d1 Cos[a]) Sin[a])/(2 Sqrt[(d1^2+d2^2-2 d1 d2 Cos[a]) Sin[a/2]^2])]
        g = np.arccos(((-shift0-shift1+2*shift0*np.cos(a))*np.sin(a))/(2*np.sqrt(np.abs((shift0**2+shift1**2-2*shift0*shift1*np.cos(a))*np.sin(a/2)**2))))
        y = r*np.sin(g)*np.sign(shift0) 
        
        # find center of mass
        cmass_0 = center_of_mass(sphere_0)
        
        log.info('  *** position of the initial sphere wrt to the rotation center (%f,%f) ***' % (x,y))
        log.info('  *** center of mass for the initial sphere (%f,%f) ***' % (cmass_0[1],cmass_0[0]))
        log.info('  *** moving sphere to the position of the rotation center ***')
        global_PVs["Motor_Sample_Top_0"].put(global_PVs["Motor_Sample_Top_0"].get()+x*params.image_resolution/1000, wait=True, timeout=5.0)                
        global_PVs["Motor_Sample_Top_90"].put(global_PVs["Motor_Sample_Top_90"].get()+y*params.image_resolution/1000, wait=True, timeout=5.0)                
        log.info('  *** moving rotation center to the detector center ***')
        global_PVs["Motor_SampleX"].put(global_PVs["Motor_SampleX"].get()-(cmass_0[1]-x-global_PVs['Cam1_SizeX'].get()/2)*params.image_resolution/1000, wait=True, timeout=600.0)

        log.info('  *** moving rotary stage to %f deg position ***' % float(0))
        global_PVs["Motor_SampleRot"].put(float(0), wait=True, timeout=600.0)            
        log.info('  *** acquire sphere at %f deg position ***' % float(0))                                

        log.info('  *** TEST: acquire sphere at %f deg position ***' % float(0)) 
        sphere_0 = normalize(flir.take_image(global_PVs, params), white_field, dark_field)                   
        cmass_0 = center_of_mass(sphere_0)
        log.info('  *** TEST: center of mass for the sphere at 0 deg (%f,%f) ***' % (cmass_0[1],cmass_0[0]))
        
def adjust_roll(global_PVs,params, dark_field, white_field,angle_shift):

    log.warning(' *** Adjusting roll ***')
    log.info('  *** moving rotary stage to %f deg position ***' % float(0+angle_shift))                                                
    global_PVs["Motor_SampleRot"].put(float(0+angle_shift), wait=True, timeout=600.0)    
    log.info('  *** moving sphere to the detector border ***')                                                
    global_PVs["Motor_Sample_Top_0"].put(global_PVs["Motor_Sample_Top_0"].get()+global_PVs['Cam1_SizeX'].get()/2*params.image_resolution/1000-0.27, wait=True, timeout=600.0)
    log.info('  *** acquire sphere at %f deg position ***' % float(0+angle_shift)) 
    sphere_0 = normalize(flir.take_image(global_PVs, params), white_field, dark_field)       
    log.info('  *** moving rotary stage to %f deg position ***' % float(180+angle_shift))                                                            
    global_PVs["Motor_SampleRot"].put(float(180+angle_shift), wait=True, timeout=600.0)            
    log.info('  *** acquire sphere at %f deg position ***' % float(180+angle_shift)) 
    sphere_180 = normalize(flir.take_image(global_PVs, params), white_field, dark_field)

    cmass_0 = center_of_mass(sphere_0)
    cmass_180 = center_of_mass(sphere_180)          
    log.info('  *** center of mass for the sphere at 0 deg (%f,%f) ***' % (cmass_0[1],cmass_0[0]))
    log.info('  *** center of mass for the sphere at 180 deg (%f,%f) ***' % (cmass_180[1],cmass_180[0]))
  
    roll = np.rad2deg(np.arctan((cmass_180[0] - cmass_0[0]) / (cmass_180[1] - cmass_0[1])))
    log.warning('  *** found roll error: %f' % roll)


    log.info('  *** moving rotary stage to %f deg position ***' % float(0+angle_shift))                                                            
    global_PVs["Motor_SampleRot"].put(float(0+angle_shift), wait=True, timeout=600.0)    
    log.info('  *** moving sphere back to the detector center ***')                                                            
    global_PVs["Motor_Sample_Top_0"].put(global_PVs["Motor_Sample_Top_0"].get()-(global_PVs['Cam1_SizeX'].get()/2*params.image_resolution/1000-0.27), wait=True, timeout=600.0)
    
    log.info('  *** find shifts resulting by the roll change ***')                                                            
    log.info('  *** acquire sphere at the current roll position ***')             
    sphere_0 = normalize(flir.take_image(global_PVs, params), white_field, dark_field)           

    ang = roll/2 # if roll is too big then ang should be decreased to keep the sphere in the field of view
    log.info('  *** acquire sphere after testing roll change %f ***' % float(global_PVs["Motor_Roll"].get()+ang))                                     
    global_PVs["Motor_Roll"].put(global_PVs["Motor_Roll"].get()+ang, wait=True, timeout=600.0)
    sphere_1 = normalize(flir.take_image(global_PVs, params), white_field, dark_field)

    shift0 = register_translation(sphere_1, sphere_0, 100)[0][1]            
    shift1 = shift0*np.sin(roll)*(np.cos(roll)*1/np.tan(ang)+np.sin(roll))
    log.info('  *** the testing roll change corresponds to %f shift in x, calculated resulting roll change gives %f shift in x ***' % (shift0,shift1))             
    log.warning('  *** change roll to %f ***' % float(global_PVs["Motor_Roll"].get()+roll-ang))
    global_PVs["Motor_Roll"].put(global_PVs["Motor_Roll"].get()+roll-ang, wait=True, timeout=600.0)
    log.info('  *** moving sphere to the detector center ***')
    global_PVs["Motor_SampleX"].put(global_PVs["Motor_SampleX"].get()-shift1*params.image_resolution/1000, wait=True, timeout=600.0)
    

    log.info('  *** TEST: acquire sphere at %f deg position ***' % float(0+angle_shift)) 
    sphere_0 = normalize(flir.take_image(global_PVs, params), white_field, dark_field)                   
    cmass_0 = center_of_mass(sphere_0)
    log.info('  *** TEST: center of mass for the sphere at 0 deg (%f,%f) ***' % (cmass_0[1],cmass_0[0]))

def adjust_pitch(global_PVs,params, dark_field, white_field,angle_shift):
    
    log.warning(' *** Adjusting pitch ***')              
    log.info('  *** acquire sphere after moving it along the beam axis by 1mm ***')             
    global_PVs["Motor_Sample_Top_90"].put(global_PVs["Motor_Sample_Top_90"].get()-1.0, wait=True, timeout=600.0)            

    log.info('  *** moving rotary stage to %f deg position ***' % float(0+angle_shift))                                                            
    global_PVs["Motor_SampleRot"].put(float(0+angle_shift), wait=True, timeout=600.0)                
    log.info('  *** acquire sphere at %f deg position ***' % float(0+angle_shift))             
    sphere_0 = normalize(flir.take_image(global_PVs, params), white_field, dark_field)         

    log.info('  *** moving rotary stage to %f deg position ***' % float(0+angle_shift))                                                            
    global_PVs["Motor_SampleRot"].put(float(180+angle_shift), wait=True, timeout=600.0)            
    log.info('  *** acquire sphere at %f deg position ***' % float(180+angle_shift))             
    sphere_180 = normalize(flir.take_image(global_PVs, params), white_field, dark_field)

    cmass_0 = center_of_mass(sphere_0)            
    cmass_180 = center_of_mass(sphere_180)   
    log.info('  *** center of mass for the initial sphere (%f,%f) ***' % (cmass_0[1],cmass_0[0]))
    log.info('  *** center of mass for the shifted sphere (%f,%f) ***' % (cmass_180[1],cmass_180[0]))                                 
    pitch = np.rad2deg(np.arctan((cmass_180[0] - cmass_0[0])*params.image_resolution/1000 / 2.0))
    log.warning('  *** found pitch error: %f' % pitch)
    log.info('  *** acquire sphere back along the beam axis by -1mm ***')             
    global_PVs["Motor_Sample_Top_90"].put(global_PVs["Motor_Sample_Top_90"].get()+1.0, wait=True, timeout=600.0)
    log.warning('  *** change pitch to %f ***' % float(global_PVs["Motor_Pitch"].get()-pitch))             
    global_PVs["Motor_Pitch"].put(global_PVs["Motor_Pitch"].get()-pitch, wait=True, timeout=600.0)
    global_PVs["Motor_SampleRot"].put(float(0+angle_shift), wait=True, timeout=600.0)    
    
    log.info('  *** TEST: acquire sphere at %f deg position ***' % float(0+angle_shift)) 
    sphere_0 = normalize(flir.take_image(global_PVs, params), white_field, dark_field)                   
    cmass_0 = center_of_mass(sphere_0)
    log.info('  *** TEST: center of mass for the sphere at 0 deg (%f,%f) ***' % (cmass_0[1],cmass_0[0]))            


def find_resolution(global_PVs, params, dark_field, white_field, angle_shift):

    log.warning(' *** Find resolution ***')
    log.info('  *** moving rotary stage to %f deg position ***' % float(0+angle_shift))                                                            
    global_PVs["Motor_SampleRot"].put(float(0+angle_shift), wait=True, timeout=600.0)    
    log.info('  *** First image at X: %f mm' % (params.sample_in_position))
    log.info('  *** acquire first image')

    sphere_0 = normalize(flir.take_image(global_PVs, params), white_field, dark_field)

    second_image_x_position = params.sample_in_position + params.off_axis_position
    log.info('  *** Second image at X: %f mm' % (second_image_x_position))
    global_PVs["Motor_SampleX"].put(second_image_x_position, wait=True, timeout=600.0)
    log.info('  *** acquire second image')
    sphere_1 = normalize(flir.take_image(global_PVs, params), white_field, dark_field)

    log.info('  *** moving X stage back to %f mm position' % (params.sample_in_position))
    aps2bm.move_sample_in(global_PVs, params)

    shift = register_translation(sphere_0, sphere_1, 100)
    log.info('  *** shift X: %f, Y: %f' % (shift[0][1],shift[0][0]))
    image_resolution =  abs(params.off_axis_position) / np.linalg.norm(shift[0]) * 1000.0
    
    log.warning('  *** found resolution %f um/pixel' % (image_resolution))    
    params.image_resolution = image_resolution
    config.update_sphere(params)
    aps2bm.image_resolution_pv_update(global_PVs, params)            

def adjust_focus(global_PVs, params):
    
    step = 1
    
    direction = 1
    max_std = 0
    three_std = np.ones(3)*2**16
    cnt = 0
    decrease_step = False
    while(step>0.01):
        initpos = global_PVs['Motor_Focus'].get()
        curpos = initpos + step*direction
        global_PVs['Motor_Focus'].put(curpos, wait=True, timeout=600.0)
        img = flir.take_image(global_PVs, params)        
        cur_std = np.std(img)
        log.info('  ***   *** Positon: %f Standard deviation: %f ' % (curpos,cur_std))
        if(cur_std > max_std): # store max std
            max_std = cur_std
        three_std[np.mod(cnt,3)] = cur_std # store std for 3 last measurements 
        if(np.sum(three_std<max_std)==3):# pass a peak
            direction = -direction
            if(decrease_step):# decrease focusing motor step
                step/=2
            else:#do not decrease step for the first direction change
                decrease_step = True
            three_std = np.ones(3)*2**16
            max_std = 0
            log.warning('  *** change direction and step to %f' % (step))
        cnt+=1

    log.warning('  *** Focusing done')

    return


def center_of_mass(image):
    
    threshold_value = filters.threshold_otsu(image)
    log.info("  *** threshold_value: %f" % (threshold_value))
    labeled_foreground = (image < threshold_value).astype(int)
    properties = regionprops(labeled_foreground, image)
    return properties[0].weighted_centroid
    #return properties[0].centroid

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
