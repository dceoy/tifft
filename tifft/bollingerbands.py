"""Bollinger Bands technical indicator calculator.

This module provides a calculator class for computing Bollinger Bands,
a volatility indicator that consists of a moving average with upper and
lower bands based on standard deviation.
"""

import logging
import os
from collections.abc import Sequence
from pprint import pformat
from typing import Any, cast

import numpy as np
import pandas as pd

# Tolerance for floating point comparison
FLOAT_TOLERANCE = 1e-10


class BollingerBandsCalculator:
    """Calculator for Bollinger Bands technical indicator.

    Bollinger Bands consist of a middle line (moving average) and two outer bands
    that are standard deviations away from the middle line. They are used to
    measure volatility and identify potential overbought/oversold conditions.

    Attributes:
        sd_multiplier (int): Standard deviation multiplier for the bands.
        rolling_kwargs (dict): Parameters for the rolling window calculation.
    """

    def __init__(
        self,
        window_size: int = 20,
        sd_multiplier: int = 2,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        """Initialize the Bollinger Bands calculator.

        Args:
            window_size: Size of the rolling window for calculations. Defaults to 20.
            sd_multiplier: Standard deviation multiplier for band width. Defaults to 2.
            **kwargs: Additional arguments passed to the rolling window function.
        """
        self.__logger = logging.getLogger(__name__)
        self.sd_multiplier = sd_multiplier
        self.rolling_kwargs = {"window": window_size, **kwargs}
        self.__logger.debug("vars(self):%s%s", os.linesep, pformat(vars(self)))

    def calculate(self, values: pd.Series | Sequence[int | float]) -> pd.DataFrame:
        """Calculate Bollinger Bands for the given values.

        Args:
            values: Price data as pandas Series or list.

        Returns:
            DataFrame with columns:
                - value: Original values
                - ma: Moving average (middle band)
                - sd: Standard deviation
                - lower_bb: Lower Bollinger Band
                - upper_bb: Upper Bollinger Band
                - signal: Trading signal based on position relative to bands
        """
        return (
            (
                values.to_frame(name="value")
                if isinstance(values, pd.Series)
                else pd.DataFrame({"value": values})
            )
            .assign(value_ff=lambda d: d["value"].ffill())
            .assign(
                ma=lambda d: d["value_ff"]
                .rolling(**cast("Any", self.rolling_kwargs))
                .mean(),
                sd=lambda d: d["value_ff"]
                .rolling(**cast("Any", self.rolling_kwargs))
                .std(),
            )
            .assign(
                lower_bb=lambda d: (d["ma"] - d["sd"] * self.sd_multiplier),
                upper_bb=lambda d: (d["ma"] + d["sd"] * self.sd_multiplier),
                residual=lambda d: (d["value_ff"] - d["ma"]) / d["sd"],
            )
            .assign(
                signal=lambda d: d["residual"]
                .apply(
                    lambda x: (
                        0
                        if pd.isna(x)
                        else int(np.floor(x) if x > 0 else np.ceil(x))
                        if abs(x - round(x)) > FLOAT_TOLERANCE
                        else round(x)
                    )
                )
                .astype(int)
            )
            .drop(columns=["value_ff", "residual"])
        )
