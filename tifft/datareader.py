"""Data reader module for fetching financial data and calculating indicators.

This module provides functionality to fetch remote financial data using
pandas_datareader and calculate technical indicators including MACD,
Bollinger Bands, and RSI.
"""

import logging
import os
from pathlib import Path
from pprint import pformat
from typing import Any

import pandas as pd
import pandas_datareader.data as pdd  # type: ignore[reportMissingTypeStubs]

from .bollingerbands import BollingerBandsCalculator
from .macd import MacdCalculator
from .rsi import RsiCalculator


def fetch_remote_data(  # noqa: PLR0913, PLR0917
    name: str | list[str],
    data_source: str = "fred",
    api_key: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    max_rows: str | int | None = None,
    *,
    drop_na: bool = False,
    output_csv_path: str | None = None,
    **kwargs: Any,  # noqa: ANN401
) -> None:
    """Fetch historical financial data from a remote data source.

    Args:
        name: Dataset name(s) to fetch. Can be a string or list of strings.
        data_source: The data source to use (e.g., 'fred', 'yahoo'). Defaults to 'fred'.
        api_key: API key for the data source if required.
        start_date: Start date for the data in format 'YYYY-MM-DD'.
        end_date: End date for the data in format 'YYYY-MM-DD'.
        max_rows: Maximum number of rows to display. None for all rows.
        drop_na: If True, remove rows with missing values.
        output_csv_path: Path to save the data as CSV file.
        **kwargs: Additional arguments passed to pandas_datareader.DataReader.
    """
    logger = logging.getLogger(__name__)
    df_hist = _load_data_with_pandas_datareader(
        name=(
            name if isinstance(name, str) or data_source in {"fred", "iex"} else name[0]
        ),
        data_source=data_source,
        start=start_date,
        end=end_date,
        api_key=api_key,
        **kwargs,
    ).pipe(lambda d: (d.dropna() if drop_na else d))
    logger.debug("df_hist:%s%s", os.linesep, df_hist)
    print(">>\tPrint results:\t" + (name if isinstance(name, str) else ", ".join(name)))  # noqa: T201
    pd.set_option("display.max_rows", (int(max_rows) if max_rows else None))
    print(df_hist)  # noqa: T201
    if output_csv_path:
        _write_df_to_csv(df=df_hist, csv_path=output_csv_path)


def _load_data_with_pandas_datareader(**kwargs: Any) -> pd.DataFrame:  # noqa: ANN401
    """Load data using pandas_datareader.DataReader.

    Args:
        **kwargs: Arguments passed to pandas_datareader.DataReader.

    Returns:
        DataFrame containing the fetched data.
    """
    logger = logging.getLogger(__name__)
    logger.info("Arguments for DataReader:%s%s", os.linesep, pformat(kwargs))
    name = kwargs["name"]
    print(  # noqa: T201
        ">>\tGet data from {}:\t".format(kwargs["data_source"])
        + (name if isinstance(name, str) else ", ".join(name))
    )
    return pdd.DataReader(**kwargs)


def _write_df_to_csv(df: pd.DataFrame, csv_path: str) -> None:
    """Write a DataFrame to a CSV file.

    Args:
        df: DataFrame to write.
        csv_path: Path where the CSV file will be saved.
    """
    output_csv = Path(csv_path).resolve()
    print(f">>\tWrite a CSV file:\t{output_csv}")  # noqa: T201
    df.to_csv(output_csv, mode="w", header=True, sep=",")


def calculate_indicator_for_remote_data(  # noqa: PLR0913, PLR0917
    indicator: str,
    name: str,
    data_source: str = "fred",
    api_key: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    max_rows: str | int | None = None,
    drop_na: bool = False,  # noqa: FBT001, FBT002
    output_csv_path: str | None = None,
    **kwargs: Any,  # noqa: ANN401
) -> None:
    """Calculate technical indicators for remotely fetched financial data.

    Args:
        indicator: Type of indicator to calculate ('macd', 'bb', or 'rsi').
        name: Dataset name to fetch.
        data_source: The data source to use. Defaults to 'fred'.
        api_key: API key for the data source if required.
        start_date: Start date for the data in format 'YYYY-MM-DD'.
        end_date: End date for the data in format 'YYYY-MM-DD'.
        max_rows: Maximum number of rows to display. None for all rows.
        drop_na: If True, remove rows with missing values.
        output_csv_path: Path to save the results as CSV file.
        **kwargs: Additional parameters specific to each indicator:
            - For MACD: fast_ema_span, slow_ema_span, macd_ema_span
            - For BB: window_size, sd_multiplier
            - For RSI: window_size, upper_line, lower_line

    Raises:
        ValueError: If an invalid indicator type is specified.
    """
    logger = logging.getLogger(__name__)
    df_hist = _load_data_with_pandas_datareader(
        name=name,
        data_source=data_source,
        start=start_date,
        end=end_date,
        api_key=api_key,
    ).pipe(lambda d: (d.dropna() if drop_na else d))
    logger.debug("df_hist:%s%s", os.linesep, df_hist)
    if indicator == "macd":
        print(f">>\tCalculate MACD:\t{name}")  # noqa: T201
        params = {
            k: int(kwargs[k])
            for k in ["fast_ema_span", "slow_ema_span", "macd_ema_span"]
        }
        calculator = MacdCalculator
    elif indicator == "bb":
        print(f">>\tCalculate Bollinger Bands:\t{name}")  # noqa: T201
        params = {k: int(kwargs[k]) for k in ["window_size", "sd_multiplier"]}
        calculator = BollingerBandsCalculator
    elif indicator == "rsi":
        print(f">>\tCalculate RSI:\t{name}")  # noqa: T201
        params = {
            k: int(kwargs[k]) for k in ["window_size", "upper_line", "lower_line"]
        }
        calculator = RsiCalculator
    else:
        msg = f"invalid indicator: {indicator}"
        raise ValueError(msg)
    _print_key_values(**params)
    df_indicator = (
        calculator(**params)
        .calculate(values=df_hist.iloc[:, 0])
        .pipe(lambda d: d.rename(columns={k: k.upper() for k in d.columns}))
    )
    logger.debug("df_indicator:%s%s", os.linesep, df_indicator)
    print(f">>\tPrint results:\t{name}")  # noqa: T201
    pd.set_option("display.max_rows", (int(max_rows) if max_rows else None))
    print(df_indicator)  # noqa: T201
    if output_csv_path:
        _write_df_to_csv(df=df_indicator, csv_path=output_csv_path)


def _print_key_values(**kwargs: Any) -> None:  # noqa: ANN401
    """Print key-value pairs in a formatted manner.

    Args:
        **kwargs: Key-value pairs to print.
    """
    for k, v in kwargs.items():
        print(f"{k.upper().replace('_', ' ')}:\t{v}")  # noqa: T201
