import os
import argparse

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

    # # create the top-level parser
    parser = argparse.ArgumentParser()
    # parser.add_argument('--foo', action='store_true', help='help for foo arg.')
    subparsers = parser.add_subparsers(help='help for subcommand')

    # create the parser for the change_energy command
    parser_a = subparsers.add_parser('set', help='set energy')
    parser_a.add_argument('energy', type=float, help='energy in keV; default=24.9')

    # create the parser for the "change2pink" command
    parser_b = subparsers.add_parser('pink', help='change to pink')
    parser_b.add_argument('angle', type=float, help='M1 angle in mrad; , default=2.657')

    # create the parser for the "white" command
    parser_c = subparsers.add_parser('white', help='set to white beam')

    args = parser.parse_args()

    try:
        angle = args.angle
        print(angle)
    except:
        print('angle is not set')
        angle = -1
    try:
        energy = args.energy
        print(energy)
    except:
        print('energy is not set')
        energy = -1

    print('*****************************')
    print(parser_c)
    # energy_lib.change2white(global_PVs)
    # angle_calibrated = energy_lib.change2pink(global_PVs)
    # energy_calibrated = energy_lib.change_energy(global_PVs, 17)
 
    
if __name__ == '__main__':
    main()
