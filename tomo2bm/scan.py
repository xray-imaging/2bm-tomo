'''
    Scan Lib for Sector 2-BM
    
'''
import sys
import time
import signal
import numpy as np

from tomo2bm import dm
from tomo2bm import log
from tomo2bm import flir
from tomo2bm import aps2bm
from tomo2bm import config

global_PVs = {}


def fly_scan(params):

    tic =  time.time()
    # aps2bm.update_variable_dict(params)
    global_PVsx = aps2bm.init_general_PVs(global_PVs, params)
    try: 
        detector_sn = global_PVs['Cam1_SerialNumber'].get()
        if ((detector_sn == None) or (detector_sn == 'Unknown')):
            log.info('*** The Point Grey Camera with EPICS IOC prefix %s is down' % params.camera_ioc_prefix)
            log.info('  *** Failed!')
        else:
            log.info('*** The Point Grey Camera with EPICS IOC prefix %s and serial number %s is on' \
                        % (params.camera_ioc_prefix, detector_sn))
            
            # calling global_PVs['Cam1_AcquireTime'] to replace the default 'ExposureTime' with the one set in the camera
            params.exposure_time = global_PVs['Cam1_AcquireTime'].get()
            # calling calc_blur_pixel() to replace the default 'SlewSpeed' 
            blur_pixel, rot_speed, scan_time = calc_blur_pixel(global_PVs, params)
            params.slew_speed = rot_speed

            # init camera
            flir.init(global_PVs, params)

            log.info(' ')
            log.info("  *** Running %d sleep scans" % params.sleep_steps)
            for i in np.arange(0, params.sleep_steps, 1):
                tic_01 =  time.time()
                # set sample file name
                # fname = str('{:03}'.format(global_PVs['HDF1_FileNumber'].get())) + '_' + global_PVs['Sample_Name'].get(as_string=True)
                params.file_path = global_PVs['HDF1_FilePath'].get(as_string=True)
                params.file_name = str('{:03}'.format(global_PVs['HDF1_FileNumber'].get())) + '_' + global_PVs['Sample_Name'].get(as_string=True)
                log.info(' ')
                log.info('  *** Start scan %d' % i)
                tomo_fly_scan(global_PVs, params)
                if ((i+1)!= params.sleep_steps):
                    log.warning('  *** Wait (s): %s ' % str(params.sleep_time))
                    time.sleep(params.sleep_time) 

                log.info(' ')
                log.info('  *** Data file: %s' % global_PVs['HDF1_FullFileName_RBV'].get(as_string=True))
                log.info('  *** Total scan time: %s minutes' % str((time.time() - tic_01)/60.))
                log.info('  *** Scan Done!')
    
                dm.scp(global_PVs, params)

            log.info('  *** Total loop scan time: %s minutes' % str((time.time() - tic)/60.))
 
            log.info('  *** Moving rotary stage to start position')
            global_PVs["Motor_SampleRot"].put(0, wait=True, timeout=600.0)
            log.info('  *** Moving rotary stage to start position: Done!')

            global_PVs['Cam1_ImageMode'].put('Continuous')
 
            log.info('  *** Done!')

    except  KeyError:
        log.error('  *** Some PV assignment failed!')
        pass


