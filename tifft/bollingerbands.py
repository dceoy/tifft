#!/usr/bin/env python

import logging
import os
from pprint import pformat
from typing import Any, Union

import numpy as np
import pandas as pd


class BollingerBandsCalculator(object):
    def __init__(
        self, window_size: int = 20, sd_multiplier: int = 2, **kwargs: Any
    ) -> None:
        self.__logger = logging.getLogger(__name__)
        self.sd_multiplier = sd_multiplier
        self.rolling_kwargs = {"window": window_size, **kwargs}
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
                ma=lambda d: d["value_ff"].rolling(**self.rolling_kwargs).mean(),
                sd=lambda d: d["value_ff"].rolling(**self.rolling_kwargs).std(),
            )
            .assign(
                lower_bb=lambda d: (d["ma"] - d["sd"] * self.sd_multiplier),
                upper_bb=lambda d: (d["ma"] + d["sd"] * self.sd_multiplier),
                residual=lambda d: ((d["value_ff"] - d["ma"]) / d["sd"]).fillna(0),
            )
            .assign(
                signal=lambda d: np.where(
                    d["residual"] > 0, np.floor(d["residual"]), np.ceil(d["residual"])
                ).astype(int)
            )
            .drop(columns=["value_ff", "residual"])
        )
