#!/usr/bin/python3

	#Artifical load profile generator v1.0, generation of artificial load profiles to benchmark demand side management approaches
    #Copyright (C) 2016 Gerwin Hoogsteen

    #This program is free software: you can redistribute it and/or modify
    #it under the terms of the GNU General Public License as published by
	#the Free Software Foundation, either version 3 of the License, or
    #(at your option) any later version.

    #This program is distributed in the hope that it will be useful,
    #but WITHOUT ANY WARRANTY; without even the implied warranty of
    #MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    #GNU General Public License for more details.

    #You should have received a copy of the GNU General Public License
    #along with this program.  If not, see <http://www.gnu.org/licenses/>.

# --------------------------------------------------------------------------- #
# Importing section
# --------------------------------------------------------------------------- #

# Standard libraries
import os
import sys
import time
import argparse
import json
import logging
from shutil import copyfile

# Profilegenerator libraries
import profilegentools

# --------------------------------------------- ------------------------------ #
# Main
# --------------------------------------------------------------------------- #
if __name__ == "__main__":

    print("Profilegenerator 1.0\n")
    print("Copyright (C) 2016 Gerwin Hoogsteen")
    print("This program comes with ABSOLUTELY NO WARRANTY.")
    print("This is free software, and you are welcome to redistribute it under certain conditions.")
    print("See the accompanying license for more information.\n")

    # --------------------------------------------------------------------------- #
    # Initial configuration
    # --------------------------------------------------------------------------- #
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-c', help='configuration file')
    arg_parser.add_argument('-l', help='log file')

    args = arg_parser.parse_args()
    file_config = json.loads(open(args.c).read())
    copyfile(args.c, 'conf/tmp.json')
    import config
    arr_path_file = args.c.split('/')
    (name_file, ext) = arr_path_file[len(arr_path_file)-1].split('.')
    config.folder = '%s/%s' % (config.folder, name_file)

    # --------------------------------------------------------------------------- #
    # Logging object
    # --------------------------------------------------------------------------- #
    if not args.l:
        log_file = None
    else:
        log_file = args.l

    logger = logging.getLogger()
    logging.basicConfig(format='%(asctime)-15s::%(levelname)s::%(funcName)s::%(message)s', level=logging.INFO,
                        filename=log_file)

    # --------------------------------------------------------------------------- #
    # Preliminary definitions (neighbourhood, addhous, etc.)
    # --------------------------------------------------------------------------- #
    logger.info('Starting program')

    import neighbourhood
    neighbourhood.neighbourhood(logger=logger)

    configFile = []

    # more preamble
    if not os.path.exists(config.folder):
        os.makedirs(config.folder)

    # Addhouse function
    configFile.append('control = False')
    configFile.append('def addHouse(node, coordx, coordy, phase, houseNum):')

    if not os.path.exists(config.folder):
        os.makedirs(config.folder)
    copyfile(args.c, '%s/settings.json' % config.folder)

    # --------------------------------------------------------------------------- #
    # Profile creation
    # --------------------------------------------------------------------------- #
    logger.info('Writing output file in %s' % config.folder)
    logger.info('The current config will create and simulate %i households' % len(config.householdList))

    logger.info('HOUSEHOLD TYPES:')
    logger.info('num_single_worker = %i' % config.num_singles_worker)
    logger.info('num_single_retired = %i' % config.num_singles_retired)
    logger.info('num_duals_worker = %i' % config.num_duals_worker)
    logger.info('num_duals_retired = %i' % config.num_duals_retired)
    logger.info('num_families_single_worker = %i' % config.num_families_single_worker)
    logger.info('num_families_dual_workers = %i' % config.num_families_dual_workers)

    hnum = 0
    fw = open('%s/HH_settings.txt' % config.folder, 'w')
    fw.write('HH,Type\n')

    for household in config.householdList:
        # Apparently, the seed is brokin in the while loop...:
        # random.seed(config.seed+hnum)

        # --------------------------------------------------------------------------- #
        # Simulation
        # --------------------------------------------------------------------------- #
        logger.info('Started simulation for household %i of %i, type=\'%s\'' % (hnum+1, len(config.householdList),
                                                                                household.type))
        fw.write('HH%02i,%s\n' % (hnum+1, household.type))

        t = time.time()
        household.simulate()
        elapsed_time = time.time() - t
        logger.info('Ended simulation for household %i of %i: elapsed time=%.2f seconds' % (hnum+1,
                                                                                            len(config.householdList),
                                                                                            elapsed_time))
        # Warning: On my PC the random number is still the same at this point,
        # but after calling scaleProfile() it isn't!!!

        logger.info('Started scaling for household %i of %i, type=\'%s\'' % (hnum+1, len(config.householdList),
                                                                             household.type))
        # --------------------------------------------------------------------------- #
        # Profiles scaling
        # --------------------------------------------------------------------------- #
        t = time.time()
        household.scaleProfile()
        household.reactivePowerProfile()
        elapsed_time = time.time() - t
        logger.info('Ended scaling for household %i of %i: elapsed time=%.2f seconds' % (hnum+1,
                                                                                         len(config.householdList),
                                                                                         elapsed_time))
        # --------------------------------------------------------------------------- #
        # Dataset resampling (STIIL TO TEST!
        # --------------------------------------------------------------------------- #
        if config.intervalLength != 1:
            logger.info('Started resampling for household %i of %i, type=\'%s\'' % (hnum + 1, len(config.householdList),
                                                                                    household.type))
            t = time.time()
            household.Consumption['Total'] = profilegentools.resample(household.Consumption['Total'],
                                                                      config.intervalLength)
            household.ReactiveConsumption['Total'] = profilegentools.resample(household.ReactiveConsumption['Total'],
                                                                              config.intervalLength)
            elapsed_time = time.time() - t
            logger.info('Ended resampling for household %i of %i: elapsed time=%.2f seconds' % (hnum+1,
                                                                                                len(config.householdList),
                                                                                                elapsed_time))
        # --------------------------------------------------------------------------- #
        # Output files writing
        # --------------------------------------------------------------------------- #
        logger.info('Started writing for household %i of %i, type=\'%s\'' % (hnum+1, len(config.householdList),
                                                                             household.type))
        t = time.time()
        config.writer.writeHousehold(household, hnum)
        config.writer.writeNeighbourhood(hnum)
        elapsed_time = time.time() - t
        logger.info('Ended writing for household %i of %i: elapsed time=%.2f seconds' % (hnum+1,
                                                                                         len(config.householdList),
                                                                                         elapsed_time))
        hnum += 1
    fw.close()
    logger.info('Ending program')