def fly_scan_vertical(params):

    tic =  time.time()
    # aps2bm.update_variable_dict(params)
    global_PVsx = aps2bm.init_general_PVs(global_PVs, params)
    try: 
        detector_sn = global_PVs['Cam1_SerialNumber'].get()
        if ((detector_sn == None) or (detector_sn == 'Unknown')):
            log.info('*** The Point Grey Camera with EPICS IOC prefix %s is down' % params.camera_ioc_prefix)
            log.info('  *** Failed!')
        else:
            log.info('*** The Point Grey Camera with EPICS IOC prefix %s and serial number %s is on' \
                        % (params.camera_ioc_prefix, detector_sn))
            
            # calling global_PVs['Cam1_AcquireTime'] to replace the default 'ExposureTime' with the one set in the camera
            params.exposure_time = global_PVs['Cam1_AcquireTime'].get()
            # calling calc_blur_pixel() to replace the default 'SlewSpeed' 
            blur_pixel, rot_speed, scan_time = calc_blur_pixel(global_PVs, params)
            params.slew_speed = rot_speed

            start_y = params.vertical_scan_start
            end_y = params.vertical_scan_end
            step_size_y = params.vertical_scan_step_size

            # init camera
            flir.init(global_PVs, params)

            log.info(' ')
            log.info("  *** Running %d scans" % params.sleep_steps)
            log.info(' ')
            log.info('  *** Vertical Positions (mm): %s' % np.arange(start_y, end_y, step_size_y))

            for ii in np.arange(0, params.sleep_steps, 1):
                log.info(' ')
                log.info('  *** Start scan %d' % ii)
                for i in np.arange(start_y, end_y, step_size_y):
                    tic_01 =  time.time()
                    # set sample file name
                    params.file_path = global_PVs['HDF1_FilePath'].get(as_string=True)
                    params.file_name = str('{:03}'.format(global_PVs['HDF1_FileNumber'].get())) + '_' + global_PVs['Sample_Name'].get(as_string=True)

                    log.info(' ')
                    log.info('  *** The sample vertical position is at %s mm' % (i))
                    global_PVs['Motor_SampleY'].put(i, wait=True, timeout=1000.0)
                    tomo_fly_scan(global_PVs, params)

                    log.info(' ')
                    log.info('  *** Data file: %s' % global_PVs['HDF1_FullFileName_RBV'].get(as_string=True))
                    log.info('  *** Total scan time: %s minutes' % str((time.time() - tic_01)/60.))
                    log.info('  *** Scan Done!')
        
                    dm.scp(global_PVs, params)

                log.info('  *** Moving vertical stage to start position')
                global_PVs['Motor_SampleY'].put(start_y, wait=True, timeout=1000.0)

                if ((ii+1)!=params.sleep_steps):
                    log.warning('  *** Wait (s): %s ' % str(params.sleep_time))
                    time.sleep(params.sleep_time) 

            log.info('  *** Total loop scan time: %s minutes' % str((time.time() - tic)/60.))
            log.info('  *** Moving rotary stage to start position')
            global_PVs["Motor_SampleRot"].put(0, wait=True, timeout=600.0)
            log.info('  *** Moving rotary stage to start position: Done!')

            global_PVs['Cam1_ImageMode'].put('Continuous')
 
            log.info('  *** Done!')

    except  KeyError:
        log.error('  *** Some PV assignment failed!')
        pass


