#!/usr/bin/env python
"""
Technical Indicators for Financial Trading

Usage:
    tifft -h|--help
    tifft --version
    tifft history [--debug|--info] [--max-rows=<int>] [--start=<date>]
        [--end=<date>] [--csv=<path>] <symbol>...
    tifft macd [--debug|--info] [--max-rows=<int>] [--start=<date>]
        [--end=<date>] [--fast-ema-span=<int>] [--slow-ema-span=<int>]
        [--macd-ema-span=<int>] [--csv=<path>] <symbol>

Options:
    -h, --help              Print help and exit
    --version               Print version and exit
    --debug, --info         Execute a command with debug|info messages
    --max-rows=<int>        Specify the max rows to display [default: 60]
    --start=<date>          Specify the start date (e.g., 2021-01-01)
    --end=<date>            Specify the end date
    --csv=<path>            Write data with CSV into a file
    --fast-ema-span=<int>   Specify the fast EMA span [default: 12]
    --slow-ema-span=<int>   Specify the slow EMA span [default: 26]
    --macd-ema-span=<int>   Specify the MACD EMA span [default: 9]

Commands:
    history                 Fetch historical data from FRED
    macd                    Fetch historical data from FRED and calculate MACD

Arguments:
    <symbol>                Data symbol
"""

import logging
import os

from docopt import docopt

from . import __version__
from .datareader import calculate_macd_from_fred_data, fetch_fred_data


def main():
    args = docopt(__doc__, version=__version__)
    _set_log_config(debug=args['--debug'], info=args['--info'])
    logger = logging.getLogger(__name__)
    logger.debug(f'args:{os.linesep}{args}')
    if args['history']:
        fetch_fred_data(
            symbols=args['<symbol>'], output_csv_path=args['--csv'],
            start_date=args['--start'], end_date=args['--end'],
            max_rows=args['--max-rows']
        )
    elif args['macd']:
        calculate_macd_from_fred_data(
            symbol=args['<symbol>'][0], output_csv_path=args['--csv'],
            start_date=args['--start'], end_date=args['--end'],
            max_rows=args['--max-rows'],
            fast_ema_span=int(args['--fast-ema-span']),
            slow_ema_span=int(args['--slow-ema-span']),
            macd_ema_span=int(args['--macd-ema-span'])
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
