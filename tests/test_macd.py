"""Unit tests for the MACD calculator module."""

from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from tifft.macd import MacdCalculator


class TestMacdCalculator:
    """Test cases for the MacdCalculator class."""

    def test_init_default_parameters(self) -> None:
        """Test initialization with default parameters."""
        calculator = MacdCalculator()
        assert calculator.fast_ema_span == 12
        assert calculator.slow_ema_span == 26
        assert calculator.macd_ema_span == 9
        assert calculator.ewm_kwargs == {"adjust": False}

    def test_init_custom_parameters(self) -> None:
        """Test initialization with custom parameters."""
        calculator = MacdCalculator(
            fast_ema_span=10, slow_ema_span=20, macd_ema_span=5, min_periods=1
        )
        assert calculator.fast_ema_span == 10
        assert calculator.slow_ema_span == 20
        assert calculator.macd_ema_span == 5
        assert calculator.ewm_kwargs == {"adjust": False, "min_periods": 1}

    def test_init_invalid_spans(self) -> None:
        """Test initialization with invalid span parameters."""
        with pytest.raises(
            ValueError, match="fast_ema_span must be less than slow_ema_span"
        ):
            MacdCalculator(fast_ema_span=26, slow_ema_span=26)

        with pytest.raises(
            ValueError, match="fast_ema_span must be less than slow_ema_span"
        ):
            MacdCalculator(fast_ema_span=30, slow_ema_span=26)

    @patch("logging.getLogger")
    def test_init_with_logging(self, mock_get_logger: MagicMock) -> None:
        """Test that logger is initialized properly."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        MacdCalculator()
        mock_get_logger.assert_called_once_with("tifft.macd")
        mock_logger.debug.assert_called_once()

    def test_calculate_with_list_input(self) -> None:
        """Test MACD calculation with list input."""
        calculator = MacdCalculator()
        values = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109]

        result = calculator.calculate(values)

        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["value", "macd", "macd_ema", "signal"]
        assert len(result) == len(values)
        assert result["value"].tolist() == values

    def test_calculate_with_series_input(self) -> None:
        """Test MACD calculation with pandas Series input."""
        calculator = MacdCalculator()
        values = pd.Series([100, 102, 101, 103, 105, 104, 106, 108, 107, 109])

        result = calculator.calculate(values)

        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["value", "macd", "macd_ema", "signal"]
        assert len(result) == len(values)
        assert result["value"].tolist() == values.tolist()

    def test_calculate_with_nan_values(self) -> None:
        """Test MACD calculation with NaN values."""
        calculator = MacdCalculator()
        values = [100, np.nan, 101, 103, np.nan, 104, 106, 108, 107, 109]

        result = calculator.calculate(values)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(values)
        # Check that NaN values are forward-filled internally for calculation
        assert not result["macd"].isna().all()
        assert not result["macd_ema"].isna().all()

    def test_signal_generation_bullish(self) -> None:
        """Test signal generation for bullish scenarios."""
        calculator = MacdCalculator(fast_ema_span=2, slow_ema_span=4, macd_ema_span=2)
        # Create an upward trending price series
        values = [100, 102, 104, 106, 108, 110, 112, 114, 116, 118]

        result = calculator.calculate(values)

        # In an upward trend, MACD should eventually become positive
        # and signal should show bullish signs (1 or 2)
        last_signals = result["signal"].iloc[-3:].to_numpy()
        assert any(signal > 0 for signal in last_signals)

    def test_signal_generation_bearish(self) -> None:
        """Test signal generation for bearish scenarios."""
        calculator = MacdCalculator(fast_ema_span=2, slow_ema_span=4, macd_ema_span=2)
        # Create a downward trending price series
        values = [120, 118, 116, 114, 112, 110, 108, 106, 104, 102]

        result = calculator.calculate(values)

        # In a downward trend, MACD should eventually become negative
        # and signal should show bearish signs (-1 or -2)
        last_signals = result["signal"].iloc[-3:].to_numpy()
        assert any(signal < 0 for signal in last_signals)

    def test_signal_values(self) -> None:
        """Test that signal values are within expected range."""
        calculator = MacdCalculator()
        values = [100 + i + (i % 3) for i in range(50)]  # Some variation

        result = calculator.calculate(values)

        # Signal should only be -2, -1, 0, 1, or 2 (0 for NaN values)
        unique_signals = result["signal"].unique()
        assert all(
            signal in {-2, -1, 0, 1, 2}
            for signal in unique_signals
            if not pd.isna(signal)
        )

    def test_macd_calculation_logic(self) -> None:
        """Test the core MACD calculation logic."""
        calculator = MacdCalculator(fast_ema_span=3, slow_ema_span=5, macd_ema_span=3)
        values = pd.Series([10, 11, 12, 11, 13, 14, 13, 15, 16, 15])

        result = calculator.calculate(values)

        # MACD = Fast EMA - Slow EMA
        # Manually calculate for verification (simplified check)
        fast_ema = values.ewm(span=3, adjust=False).mean()
        slow_ema = values.ewm(span=5, adjust=False).mean()
        expected_macd = fast_ema - slow_ema

        # Allow for small floating point differences
        pd.testing.assert_series_equal(
            result["macd"], expected_macd, check_names=False, rtol=1e-10
        )

    def test_empty_input(self) -> None:
        """Test behavior with empty input."""
        calculator = MacdCalculator()

        result = calculator.calculate([])

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        assert list(result.columns) == ["value", "macd", "macd_ema", "signal"]

    def test_single_value_input(self) -> None:
        """Test behavior with single value input."""
        calculator = MacdCalculator()

        result = calculator.calculate([100])

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result["value"].iloc[0] == 100

    def test_custom_ewm_kwargs(self) -> None:
        """Test that custom EWM kwargs are properly applied."""
        calculator = MacdCalculator(min_periods=5)
        values = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109]

        result = calculator.calculate(values)

        # With min_periods=5, early values should have more NaN
        assert result["macd"].iloc[:4].isna().sum() > 0

    def test_dataframe_structure(self) -> None:
        """Test the structure of the output DataFrame."""
        calculator = MacdCalculator()
        values = list(range(100, 150))

        result = calculator.calculate(values)

        # Check column order
        assert list(result.columns) == ["value", "macd", "macd_ema", "signal"]

        # Check data types
        assert result["value"].dtype in {np.dtype("int64"), np.dtype("float64")}
        assert result["macd"].dtype == np.dtype("float64")
        assert result["macd_ema"].dtype == np.dtype("float64")
        assert result["signal"].dtype == np.dtype("int64")
