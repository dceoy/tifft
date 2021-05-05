#!/usr/bin/env python

import logging
import os
from pprint import pformat

import pandas as pd


class MacdCalculator(object):
    def __init__(self, fast_ema_span=12, slow_ema_span=26, macd_ema_span=9,
                 **kwargs):
        assert fast_ema_span < slow_ema_span, 'invalid spans'
        self.__logger = logging.getLogger(__name__)
        self.__fast_ema_span = fast_ema_span
        self.__slow_ema_span = slow_ema_span
        self.__macd_ema_span = macd_ema_span
        self.__ewm_kwargs = {'adjust': False, **kwargs}
        self.__logger.debug(f'vars(self):{os.linesep}' + pformat(vars(self)))

    def calculate(self, values):
        return (
            values.to_frame(name='value') if isinstance(values, pd.Series)
            else pd.DataFrame({'value': values})
        ).assign(
            value_ffill=lambda d: d['value'].fillna(method='ffill')
        ).assign(
            macd=lambda d: (
                d['value_ffill'].ewm(
                    span=self.__fast_ema_span, **self.__ewm_kwargs
                ).mean()
                - d['value_ffill'].ewm(
                    span=self.__slow_ema_span, **self.__ewm_kwargs
                ).mean()
            )
        ).assign(
            macd_ema=lambda d: d['macd'].ewm(
                span=self.__macd_ema_span, **self.__ewm_kwargs
            ).mean()
        ).assign(
            macd_ema_diff=lambda d: (d['macd'] - d['macd_ema'])
        ).assign(
            signal=lambda d: d['macd_ema_diff'].mask(
                (d['macd_ema_diff'] > 0) & (d['macd'] > 0), 2
            ).mask(
                d['macd_ema_diff'] > 0, 1
            ).mask(
                (d['macd_ema_diff'] < 0) & (d['macd'] < 0), -2
            ).mask(
                d['macd_ema_diff'] < 0, -1
            ).astype(int)
        ).drop(columns=['value_ffill', 'macd_ema_diff'])
