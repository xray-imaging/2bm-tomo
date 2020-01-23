'''
    Data Management Lib for Sector 32-ID internal data transfer
    
'''
from __future__ import print_function

import os
import subprocess
import pathlib
from paramiko import SSHClient

from tomo2bm import log


def check_remote_directory(remote_server, remote_dir):
    try:
        rcmd = 'ls ' + remote_dir
        # rcmd is the command used to check if the remote directory exists
        subprocess.check_call(['ssh', remote_server, rcmd], stderr=open(os.devnull, 'wb'), stdout=open(os.devnull, 'wb'))
        log.warning('      *** remote directory %s exists' % (remote_dir))
        return 0

    except subprocess.CalledProcessError as e: 
        # log.info('      *** return code = %d' % (e.returncode))
        log.warning('      *** remote directory %s does not exist' % (remote_dir))
        if e.returncode == 2:
            return e.returncode
        else:
            log.error('  *** Unknown error code returned: %d' % (e.returncode))
            return -1


def create_remote_directory(remote_server, remote_dir):
    cmd = 'mkdir -p ' + remote_dir
    try:
        # log.info('      *** sending command %s' % (cmd))
        log.info('      *** creating remote directory %s' % (remote_dir))
        subprocess.check_call(['ssh', remote_server, cmd])
        log.info('      *** creating remote directory %s: Done!' % (remote_dir))
        return 0

    except subprocess.CalledProcessError as e:
        log.error('  *** Error while creating remote directory. Error code: %d' % (e.returncode))
        return -1


def scp(global_PVs, params):

    log.info(' ')
    log.info('  *** Data transfer')

    remote_server = params.remote_analysis_dir.split(':')[0]
    remote_top_dir = params.remote_analysis_dir.split(':')[1]
    log.info('      *** remote server: %s' % remote_server)
    log.info('      *** remote top directory: %s' % remote_top_dir)

    fname_origin = global_PVs['HDF1_FullFileName_RBV'].get(as_string=True)
    p = pathlib.Path(fname_origin)
    fname_destination = params.remote_analysis_dir + p.parts[-3] + '/' + p.parts[-2] + '/'
    remote_dir = remote_top_dir + p.parts[-3] + '/' + p.parts[-2] + '/'

    log.info('      *** origin: %s' % fname_origin)
    log.info('      *** destination: %s' % fname_destination)
    # log.info('      *** remote directory: %s' % remote_dir)

    ret = check_remote_directory(remote_server, remote_dir)

    if ret == 0:
        os.system('scp -q ' + fname_origin + ' ' + fname_destination + '&')
        log.info('  *** Data transfer: Done!')
        return 0
    elif ret == 2:
        iret = create_remote_directory(remote_server, remote_dir)
        if iret == 0: 
            os.system('scp -q ' + fname_origin + ' ' + fname_destination + '&')
        log.info('  *** Data transfer: Done!')
        return 0
    else:
        log.error('  *** Quitting the copy operation')
        return -1


def mkdir(remote_server, remote_dir):

    log.info('Creating directory on server %s:%s' % (remote_server, remote_dir))
    ret = dm_lib.check_remote_directory(remote_server , remote_dir)
    if ret == 2:
        iret = dm_lib.create_remote_directory(remote_server, remote_dir)

