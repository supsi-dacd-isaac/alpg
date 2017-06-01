#!/usr/bin/python3

# --------------------------------------------------------------------------- #
# Importing section
# --------------------------------------------------------------------------- #

# Standard libraries
import argparse
import logging
import pandas as pd

# --------------------------------------------- ------------------------------ #
# Main
# --------------------------------------------------------------------------- #
if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-i', help='input file')
    arg_parser.add_argument('-o', help='output file')
    arg_parser.add_argument('-l', help='log file')
    args = arg_parser.parse_args()

    if not args.l:
        log_file = None
    else:
        log_file = args.l

    logger = logging.getLogger()
    logging.basicConfig(format='%(asctime)-15s::%(levelname)s::%(funcName)s::%(message)s', level=logging.INFO,
                        filename=log_file)

    logger.info('Starting program')

    # Do not consider the 29th of February (leap year used in Meteonorm format)
    indexes = pd.date_range('2015-01-01 00:01', periods=24 * 60 * 365, freq='T')
    logger.info('Reading data from %s' % args.i)
    df = pd.read_csv(args.i, header=2, sep='	')
    df = pd.concat([df[0:84960 - 1], df[84960 + 1440 - 1:len(df)]])

    df = df.set_index(indexes)
    df.index.name = 't'

    # From W/m² in J/cm²
    # W/m² (1m resolution) => 1/60 * Wh/m => 0.36 * J/cm²
    df_1h = pd.DataFrame({'H_Gh_J_on_cm2': df['G_Gh'].resample('1H').sum()})
    df_1h = df_1h * 0.36 / 60

    # Write on file
    df_1h.to_csv(args.o, columns=['H_Gh_J_on_cm2'], header=False, index=False)

    logger.info('Writing data from %s' % args.i)
    logger.info('Ending program')