def fly_scan_mosaic(params):

    tic =  time.time()
    # aps2bm.update_variable_dict(params)
    global_PVsx = aps2bm.init_general_PVs(global_PVs, params)
    try: 
        detector_sn = global_PVs['Cam1_SerialNumber'].get()
        if ((detector_sn == None) or (detector_sn == 'Unknown')):
            log.info('*** The Point Grey Camera with EPICS IOC prefix %s is down' % params.camera_ioc_prefix)
            log.info('  *** Failed!')
        else:
            log.info('*** The Point Grey Camera with EPICS IOC prefix %s and serial number %s is on' \
                        % (params.camera_ioc_prefix, detector_sn))
            
            # calling global_PVs['Cam1_AcquireTime'] to replace the default 'ExposureTime' with the one set in the camera
            params.exposure_time = global_PVs['Cam1_AcquireTime'].get()
            # calling calc_blur_pixel() to replace the default 'SlewSpeed' 
            blur_pixel, rot_speed, scan_time = calc_blur_pixel(global_PVs, params)
            params.slew_speed = rot_speed

            start_y = params.vertical_scan_start
            end_y = params.vertical_scan_end
            step_size_y = params.vertical_scan_step_size


            start_x = params.horizontal_scan_start
            end_x = params.horizontal_scan_end
            step_size_x = params.horizontal_scan_step_size

            # set scan stop so also ends are included
            stop_x = end_x + step_size_x
            stop_y = end_y + step_size_y

            # init camera
            flir.init(global_PVs, params)

            log.info(' ')
            log.info("  *** Running %d sleep scans" % params.sleep_steps)
            for ii in np.arange(0, params.sleep_steps, 1):
                tic_01 =  time.time()

                log.info(' ')
                log.info("  *** Running %d mosaic scans" % (len(np.arange(start_x, stop_x, step_size_x)) * len(np.arange(start_y, stop_y, step_size_y))))
                log.info(' ')
                log.info('  *** Horizontal Positions (mm): %s' % np.arange(start_x, stop_x, step_size_x))
                log.info('  *** Vertical Positions (mm): %s' % np.arange(start_y, stop_y, step_size_y))

                h = 0
                v = 0
                
                for i in np.arange(start_y, stop_y, step_size_y):
                    log.info(' ')
                    log.error('  *** The sample vertical position is at %s mm' % (i))
                    global_PVs['Motor_SampleY'].put(i, wait=True)
                    for j in np.arange(start_x, stop_x, step_size_x):
                        log.error('  *** The sample horizontal position is at %s mm' % (j))
                        params.sample_in_position = j
                        # set sample file name
                        params.file_path = global_PVs['HDF1_FilePath'].get(as_string=True)
                        params.file_name = str('{:03}'.format(global_PVs['HDF1_FileNumber'].get())) + '_' + global_PVs['Sample_Name'].get(as_string=True) + '_y' + str(v) + '_x' + str(h)
                        tomo_fly_scan(global_PVs, params)
                        h = h + 1
                        dm.scp(global_PVs, params)
                    log.info(' ')
                    log.info('  *** Total scan time: %s minutes' % str((time.time() - tic)/60.))
                    log.info('  *** Data file: %s' % global_PVs['HDF1_FullFileName_RBV'].get(as_string=True))
                    v = v + 1
                    h = 0

                log.info('  *** Moving vertical stage to start position')
                global_PVs['Motor_SampleY'].put(start_y, wait=True, timeout=1000.0)

                log.info('  *** Moving horizontal stage to start position')
                global_PVs['Motor_SampleX'].put(start_x, wait=True, timeout=1000.0)

                log.info('  *** Moving rotary stage to start position')
                global_PVs["Motor_SampleRot"].put(0, wait=True, timeout=600.0)
                log.info('  *** Moving rotary stage to start position: Done!')

                if ((ii+1)!=params.sleep_steps):
                    log.warning('  *** Wait (s): %s ' % str(params.sleep_time))
                    time.sleep(params.sleep_time) 

                global_PVs['Cam1_ImageMode'].put('Continuous')

                log.info('  *** Done!')

    except  KeyError:
        log.error('  *** Some PV assignment failed!')
        pass


def dummy_scan(params):
    tic =  time.time()
    # aps2bm.update_variable_dict(params)
    global_PVsx = aps2bm.init_general_PVs(global_PVs, params)
    try: 
        detector_sn = global_PVs['Cam1_SerialNumber'].get()
        if ((detector_sn == None) or (detector_sn == 'Unknown')):
            log.info('*** The Point Grey Camera with EPICS IOC prefix %s is down' % params.camera_ioc_prefix)
            log.info('  *** Failed!')
        else:
            log.info('*** The Point Grey Camera with EPICS IOC prefix %s and serial number %s is on' \
                        % (params.camera_ioc_prefix, detector_sn))
    except  KeyError:
        log.error('  *** Some PV assignment failed!')
        pass


def set_image_factor(global_PVs, params):

    if (params.recursive_filter == False):
        params.recursive_filter_n_images = 1 
    return params.recursive_filter_n_images

   
def tomo_fly_scan(global_PVs, params):
    log.info(' ')
    log.info('  *** start_scan')

    def cleanup(signal, frame):
        stop_scan(global_PVs, params)
        sys.exit(0)
    signal.signal(signal.SIGINT, cleanup)

    # if params.has_key('StopTheScan'):
    #     stop_scan(global_PVs, params)
    #     return

    # moved to outer loop in main()
    # init(global_PVs, params)
    set_image_factor(global_PVs, params)
    set_pso(global_PVs, params)

    # fname = global_PVs['HDF1_FileName'].get(as_string=True)
    log.info('  *** File name prefix: %s' % params.file_name)
    flir.set(global_PVs, params) 

    aps2bm.open_shutters(global_PVs, params)
    move_sample_in(global_PVs, params)
    theta = flir.acquire(global_PVs, params)

    theta_end =  global_PVs['Motor_SampleRot_RBV'].get()
    if (0 < theta_end < 180.0):
        # print('\x1b[2;30;41m' + '  *** Rotary Stage ERROR. Theta stopped at: ***' + theta_end + '\x1b[0m')
        log.error('  *** Rotary Stage ERROR. Theta stopped at: %s ***' % str(theta_end))

    move_sample_out(global_PVs, params)
    flir.acquire_flat(global_PVs, params)
    move_sample_in(global_PVs, params)

    aps2bm.close_shutters(global_PVs, params)
    time.sleep(2)

    flir.acquire_dark(global_PVs, params)
    flir.checkclose_hdf(global_PVs, params)
    flir.add_theta(global_PVs, params, theta)

    # update config file
    config.update_config(params)


