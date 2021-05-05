#!/usr/bin/env python

import logging
import os
from pprint import pformat

import numpy as np
import pandas as pd


class BollingerBandsCalculator(object):
    def __init__(self, window_size=20, sd_multiplier=2, **kwargs):
        self.__logger = logging.getLogger(__name__)
        self.__window_size = window_size
        self.__sd_multiplier = sd_multiplier
        self.__rolling_kwargs = kwargs
        self.__logger.debug(f'vars(self):{os.linesep}' + pformat(vars(self)))

    def calculate(self, values):
        return (
            values.to_frame(name='value') if isinstance(values, pd.Series)
            else pd.DataFrame({'value': values})
        ).assign(
            value_ffill=lambda d: d['value'].fillna(method='ffill')
        ).assign(
            ma=lambda d: d['value_ffill'].rolling(
                window=self.__window_size, **self.__rolling_kwargs
            ).mean(),
            sd=lambda d: d['value_ffill'].rolling(
                window=self.__window_size, **self.__rolling_kwargs
            ).std()
        ).assign(
            lower_bb=lambda d: (d['ma'] - d['sd'] * self.__sd_multiplier),
            upper_bb=lambda d: (d['ma'] + d['sd'] * self.__sd_multiplier),
            residual=lambda d: ((d['value'] - d['ma']) / d['sd']).fillna(0)
        ).assign(
            signal=lambda d: np.where(
                d['residual'] > 0, np.floor(d['residual']),
                np.ceil(d['residual'])
            ).astype(int)
        ).drop(columns=['value_ffill', 'residual'])
