#!/usr/bin/env python

import logging
import os
from pathlib import Path

import pandas as pd
import pandas_datareader.data as pdd

from .macd import MacdCalculator


def fetch_fred_data(symbols, output_csv_path=None, start_date=None,
                    end_date=None, max_rows=None, **kwargs):
    logger = logging.getLogger(__name__)
    pd.set_option('display.max_rows', (int(max_rows) if max_rows else None))
    print('>>\tGet historical data from FRED:\t' + ', '.join(symbols))
    df_hist = _fetch_fred_df(
        symbols=symbols, start_date=start_date, end_date=end_date,
        max_rows=max_rows, **kwargs
    )
    logger.debug(f'df_hist:{os.linesep}{df_hist}')
    print(df_hist)
    if output_csv_path:
        _write_df_to_csv(df=df_hist, csv_path=output_csv_path)


def _fetch_fred_df(symbols, start_date=None, end_date=None, max_rows=None,
                   **kwargs):
    return pdd.DataReader(
        name=symbols, data_source='fred', start=start_date, end=end_date,
        **kwargs
    )


def _write_df_to_csv(df, csv_path):
    output_csv = Path(csv_path).resolve()
    print(f'>>\tWrite a CSV file:\t{output_csv}')
    df.to_csv(output_csv, mode='w', header=True, sep=',')


def calculate_macd_from_fred_data(symbol, output_csv_path=None,
                                  start_date=None, end_date=None,
                                  max_rows=None, fast_ema_span=12,
                                  slow_ema_span=26, macd_ema_span=9, **kwargs):
    logger = logging.getLogger(__name__)
    pd.set_option('display.max_rows', (int(max_rows) if max_rows else None))
    print(f'>>\tGet historical data from FRED:\t{symbol}')
    df_hist = _fetch_fred_df(
        symbols=symbol, start_date=start_date, end_date=end_date,
        max_rows=max_rows
    )
    logger.debug(f'df_hist:{os.linesep}{df_hist}')
    print(f'>>\tCalculate MACD:\t{symbol}')
    macdc = MacdCalculator(
        fast_ema_span=fast_ema_span, slow_ema_span=slow_ema_span,
        macd_ema_span=macd_ema_span, **kwargs
    )
    df_macd = macdc.calculate_oscillator(values=df_hist.iloc[:, 0]).rename(
        columns={
            'value': symbol, 'macd': 'MACD', 'macd_ema': 'MACD_EMA',
            'signal': 'SIGNAL'
        }
    )
    logger.debug(f'df_macd:{os.linesep}{df_macd}')
    print(df_macd)
    if output_csv_path:
        _write_df_to_csv(df=df_macd, csv_path=output_csv_path)