def calc_blur_pixel(global_PVs, params):
    """
    Calculate the blur error (pixel units) due to a rotary stage fly scan motion durng the exposure.
    
    Parameters
    ----------
    params.exposure_time: float
        Detector exposure time
    params.ccd_readout : float
        Detector read out time
    variableDict[''roiSizeX''] : int
        Detector X size
    params.sample_rotation_end : float
        Tomographic scan angle end
    params.sample_rotation_start : float
        Tomographic scan angle start
    variableDict[''Projections'] : int
        Numember of projections

    Returns
    -------
    float
        Blur error in pixel. For good quality reconstruction this should be < 0.2 pixel.
    """

    angular_range =  params.sample_rotation_end -  params.sample_rotation_start
    angular_step = angular_range/params.num_projections
    scan_time = params.num_projections * (params.exposure_time + params.ccd_readout)
    rot_speed = angular_range / scan_time
    frame_rate = params.num_projections / scan_time
    blur_delta = params.exposure_time * rot_speed
 
   
    mid_detector = global_PVs['Cam1_MaxSizeX_RBV'].get() / 2.0
    blur_pixel = mid_detector * (1 - np.cos(blur_delta * np.pi /180.))

    log.info(' ')
    log.info('  *** Calc blur pixel')
    log.info("  *** *** Total # of proj: %s " % params.num_projections)
    log.info("  *** *** Exposure Time: %s s" % params.exposure_time)
    log.info("  *** *** Readout Time: %s s" % params.ccd_readout)
    log.info("  *** *** Angular Range: %s degrees" % angular_range)
    log.info("  *** *** Camera X size: %s " % global_PVs['Cam1_SizeX'].get())
    log.info(' ')
    log.info("  *** *** *** *** Angular Step: %f degrees" % angular_step)   
    log.info("  *** *** *** *** Scan Time: %f s" % scan_time) 
    log.info("  *** *** *** *** Rot Speed: %f degrees/s" % rot_speed)
    log.info("  *** *** *** *** Frame Rate: %f fps" % frame_rate)
    log.info("  *** *** *** *** Max Blur: %f pixels" % blur_pixel)
    log.info('  *** Calc blur pixel: Done!')
    
    return blur_pixel, rot_speed, scan_time


def move_sample_out(global_PVs, params):

    log.info('      *** Sample out')
    if not (params.sample_move_freeze):
        if (params.sample_in_out=="vertical"):
            log.info('      *** *** Move Sample Y out at: %f' % params.sample_out_position)
            global_PVs['Motor_SampleY'].put(str(params.sample_out_position), wait=True, timeout=1000.0)                
            if aps2bm.wait_pv(global_PVs['Motor_SampleY'], float(params.sample_out_position), 60) == False:
                log.error('Motor_SampleY did not move in properly')
                log.error(global_PVs['Motor_SampleY'].get())
        else:
            if (params.use_furnace):
                log.info('      *** *** Move Furnace Y out at: %f' % params.furnace_out_position)
                global_PVs['Motor_FurnaceY'].put(str(params.furnace_out_position), wait=True, timeout=1000.0)
                if aps2bm.wait_pv(global_PVs['Motor_FurnaceY'], float(params.furnace_out_position), 60) == False:
                    log.error('Motor_FurnaceY did not move in properly')
                    log.error(global_PVs['Motor_FurnaceY'].get())
            log.info('      *** *** Move Sample X out at: %f' % params.sample_out_position)
            global_PVs['Motor_SampleX'].put(str(params.sample_out_position), wait=True, timeout=1000.0)
            if aps2bm.wait_pv(global_PVs['Motor_SampleX'], float(params.sample_out_position), 60) == False:
                log.error('Motor_SampleX did not move in properly')
                log.error(global_PVs['Motor_SampleX'].get())
    else:
        log.info('      *** *** Sample Stack is Frozen')


