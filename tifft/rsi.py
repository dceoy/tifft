#!/usr/bin/env python

import logging
import os
from pprint import pformat

import numpy as np
import pandas as pd


class RsiCalculator(object):
    def __init__(self, window_size=14, upper_line=70, lower_line=30, **kwargs):
        self.__logger = logging.getLogger(__name__)
        self.__upper_line = upper_line
        self.__lower_line = lower_line
        self.__rolling_kwargs = {'window': window_size, **kwargs}
        self.__logger.debug(f'vars(self):{os.linesep}' + pformat(vars(self)))

    def calculate(self, values):
        return (
            values.to_frame(name='value') if isinstance(values, pd.Series)
            else pd.DataFrame({'value': values})
        ).assign(
            ff_diff=lambda d: d['value'].fillna(method='ffill').diff()
        ).assign(
            upward=lambda d: d['ff_diff'].mask(d['ff_diff'] < 0, 0),
            downward=lambda d: d['ff_diff'].mask(d['ff_diff'] > 0, 0) * -1
        ).assign(
            rs=lambda d: (
                d['upward'].rolling(**self.__rolling_kwargs).mean()
                / d['downward'].rolling(**self.__rolling_kwargs).mean()
            )
        ).assign(
            rsi=lambda d: (100 - 100 / (1 + d['rs']))
        ).assign(
            signal=lambda d: np.where(
                d['rsi'] > self.__upper_line, 1,
                np.where(d['rsi'] < self.__lower_line, -1, 0)
            ).astype(int)
        ).drop(columns=['ff_diff', 'upward', 'downward'])
