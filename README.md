tifft
=====

Technical Indicators for Financial Trading

[![Test](https://github.com/dceoy/tifft/actions/workflows/test.yml/badge.svg)](https://github.com/dceoy/tifft/actions/workflows/test.yml)
[![Upload Python Package](https://github.com/dceoy/tifft/actions/workflows/python-publish.yml/badge.svg)](https://github.com/dceoy/tifft/actions/workflows/python-publish.yml)

Installation
------------

```sh
$ pip install -U https://github.com/dceoy/tifft/archive/main.tar.gz
```

Docker image
------------

The image is available at [Docker Hub](https://hub.docker.com/r/dceoy/tifft/).

```sh
$ docker pull dceoy/tifft
```

Usage
-----

#### Calculator Classes for Python

```python
import numpy as np
from tifft.bollingerbands import BollingerBandsCalculator
from tifft.macd import MacdCalculator
from tifft.rsi import RsiCalculator

prices = np.random.randn(100) * 100

# MACD
macdc = MacdCalculator(fast_ema_span=12, slow_ema_span=26, macd_ema_span=9)
df_macd = macdc.calculate(values=prices)
print(df_macd)

# Bollinger Bands
bbc = BollingerBandsCalculator(window_size=20, sd_multiplier=2)
df_bb = bbc.calculate(values=prices)
print(df_bb)

# RSI
rsic = RsiCalculator(window_size=14, upper_line=70, lower_line=30)
df_rsi = rsic.calculate(values=prices)
print(df_rsi)
```

#### Command-line Tools

Fetch the historical data of DJIA, SP500, and NASDAQ100 from FRED (St. Louis Fed).

```sh
$ tifft history DJIA SP500 NASDAQ100
```

Fetch the data of SP500 from FRED and calculate the MACD.

```sh
$ tifft macd SP500
```

Fetch the data of SP500 from FRED and calculate the Bollinger Bands.

```sh
$ tifft bb SP500
```

Fetch the data of SP500 from FRED and calculate the RSI.

```sh
$ tifft rsi SP500
```

Run `tifft --help` for information.
