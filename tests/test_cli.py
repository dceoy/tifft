"""Unit tests for the CLI module."""

from unittest.mock import MagicMock, patch

import pytest

from tifft.cli import _set_log_config, main  # type: ignore[reportPrivateUsage]


def _get_default_docopt_args() -> dict[str, bool | list[str] | str | None]:
    """Get default docopt arguments with all keys.

    Returns:
        dict: A dictionary containing all docopt argument keys with default values.
    """
    return {
        "-h": False,
        "--help": False,
        "--version": False,
        "history": False,
        "macd": False,
        "bb": False,
        "rsi": False,
        "<n>": [],
        "--data-source": "fred",
        "--api-key": None,
        "--start": None,
        "--end": None,
        "--max-rows": "60",
        "--drop-na": False,
        "--output-csv": None,
        "--debug": False,
        "--info": False,
        "--fast-ema-span": "12",
        "--slow-ema-span": "26",
        "--macd-ema-span": "9",
        "--bb-window": "20",
        "--sd-multiplier": "2",
        "--rsi-window": "14",
        "--upper-rsi": "70",
        "--lower-rsi": "30",
    }


class TestSetLogConfig:
    """Test cases for the _set_log_config function."""

    @patch("tifft.cli.logging.basicConfig")
    def test_debug_level(self, mock_basic_config: MagicMock) -> None:
        """Test logging configuration with debug level."""
        _set_log_config(debug=True, info=False)
        mock_basic_config.assert_called_once()
        assert mock_basic_config.call_args[1]["level"] == 10  # logging.DEBUG

    @patch("tifft.cli.logging.basicConfig")
    def test_info_level(self, mock_basic_config: MagicMock) -> None:
        """Test logging configuration with info level."""
        _set_log_config(debug=False, info=True)
        mock_basic_config.assert_called_once()
        assert mock_basic_config.call_args[1]["level"] == 20  # logging.INFO

    @patch("tifft.cli.logging.basicConfig")
    def test_warning_level(self, mock_basic_config: MagicMock) -> None:
        """Test logging configuration with warning level (default)."""
        _set_log_config(debug=False, info=False)
        mock_basic_config.assert_called_once()
        assert mock_basic_config.call_args[1]["level"] == 30  # logging.WARNING


class TestMain:
    """Test cases for the main function."""

    @patch("tifft.cli.docopt")
    def test_version_option(self, mock_docopt: MagicMock) -> None:
        """Test --version option."""
        mock_docopt.side_effect = SystemExit(0)
        with pytest.raises(SystemExit):
            main()

    @patch("tifft.cli.fetch_remote_data")
    @patch("tifft.cli.docopt")
    def test_history_command(
        self, mock_docopt: MagicMock, mock_fetch: MagicMock
    ) -> None:
        """Test history command."""
        # Explicitly create the return value for docopt
        docopt_args = {
            "-h": False,
            "--help": False,
            "--version": False,
            "history": True,
            "macd": False,
            "bb": False,
            "rsi": False,
            "<n>": ["SPY", "QQQ"],
            "--data-source": "yahoo",
            "--api-key": None,
            "--start": "2021-01-01",
            "--end": "2021-12-31",
            "--max-rows": "60",
            "--drop-na": True,
            "--output-csv": "output.csv",
            "--debug": False,
            "--info": False,
            "--fast-ema-span": "12",
            "--slow-ema-span": "26",
            "--macd-ema-span": "9",
            "--bb-window": "20",
            "--sd-multiplier": "2",
            "--rsi-window": "14",
            "--upper-rsi": "70",
            "--lower-rsi": "30",
        }
        mock_docopt.return_value = docopt_args

        main()

        mock_fetch.assert_called_once_with(
            name=["SPY", "QQQ"],
            data_source="yahoo",
            api_key=None,
            start_date="2021-01-01",
            end_date="2021-12-31",
            max_rows="60",
            drop_na=True,
            output_csv_path="output.csv",
        )

    @patch("tifft.cli.calculate_indicator_for_remote_data")
    @patch("tifft.cli.docopt")
    def test_macd_command(
        self, mock_docopt: MagicMock, mock_calculate: MagicMock
    ) -> None:
        """Test MACD command."""
        args = _get_default_docopt_args()
        args.update({
            "macd": True,
            "<n>": ["SPY"],
            "--data-source": "yahoo",
            "--start": "2021-01-01",
            "--end": "2021-12-31",
            "--max-rows": "60",
        })
        mock_docopt.return_value = args
        main()
        mock_calculate.assert_called_once_with(
            name="SPY",
            data_source="yahoo",
            api_key=None,
            start_date="2021-01-01",
            end_date="2021-12-31",
            max_rows="60",
            drop_na=False,
            output_csv_path=None,
            indicator="macd",
            fast_ema_span="12",
            slow_ema_span="26",
            macd_ema_span="9",
        )

    @patch("tifft.cli.calculate_indicator_for_remote_data")
    @patch("tifft.cli.docopt")
    def test_bb_command(
        self, mock_docopt: MagicMock, mock_calculate: MagicMock
    ) -> None:
        """Test Bollinger Bands command."""
        args = _get_default_docopt_args()
        args.update({
            "bb": True,
            "<n>": ["SPY"],
            "--data-source": "yahoo",
            "--max-rows": "30",
            "--info": True,
        })
        mock_docopt.return_value = args
        main()
        mock_calculate.assert_called_once_with(
            name="SPY",
            data_source="yahoo",
            api_key=None,
            start_date=None,
            end_date=None,
            max_rows="30",
            drop_na=False,
            output_csv_path=None,
            indicator="bb",
            window_size="20",
            sd_multiplier="2",
        )

    @patch("tifft.cli.calculate_indicator_for_remote_data")
    @patch("tifft.cli.docopt")
    def test_rsi_command(
        self, mock_docopt: MagicMock, mock_calculate: MagicMock
    ) -> None:
        """Test RSI command."""
        args = _get_default_docopt_args()
        args.update({
            "rsi": True,
            "<n>": ["QQQ"],
            "--api-key": "test-api-key",
            "--max-rows": "100",
            "--drop-na": True,
            "--output-csv": "rsi_output.csv",
            "--debug": True,
        })
        mock_docopt.return_value = args
        main()
        mock_calculate.assert_called_once_with(
            name="QQQ",
            data_source="fred",
            api_key="test-api-key",
            start_date=None,
            end_date=None,
            max_rows="100",
            drop_na=True,
            output_csv_path="rsi_output.csv",
            indicator="rsi",
            window_size="14",
            upper_line="70",
            lower_line="30",
        )

    @patch("tifft.cli.docopt")
    def test_no_command(self, mock_docopt: MagicMock) -> None:
        """Test when no command is specified."""
        args = _get_default_docopt_args()
        # All commands are False by default
        mock_docopt.return_value = args
        # This should execute without doing anything
        main()
