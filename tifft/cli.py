#!/usr/bin/env python
"""
Technical Indicators for Financial Trading

Usage:
    tifft -h|--help
    tifft --version
    tifft fred [--debug|--info] [--max-rows=<int>] [--start=<date>]
        [--end=<date>] [--csv=<path>] <symbol>...

Options:
    -h, --help          Print help and exit
    --version           Print version and exit
    --debug, --info     Execute a command with debug|info messages
    --csv=<path>        Write data with CSV into a file
    --start=<date>      Specify the start date
    --end=<date>        Specify the end date
    --max-rows=<int>    Specify the max rows to display [default: 60]

Commands:
    fred                Fetch data from FRED

Arguments:
    <symbol>            Data symbol
"""

import logging
import os

from docopt import docopt

from . import __version__
from .datareader import fetch_df_from_fred


def main():
    args = docopt(__doc__, version=__version__)
    _set_log_config(debug=args['--debug'], info=args['--info'])
    logger = logging.getLogger(__name__)
    logger.debug(f'args:{os.linesep}{args}')
    if args['fred']:
        fetch_df_from_fred(
            symbols=args['<symbol>'], output_csv_path=args['--csv'],
            max_rows=args['--max-rows']
        )


def _set_log_config(debug=None, info=None):
    if debug:
        lv = logging.DEBUG
    elif info:
        lv = logging.INFO
    else:
        lv = logging.WARNING
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S', level=lv
    )
