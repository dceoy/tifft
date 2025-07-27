#!/usr/bin/env python
"""Command-line interface for Technical Indicators for Financial Trading.

This module provides the command-line interface for the tifft package,
enabling users to fetch historical financial data and calculate technical
indicators such as MACD, Bollinger Bands, and RSI.

Usage:
    tifft -h|--help
    tifft --version
    tifft history [--debug|--info] [--data-source=<name>] [--api-key=<token>]
        [--start=<date>] [--end=<date>] [--max-rows=<int>] [--drop-na]
        [--output-csv=<path>] <name>...
    tifft macd [--debug|--info] [--data-source=<name>] [--api-key=<token>]
        [--start=<date>] [--end=<date>] [--max-rows=<int>] [--drop-na]
        [--fast-ema-span=<int>] [--slow-ema-span=<int>] [--macd-ema-span=<int>]
        [--output-csv=<path>] <name>
    tifft bb [--debug|--info] [--data-source=<name>] [--api-key=<token>]
        [--start=<date>] [--end=<date>] [--max-rows=<int>] [--drop-na]
        [--bb-window=<int>] [--sd-multiplier=<int>] [--output-csv=<path>]
        <name>
    tifft rsi [--debug|--info] [--data-source=<name>] [--api-key=<token>]
        [--start=<date>] [--end=<date>] [--max-rows=<int>] [--drop-na]
        [--rsi-window=<int>] [--upper-rsi=<int>] [--lower-rsi=<int>]
        [--output-csv=<path>] <name>

Options:
    -h, --help              Print help and exit
    --version               Print version and exit
    --debug, --info         Execute a command with debug|info messages
    --data-source=<name>    Specify the data source [default: fred]
    --api-key=<token>       Specify an API key for a data source
    --start=<date>          Specify the start date (e.g., 2021-01-01)
    --end=<date>            Specify the end date
    --max-rows=<int>        Specify the max rows to display [default: 60]
    --drop-na               Delete rows with missing values from the input data
    --output-csv=<path>     Write data with CSV into a file
    --fast-ema-span=<int>   Specify the fast EMA span [default: 12]
    --slow-ema-span=<int>   Specify the slow EMA span [default: 26]
    --macd-ema-span=<int>   Specify the MACD EMA span [default: 9]
    --bb-window=<int>       Specify the window size of BB [default: 20]
    --sd-multiplier=<int>   Specify the SD multiplier [default: 2]
    --rsi-window=<int>      Specify the window size of RSI [default: 14]
    --upper-rsi=<int>       Specify the upper line of RSI [default: 70]
    --lower-rsi=<int>       Specify the lower line of RSI [default: 30]

Commands:
    history                 Fetch historical data from a data source
                            (Using pandas_datareader.data.DataReader)
    macd                    Calculate MACD
    bb                      Calculate Bollinger Bands (BB)
    rsi                     Calculate RSI

Arguments:
    <name>                  Dataset name
"""

import logging
import os
from typing import Optional

from docopt import docopt

from . import __version__
from .datareader import calculate_indicator_for_remote_data, fetch_remote_data


def main() -> None:
    """Execute the main command-line interface.

    Parses command-line arguments and executes the appropriate command
    for fetching historical data or calculating technical indicators.
    """
    args = docopt(__doc__, version=__version__)
    _set_log_config(debug=args["--debug"], info=args["--info"])
    logger = logging.getLogger(__name__)
    logger.debug(f"args:{os.linesep}{args}")
    if args["history"]:
        fetch_remote_data(
            name=args["<name>"],
            data_source=args["--data-source"],
            api_key=args["--api-key"],
            start_date=args["--start"],
            end_date=args["--end"],
            max_rows=args["--max-rows"],
            drop_na=args["--drop-na"],
            output_csv_path=args["--output-csv"],
        )
    elif args["macd"]:
        calculate_indicator_for_remote_data(
            name=args["<name>"][0],
            data_source=args["--data-source"],
            api_key=args["--api-key"],
            start_date=args["--start"],
            end_date=args["--end"],
            max_rows=args["--max-rows"],
            drop_na=args["--drop-na"],
            output_csv_path=args["--output-csv"],
            indicator="macd",
            fast_ema_span=args["--fast-ema-span"],
            slow_ema_span=args["--slow-ema-span"],
            macd_ema_span=args["--macd-ema-span"],
        )
    elif args["bb"]:
        calculate_indicator_for_remote_data(
            name=args["<name>"][0],
            data_source=args["--data-source"],
            api_key=args["--api-key"],
            start_date=args["--start"],
            end_date=args["--end"],
            max_rows=args["--max-rows"],
            drop_na=args["--drop-na"],
            output_csv_path=args["--output-csv"],
            indicator="bb",
            window_size=args["--bb-window"],
            sd_multiplier=args["--sd-multiplier"],
        )
    elif args["rsi"]:
        calculate_indicator_for_remote_data(
            name=args["<name>"][0],
            data_source=args["--data-source"],
            api_key=args["--api-key"],
            start_date=args["--start"],
            end_date=args["--end"],
            max_rows=args["--max-rows"],
            drop_na=args["--drop-na"],
            output_csv_path=args["--output-csv"],
            indicator="rsi",
            window_size=args["--rsi-window"],
            upper_line=args["--upper-rsi"],
            lower_line=args["--lower-rsi"],
        )


def _set_log_config(debug: Optional[bool] = None, info: Optional[bool] = None) -> None:
    """Configure logging based on command-line arguments.

    Args:
        debug: If True, set logging level to DEBUG.
        info: If True, set logging level to INFO.
            If neither debug nor info is True, set to WARNING.
    """
    if debug:
        lv = logging.DEBUG
    elif info:
        lv = logging.INFO
    else:
        lv = logging.WARNING
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=lv,
    )
