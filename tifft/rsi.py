#!/usr/bin/env python

import logging
import os
from pprint import pformat
from typing import Any, Union

import numpy as np
import pandas as pd


class RsiCalculator(object):
    def __init__(
        self,
        window_size: int = 14,
        upper_line: int = 70,
        lower_line: int = 30,
        **kwargs: Any,
    ) -> None:
        self.__logger = logging.getLogger(__name__)
        self.upper_line = upper_line
        self.lower_line = lower_line
        self.rolling_kwargs = {"window": window_size, **kwargs}
        self.__logger.debug(f"vars(self):{os.linesep}" + pformat(vars(self)))

    def calculate(self, values: Union[pd.Series, list]) -> pd.DataFrame:
        return (
            (
                values.to_frame(name="value")
                if isinstance(values, pd.Series)
                else pd.DataFrame({"value": values})
            )
            .assign(ff_diff=lambda d: d["value"].ffill().diff())
            .assign(
                upward=lambda d: d["ff_diff"].mask(d["ff_diff"] < 0, 0),
                downward=lambda d: d["ff_diff"].mask(d["ff_diff"] > 0, 0) * -1,
            )
            .assign(
                rs=lambda d: (
                    d["upward"].rolling(**self.rolling_kwargs).mean()
                    / d["downward"].rolling(**self.rolling_kwargs).mean()
                )
            )
            .assign(rsi=lambda d: (100 - 100 / (1 + d["rs"])))
            .assign(
                signal=lambda d: np.where(
                    d["rsi"] > self.upper_line,
                    1,
                    np.where(d["rsi"] < self.lower_line, -1, 0),
                ).astype(int)
            )
            .drop(columns=["ff_diff", "upward", "downward"])
        )
