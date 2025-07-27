#!/usr/bin/env python

import logging
import os
from pprint import pformat
from typing import Any, Union

import pandas as pd


class MacdCalculator(object):
    def __init__(
        self,
        fast_ema_span: int = 12,
        slow_ema_span: int = 26,
        macd_ema_span: int = 9,
        **kwargs: Any,
    ) -> None:
        assert fast_ema_span < slow_ema_span, "invalid spans"
        self.__logger = logging.getLogger(__name__)
        self.fast_ema_span = fast_ema_span
        self.slow_ema_span = slow_ema_span
        self.macd_ema_span = macd_ema_span
        self.ewm_kwargs = {"adjust": False, **kwargs}
        self.__logger.debug(f"vars(self):{os.linesep}" + pformat(vars(self)))

    def calculate(self, values: Union[pd.Series, list]) -> pd.DataFrame:
        return (
            (
                values.to_frame(name="value")
                if isinstance(values, pd.Series)
                else pd.DataFrame({"value": values})
            )
            .assign(value_ff=lambda d: d["value"].ffill())
            .assign(
                macd=lambda d: (
                    d["value_ff"].ewm(span=self.fast_ema_span, **self.ewm_kwargs).mean()
                    - d["value_ff"]
                    .ewm(span=self.slow_ema_span, **self.ewm_kwargs)
                    .mean()
                )
            )
            .assign(
                macd_ema=lambda d: d["macd"]
                .ewm(span=self.macd_ema_span, **self.ewm_kwargs)
                .mean()
            )
            .assign(macd_ema_delta=lambda d: (d["macd"] - d["macd_ema"]))
            .assign(
                signal=lambda d: d["macd_ema_delta"]
                .mask((d["macd_ema_delta"] > 0) & (d["macd"] > 0), 2)
                .mask(d["macd_ema_delta"] > 0, 1)
                .mask((d["macd_ema_delta"] < 0) & (d["macd"] < 0), -2)
                .mask(d["macd_ema_delta"] < 0, -1)
                .astype(int)
            )
            .drop(columns=["value_ff", "macd_ema_delta"])
        )