def move_sample_in(global_PVs, params):

    log.info('      *** Sample in')
    if not (params.sample_move_freeze):
        if (params.sample_in_out=="vertical"):
            log.info('      *** *** Move Sample Y in at: %f' % params.sample_in_position)
            global_PVs['Motor_SampleY'].put(str(params.sample_in_position), wait=True, timeout=1000.0)                
            if aps2bm.wait_pv(global_PVs['Motor_SampleY'], float(params.sample_in_position), 60) == False:
                log.error('Motor_SampleY did not move in properly')
                log.error(global_PVs['Motor_SampleY'].get())
        else:
            log.info('      *** *** Move Sample X in at: %f' % params.sample_in_position)
            global_PVs['Motor_SampleX'].put(str(params.sample_in_position), wait=True, timeout=1000.0)
            if aps2bm.wait_pv(global_PVs['Motor_SampleX'], float(params.sample_in_position), 60) == False:
                log.error('Motor_SampleX did not move in properly')
                log.error(global_PVs['Motor_SampleX'].get())
            if (params.use_furnace):
                log.info('      *** *** Move Furnace Y in at: %f' % params.furnace_in_position)
                global_PVs['Motor_FurnaceY'].put(str(params.furnace_in_position), wait=True, timeout=1000.0)
                if aps2bm.wait_pv(global_PVs['Motor_FurnaceY'], float(params.furnace_in_position), 60) == False:
                    log.error('Motor_FurnaceY did not move in properly')
                    log.error(global_PVs['Motor_FurnaceY'].get())
    else:
        log.info('      *** *** Sample Stack is Frozen')


def stop_scan(global_PVs, params):
        log.info(' ')
        log.error('  *** Stopping the scan: PLEASE WAIT')
        global_PVs['Motor_SampleRot_Stop'].put(1)
        global_PVs['HDF1_Capture'].put(0)
        aps2bm.wait_pv(global_PVs['HDF1_Capture'], 0)
        flir.init(global_PVs, params)
        log.error('  *** Stopping scan: Done!')
        ##init(global_PVs, params)


def set_pso(global_PVs, params):

    acclTime = 1.0 * params.slew_speed/params.accl_rot
    scanDelta = abs(((float(params.sample_rotation_end) - float(params.sample_rotation_start))) / ((float(params.num_projections)) * float(params.recursive_filter_n_images)))

    log.info('  *** *** start_pos %f' % float(params.sample_rotation_start))
    log.info('  *** *** end pos %f' % float(params.sample_rotation_end))

    global_PVs['Fly_StartPos'].put(float(params.sample_rotation_start), wait=True)
    global_PVs['Fly_EndPos'].put(float(params.sample_rotation_end), wait=True)
    global_PVs['Fly_SlewSpeed'].put(params.slew_speed, wait=True)
    global_PVs['Fly_ScanDelta'].put(scanDelta, wait=True)
    time.sleep(3.0)

    calc_num_proj = global_PVs['Fly_Calc_Projections'].get()
    
    if calc_num_proj == None:
        log.error('  *** *** Error getting fly calculated number of projections!')
        calc_num_proj = global_PVs['Fly_Calc_Projections'].get()
        log.error('  *** *** Using %s instead of %s' % (calc_num_proj, params.num_projections))
    if calc_num_proj != int(params.num_projections):
        log.warning('  *** *** Changing number of projections from: %s to: %s' % (params.num_projections, int(calc_num_proj)))
        params.num_projections = int(calc_num_proj)
    log.info('  *** *** Number of projections: %d' % int(params.num_projections))
    log.info('  *** *** Fly calc triggers: %d' % int(calc_num_proj))
    global_PVs['Fly_ScanControl'].put('Standard')

    log.info(' ')
    log.info('  *** Taxi before starting capture')
    global_PVs['Fly_Taxi'].put(1, wait=True)
    aps2bm.wait_pv(global_PVs['Fly_Taxi'], 0)
    log.info('  *** Taxi before starting capture: Done!')


