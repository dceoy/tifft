"""Technical Indicators for Financial Trading (tifft).

This package provides tools for calculating technical indicators for financial trading.
It includes calculators for MACD, Bollinger Bands, and RSI indicators, along with
a command-line interface for fetching historical data and calculating indicators.

Modules:
    cli: Command-line interface for the package
    datareader: Data fetching and indicator calculation orchestration
    macd: MACD (Moving Average Convergence Divergence) calculator
    bollingerbands: Bollinger Bands calculator
    rsi: RSI (Relative Strength Index) calculator
"""

from importlib.metadata import version

__version__ = version(__package__) if __package__ else None
