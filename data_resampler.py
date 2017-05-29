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
import glob
import os
import argparse
import logging
import pandas as pd

from shutil import copyfile

# --------------------------------------------- ------------------------------ #
# Main
# --------------------------------------------------------------------------- #
if __name__ == "__main__":

    # --------------------------------------------------------------------------- #
    # Initial configuration
    # --------------------------------------------------------------------------- #
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-i', help='input folder')
    arg_parser.add_argument('-o', help='output folder')
    arg_parser.add_argument('-r', help='resampling rate')
    arg_parser.add_argument('-l', help='log file')
    args = arg_parser.parse_args()

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
    # Preliminary definitions (neighbourhood, addhouse, etc.)
    # --------------------------------------------------------------------------- #
    logger.info('Starting program')
    ax = None
    legend_data = []

    index = pd.date_range('2015-01-01 00:00', periods=24 * 60 * 365, freq='T')

    for root, subfolders, files in os.walk(args.i):
        for subfolder in subfolders:
            logger.info('**********************************')
            logger.info('**********************************')
            logger.info('Resampling data in folder %s/%s' % (args.i, subfolder))
            ep_file_path = '%s/%s/Electricity_Profile.csv' % (args.i, subfolder)

            with open(ep_file_path, 'r') as f:
                first_line = f.readline()
                arr_line = first_line.split(';')
            f.close()
            cols = ['HH%02i' % i for i in range(0, len(arr_line))]

            for data_file in glob.glob('%s/%s/*.csv' % (args.i, subfolder)):
                logger.info('**********************************')
                arr_path_file = data_file.split('/')
                file_name = arr_path_file[len(arr_path_file) - 1]
                (desc_string, ext) = file_name.split('.')
                logger.info('Input raw file: %s' % file_name)

                # Resampling data
                logger.info('Resampling data')
                df = pd.read_csv(data_file, names=cols, sep=';')
                df = df.set_index(index)
                df.index.name = 't'
                df = df.resample(args.r).mean()

                # Write data on output files
                output_folder = '%s/%s' % (args.o, subfolder)
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                output_file = '%s/%s_%s.csv' % (output_folder, desc_string, args.r)
                logger.info('Write re-sampled data on file %s' % output_file)
                df.to_csv(output_file)
                del df

                # Copy info files in output folder
                copyfile('%s/%s/settings.json' % (args.i, subfolder), '%s/settings.json' % output_folder)
                copyfile('%s/%s/HH_settings.txt' % (args.i, subfolder), '%s/HH_settings.txt' % output_folder)

    logger.info('Ending program')

