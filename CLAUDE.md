# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`tifft` is a Python package for calculating technical indicators for financial trading. It provides:
- Python calculator classes for MACD, Bollinger Bands, and RSI
- Command-line interface for fetching historical data and calculating indicators
- Integration with pandas-datareader for remote data sources (FRED, etc.)

## Commands

### Development
```bash
# Install the package in development mode
pip install -e .

# Run linting (as per test workflow)
flake8 .

# Test command-line interface
tifft --version
tifft --help
```

### Testing
```bash
# Run basic commands to test functionality
tifft history DJIA SP500 NASDAQ100
tifft macd SP500
tifft bb SP500
tifft rsi SP500
```

### Building and Publishing
```bash
# Build package (standard Python packaging)
python setup.py sdist bdist_wheel

# Docker build
docker build -t tifft .
```

## Architecture

### Core Structure
- `tifft/cli.py`: Command-line interface using docopt, entry point for the package
- `tifft/datareader.py`: Data fetching and indicator calculation orchestration
- `tifft/macd.py`, `tifft/bollingerbands.py`, `tifft/rsi.py`: Calculator classes for each indicator

### Key Design Patterns
- Each indicator is implemented as a Calculator class with a `calculate()` method
- CLI commands map to functions in `datareader.py` that handle data fetching and processing
- Uses pandas DataFrames for all data manipulation
- Remote data fetching via `pandas_datareader.data.DataReader`

### Dependencies
- `docopt`: CLI argument parsing
- `pandas`: Data manipulation
- `pandas-datareader`: Financial data fetching

### Entry Points
- Console script: `tifft` (defined in setup.py)
- Python imports: `from tifft.{indicator} import {Indicator}Calculator`