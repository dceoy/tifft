#!/usr/bin/env python

import logging
import os
from pprint import pformat

import pandas as pd


class MacdCalculator(object):
    def __init__(self, fast_ema_span=12, slow_ema_span=26, signal_ema_span=9,
                 **kwargs):
        assert fast_ema_span < slow_ema_span, 'invalid spans'
        self.__logger = logging.getLogger(__name__)
        self.__fast_ema_span = fast_ema_span
        self.__slow_ema_span = slow_ema_span
        self.__signal_ema_span = signal_ema_span
        self.__ewm_kwargs = {'adjust': False, **kwargs}
        self.__logger.debug(f'vars(self):{os.linesep}' + pformat(vars(self)))

    def calculate_oscillator(self, values):
        return (
            values.to_frame(name='value') if isinstance(values, pd.Series)
            else pd.DataFrame({'value': values})
        ).assign(
            fast_ema=lambda d: d['value'].ewm(
                span=self.__fast_ema_span, **self.__ewm_kwargs
            ).mean(),
            slow_ema=lambda d: d['value'].ewm(
                span=self.__slow_ema_span, **self.__ewm_kwargs
            ).mean()
        ).assign(
            signal_ema=lambda d: (d['fast_ema'] - d['slow_ema']).ewm(
                span=self.__slow_ema_span, **self.__ewm_kwargs
            ).mean()
        )
