"""MACD (Moving Average Convergence Divergence) technical indicator calculator.

This module provides a calculator class for computing MACD, a momentum
indicator that shows the relationship between two moving averages of a
security's price.
"""

import logging
import os
from pprint import pformat
from typing import Any

import pandas as pd


class MacdCalculator:
    """Calculator for MACD (Moving Average Convergence Divergence) indicator.

    MACD is calculated by subtracting the slow exponential moving average (EMA)
    from the fast EMA. A signal line (EMA of MACD) is then calculated to
    generate trading signals.

    Attributes:
        fast_ema_span (int): Span for the fast exponential moving average.
        slow_ema_span (int): Span for the slow exponential moving average.
        macd_ema_span (int): Span for the MACD signal line EMA.
        ewm_kwargs (dict): Parameters for exponential weighted moving average.
    """

    def __init__(
        self,
        fast_ema_span: int = 12,
        slow_ema_span: int = 26,
        macd_ema_span: int = 9,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        """Initialize the MACD calculator.

        Args:
            fast_ema_span: Period for fast EMA calculation. Defaults to 12.
            slow_ema_span: Period for slow EMA calculation. Defaults to 26.
            macd_ema_span: Period for MACD signal line EMA. Defaults to 9.
            **kwargs: Additional arguments passed to the EWM function.

        Raises:
            ValueError: If fast_ema_span >= slow_ema_span.
        """
        if fast_ema_span >= slow_ema_span:
            msg = "fast_ema_span must be less than slow_ema_span"
            raise ValueError(msg)
        self.__logger = logging.getLogger(__name__)
        self.fast_ema_span = fast_ema_span
        self.slow_ema_span = slow_ema_span
        self.macd_ema_span = macd_ema_span
        self.ewm_kwargs = {"adjust": False, **kwargs}
        self.__logger.debug("vars(self):%s%s", os.linesep, pformat(vars(self)))

    def calculate(self, values: pd.Series | list) -> pd.DataFrame:
        """Calculate MACD indicator for the given values.

        Args:
            values: Price data as pandas Series or list.

        Returns:
            DataFrame with columns:
                - value: Original values
                - macd: MACD line (fast EMA - slow EMA)
                - macd_ema: Signal line (EMA of MACD)
                - signal: Trading signal based on MACD and signal line crossover
                    (2: strong bullish, 1: bullish, -1: bearish, -2: strong bearish)
        """
        return (
            (
                values.to_frame(name="value")
                if isinstance(values, pd.Series)
                else pd.DataFrame({"value": values})
            )
            .assign(value_ff=lambda d: d["value"].fillna(method='ffill'))
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
