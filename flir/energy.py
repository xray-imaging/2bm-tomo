import time
import epics
import numpy as np
import os
import Tkinter
import tkMessageBox as mbox

import libs.aps2bm_lib as aps2bm_lib
import libs.log_lib as log_lib
import libs.energy_lib as energy_lib


    
def main():
    # create logger
    # # python 3.5+ 
    # home = str(pathlib.Path.home())
    home = os.path.expanduser("~")
    logs_home = home + '/logs/'

    # make sure logs directory exists
    if not os.path.exists(logs_home):
        os.makedirs(logs_home)

    lfname = logs_home + 'energy.log'
    log_lib.setup_logger(lfname)

    global_PVs = energy_lib.init_energy_change_PVs()

    # energy_lib.change2white(global_PVs)
    # angle_calibrated = energy_lib.change2pink(global_PVs)
    energy_calibrated = energy_lib.change_energy(global_PVs, 17)
 
    
if __name__ == '__main__':
    main()
