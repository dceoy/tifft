"""RSI (Relative Strength Index) technical indicator calculator.

This module provides a calculator class for computing RSI, a momentum
oscillator that measures the speed and change of price movements.
RSI oscillates between 0 and 100 and is used to identify overbought
and oversold conditions.
"""

import logging
import os
from collections.abc import Sequence
from pprint import pformat
from typing import Any, cast

import numpy as np
import pandas as pd


class RsiCalculator:
    """Calculator for RSI (Relative Strength Index) indicator.

    RSI is calculated based on the ratio of upward price changes to downward
    price changes over a specified time period. Values above 70 typically
    indicate overbought conditions, while values below 30 indicate oversold
    conditions.

    Attributes:
        upper_line (int): RSI threshold for overbought condition.
        lower_line (int): RSI threshold for oversold condition.
        rolling_kwargs (dict): Parameters for the rolling window calculation.
    """

    def __init__(
        self,
        window_size: int = 14,
        upper_line: int = 70,
        lower_line: int = 30,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        """Initialize the RSI calculator.

        Args:
            window_size: Size of the rolling window for RSI calculation. Defaults to 14.
            upper_line: RSI threshold for overbought signal. Defaults to 70.
            lower_line: RSI threshold for oversold signal. Defaults to 30.
            **kwargs: Additional arguments passed to the rolling window function.
        """
        self.__logger = logging.getLogger(__name__)
        self.upper_line = upper_line
        self.lower_line = lower_line
        self.rolling_kwargs = {"window": window_size, **kwargs}
        self.__logger.debug("vars(self):%s%s", os.linesep, pformat(vars(self)))

    def calculate(self, values: pd.Series | Sequence[int | float]) -> pd.DataFrame:
        """Calculate RSI indicator for the given values.

        Args:
            values: Price data as pandas Series or list.

        Returns:
            DataFrame with columns:
                - value: Original values
                - rs: Relative Strength ratio (average gain / average loss)
                - rsi: RSI values (0-100)
                - signal: Trading signal (1: overbought, -1: oversold, 0: neutral)
        """
        return (
            (
                values.to_frame(name="value")
                if isinstance(values, pd.Series)
                else pd.DataFrame({"value": values})
            )
            .assign(ff_diff=lambda d: d["value"].fillna(method="ffill").diff())
            .assign(
                upward=lambda d: d["ff_diff"].mask(d["ff_diff"] < 0, 0),
                downward=lambda d: d["ff_diff"].mask(d["ff_diff"] > 0, 0) * -1,
            )
            .assign(
                rs=lambda d: (
                    d["upward"].rolling(**cast("Any", self.rolling_kwargs)).mean()
                    / d["downward"].rolling(**cast("Any", self.rolling_kwargs)).mean()
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
