#!/usr/bin/env python

import logging
import os
from pathlib import Path

import pandas as pd
import pandas_datareader.data as pdd

from .bollingerbands import BollingerBandsCalculator
from .macd import MacdCalculator


def fetch_fred_data(symbols, output_csv_path=None, start_date=None,
                    end_date=None, max_rows=None, **kwargs):
    logger = logging.getLogger(__name__)
    print('>>\tGet historical data from FRED:\t' + ', '.join(symbols))
    df_hist = _fetch_fred_df(
        symbols=symbols, start_date=start_date, end_date=end_date, **kwargs
    )
    logger.debug(f'df_hist:{os.linesep}{df_hist}')
    print('>>\tPrint results:\t' + ', '.join(symbols))
    pd.set_option('display.max_rows', (int(max_rows) if max_rows else None))
    print(df_hist)
    if output_csv_path:
        _write_df_to_csv(df=df_hist, csv_path=output_csv_path)


def _fetch_fred_df(symbols, start_date=None, end_date=None, **kwargs):
    return pdd.DataReader(
        name=symbols, data_source='fred', start=start_date, end=end_date,
        **kwargs
    )


def _write_df_to_csv(df, csv_path):
    output_csv = Path(csv_path).resolve()
    print(f'>>\tWrite a CSV file:\t{output_csv}')
    df.to_csv(output_csv, mode='w', header=True, sep=',')


def calculate_oscillator_for_fred_data(oscillator, symbol,
                                       output_csv_path=None, start_date=None,
                                       end_date=None, max_rows=None, **kwargs):
    logger = logging.getLogger(__name__)
    print(f'>>\tGet historical data from FRED:\t{symbol}')
    df_hist = _fetch_fred_df(
        symbols=symbol, start_date=start_date, end_date=end_date
    )
    logger.debug(f'df_hist:{os.linesep}{df_hist}')
    if oscillator == 'macd':
        print(f'>>\tCalculate MACD:\t{symbol}')
        params = {
            k: int(kwargs[k])
            for k in ['fast_ema_span', 'slow_ema_span', 'macd_ema_span']
        }
        calculator = MacdCalculator
    elif oscillator == 'bb':
        print(f'>>\tCalculate Bollinger Bands:\t{symbol}')
        params = {k: int(kwargs[k]) for k in ['window_size', 'sd_multiplier']}
        calculator = BollingerBandsCalculator
    else:
        raise ValueError(f'invalid oscillator: {oscillator}')
    _print_key_values(**params)
    df_oscillator = calculator(**params).calculate(
        values=df_hist.iloc[:, 0]
    ).pipe(lambda d: d.rename(columns={k: k.upper() for k in d.columns}))
    logger.debug(f'df_oscillator:{os.linesep}{df_oscillator}')
    print(f'>>\tPrint results:\t{symbol}')
    pd.set_option('display.max_rows', (int(max_rows) if max_rows else None))
    print(df_oscillator)
    if output_csv_path:
        _write_df_to_csv(df=df_oscillator, csv_path=output_csv_path)


def _print_key_values(**kwargs):
    for k, v in kwargs.items():
        print('{0}:\t{1}'.format(k.upper().replace('_', ' '), v))
