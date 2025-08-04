"""Unit tests for the datareader module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from tifft.datareader import (
    _load_data_with_pandas_datareader,  # pyright: ignore[reportPrivateUsage]
    _print_key_values,  # pyright: ignore[reportPrivateUsage]
    _write_df_to_csv,  # pyright: ignore[reportPrivateUsage]
    calculate_indicator_for_remote_data,
    fetch_remote_data,
)


class TestFetchRemoteData:
    """Test cases for the fetch_remote_data function."""

    @patch("tifft.datareader._write_df_to_csv")
    @patch("tifft.datareader._load_data_with_pandas_datareader")
    @patch("tifft.datareader.pd.set_option")
    @patch("builtins.print")
    def test_fetch_single_name(
        self,
        mock_print: MagicMock,
        mock_set_option: MagicMock,
        mock_load_data: MagicMock,
        mock_write_csv: MagicMock,
    ) -> None:
        """Test fetching data with a single dataset name."""
        mock_df = pd.DataFrame({"value": [1, 2, 3]})
        mock_load_data.return_value = mock_df

        fetch_remote_data(
            name="SPY",
            data_source="yahoo",
            start_date="2021-01-01",
            end_date="2021-12-31",
            max_rows="10",
        )

        mock_load_data.assert_called_once_with(
            name="SPY",
            data_source="yahoo",
            start="2021-01-01",
            end="2021-12-31",
            api_key=None,
        )
        mock_set_option.assert_called_once_with("display.max_rows", 10)
        assert mock_print.call_count == 2
        mock_write_csv.assert_not_called()

    @patch("tifft.datareader._write_df_to_csv")
    @patch("tifft.datareader._load_data_with_pandas_datareader")
    @patch("builtins.print")
    def test_fetch_multiple_names(
        self,
        mock_print: MagicMock,
        mock_load_data: MagicMock,
        mock_write_csv: MagicMock,
    ) -> None:
        """Test fetching data with multiple dataset names."""
        mock_df = pd.DataFrame({"value": [1, 2, 3]})
        mock_load_data.return_value = mock_df

        fetch_remote_data(
            name=["SPY", "QQQ"],
            data_source="yahoo",
            drop_na=True,
            output_csv_path="output.csv",
        )

        mock_load_data.assert_called_once_with(
            name="SPY",  # Uses first element for non-fred sources
            data_source="yahoo",
            start=None,
            end=None,
            api_key=None,
        )
        mock_write_csv.assert_called_once()
        assert any("SPY, QQQ" in str(call_) for call_ in mock_print.call_args_list)

    @patch("tifft.datareader._load_data_with_pandas_datareader")
    def test_fetch_with_drop_na(self, mock_load_data: MagicMock) -> None:
        """Test fetching data with drop_na option."""
        mock_df = MagicMock(spec=pd.DataFrame)
        mock_df.pipe.return_value = mock_df
        mock_load_data.return_value = mock_df

        fetch_remote_data(name="TEST", drop_na=True)

        mock_df.pipe.assert_called_once()
        # Check that dropna was called in the lambda function
        pipe_func = mock_df.pipe.call_args[0][0]
        test_df = pd.DataFrame({"a": [1, 2, None]})
        result = pipe_func(test_df)
        assert len(result) == 2  # None should be dropped


class TestLoadDataWithPandasDatareader:
    """Test cases for the _load_data_with_pandas_datareader function."""

    @patch("tifft.datareader.pdd.DataReader")
    @patch("builtins.print")
    def test_load_data(
        self, mock_print: MagicMock, mock_data_reader: MagicMock
    ) -> None:
        """Test loading data with pandas_datareader."""
        mock_df = pd.DataFrame({"value": [1, 2, 3]})
        mock_data_reader.return_value = mock_df

        result = _load_data_with_pandas_datareader(
            name="SPY", data_source="yahoo", start="2021-01-01", end="2021-12-31"
        )

        assert result.equals(mock_df)
        mock_data_reader.assert_called_once_with(
            name="SPY",
            data_source="yahoo",
            start="2021-01-01",
            end="2021-12-31",
        )
        assert "Get data from yahoo" in mock_print.call_args[0][0]


class TestWriteDfToCsv:
    """Test cases for the _write_df_to_csv function."""

    @patch("builtins.print")
    def test_write_csv(self, mock_print: MagicMock, tmp_path: Path) -> None:
        """Test writing DataFrame to CSV."""
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        csv_path = tmp_path / "test.csv"

        _write_df_to_csv(df, str(csv_path))

        assert csv_path.exists()
        loaded_df = pd.read_csv(csv_path, index_col=0)
        assert df.equals(loaded_df)
        assert "Write a CSV file" in mock_print.call_args[0][0]


class TestCalculateIndicatorForRemoteData:
    """Test cases for the calculate_indicator_for_remote_data function."""

    @patch("tifft.datareader._print_key_values")
    @patch("tifft.datareader.MacdCalculator")
    @patch("tifft.datareader._load_data_with_pandas_datareader")
    @patch("builtins.print")
    def test_calculate_macd(
        self,
        mock_print: MagicMock,
        mock_load_data: MagicMock,
        mock_macd_calculator: MagicMock,
        mock_print_kv: MagicMock,
    ) -> None:
        """Test calculating MACD indicator."""
        mock_df = pd.DataFrame({"Close": [100, 101, 102, 103, 104]})
        mock_load_data.return_value = mock_df

        mock_result_df = pd.DataFrame({"macd": [1, 2, 3], "signal": [0.5, 1, 1.5]})
        mock_calc_instance = MagicMock()
        mock_calc_instance.calculate.return_value = mock_result_df
        mock_macd_calculator.return_value = mock_calc_instance

        calculate_indicator_for_remote_data(
            indicator="macd",
            name="SPY",
            fast_ema_span="12",
            slow_ema_span="26",
            macd_ema_span="9",
        )

        mock_macd_calculator.assert_called_once_with(
            fast_ema_span=12, slow_ema_span=26, macd_ema_span=9
        )
        mock_calc_instance.calculate.assert_called_once()
        mock_print_kv.assert_called_once_with(
            fast_ema_span=12, slow_ema_span=26, macd_ema_span=9
        )
        assert "Calculate MACD" in str(mock_print.call_args_list)

    @patch("tifft.datareader.BollingerBandsCalculator")
    @patch("tifft.datareader._load_data_with_pandas_datareader")
    def test_calculate_bb(
        self, mock_load_data: MagicMock, mock_bb_calculator: MagicMock
    ) -> None:
        """Test calculating Bollinger Bands indicator."""
        mock_df = pd.DataFrame({"Close": [100, 101, 102, 103, 104]})
        mock_load_data.return_value = mock_df

        mock_result_df = pd.DataFrame({"middle": [100, 101, 102]})
        mock_calc_instance = MagicMock()
        mock_calc_instance.calculate.return_value = mock_result_df
        mock_bb_calculator.return_value = mock_calc_instance

        calculate_indicator_for_remote_data(
            indicator="bb", name="SPY", window_size="20", sd_multiplier="2"
        )

        mock_bb_calculator.assert_called_once_with(window_size=20, sd_multiplier=2)

    @patch("tifft.datareader.RsiCalculator")
    @patch("tifft.datareader._load_data_with_pandas_datareader")
    def test_calculate_rsi(
        self, mock_load_data: MagicMock, mock_rsi_calculator: MagicMock
    ) -> None:
        """Test calculating RSI indicator."""
        mock_df = pd.DataFrame({"Close": [100, 101, 102, 103, 104]})
        mock_load_data.return_value = mock_df

        mock_result_df = pd.DataFrame({"rsi": [50, 55, 60]})
        mock_calc_instance = MagicMock()
        mock_calc_instance.calculate.return_value = mock_result_df
        mock_rsi_calculator.return_value = mock_calc_instance

        calculate_indicator_for_remote_data(
            indicator="rsi",
            name="SPY",
            window_size="14",
            upper_line="70",
            lower_line="30",
        )

        mock_rsi_calculator.assert_called_once_with(
            window_size=14, upper_line=70, lower_line=30
        )

    @patch("tifft.datareader._load_data_with_pandas_datareader")
    def test_calculate_invalid_indicator(self, mock_load_data: MagicMock) -> None:
        """Test calculating with invalid indicator type."""
        mock_df = pd.DataFrame({"Close": [100, 101, 102]})
        mock_load_data.return_value = mock_df

        with pytest.raises(ValueError, match="invalid indicator: invalid"):
            calculate_indicator_for_remote_data(indicator="invalid", name="SPY")

    @patch("tifft.datareader._write_df_to_csv")
    @patch("tifft.datareader.MacdCalculator")
    @patch("tifft.datareader._load_data_with_pandas_datareader")
    def test_calculate_with_output_csv(
        self,
        mock_load_data: MagicMock,
        mock_macd_calculator: MagicMock,
        mock_write_csv: MagicMock,
    ) -> None:
        """Test calculating indicator with CSV output."""
        mock_df = pd.DataFrame({"Close": [100, 101, 102]})
        mock_load_data.return_value = mock_df

        mock_result_df = pd.DataFrame({"macd": [1, 2, 3]})
        mock_calc_instance = MagicMock()
        mock_calc_instance.calculate.return_value = mock_result_df
        mock_macd_calculator.return_value = mock_calc_instance

        calculate_indicator_for_remote_data(
            indicator="macd",
            name="SPY",
            output_csv_path="output.csv",
            fast_ema_span="12",
            slow_ema_span="26",
            macd_ema_span="9",
        )

        mock_write_csv.assert_called_once()


class TestPrintKeyValues:
    """Test cases for the _print_key_values function."""

    @patch("builtins.print")
    def test_print_key_values(self, mock_print: MagicMock) -> None:
        """Test printing key-value pairs."""
        _print_key_values(fast_ema_span=12, slow_ema_span=26)

        assert mock_print.call_count == 2
        printed_values = [call_[0][0] for call_ in mock_print.call_args_list]
        assert "FAST EMA SPAN:\t12" in printed_values
        assert "SLOW EMA SPAN:\t26" in printed_values
