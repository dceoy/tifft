#!/usr/bin/env python

from pathlib import Path

import pandas as pd
import pandas_datareader.data as pdd


def fetch_df_from_fred(symbols, output_csv_path=None, start_date=None,
                       end_date=None, max_rows=None, **kwargs):
    pd.set_option('display.max_rows', (int(max_rows) if max_rows else None))
    df = pdd.DataReader(
        name=symbols, data_source='fred', start=start_date, end=end_date,
        **kwargs
    )
    print('>>\tGet historical data from FRED:\t' + ', '.join(symbols))
    print(df)
    if output_csv_path:
        output_csv = Path(output_csv_path).resolve()
        print(f'>>\tWrite a CSV file:\t{output_csv}')
        df.to_csv(output_csv, mode='w', header=True, sep=',')
