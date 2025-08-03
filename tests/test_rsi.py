"""Unit tests for the RSI calculator module."""

from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from tifft.rsi import RsiCalculator


class TestRsiCalculator:
    """Test cases for the RsiCalculator class."""

    def test_init_default_parameters(self) -> None:
        """Test initialization with default parameters."""
        calculator = RsiCalculator()
        assert calculator.upper_line == 70
        assert calculator.lower_line == 30
        assert calculator.rolling_kwargs == {"window": 14}

    def test_init_custom_parameters(self) -> None:
        """Test initialization with custom parameters."""
        calculator = RsiCalculator(
            window_size=10, upper_line=80, lower_line=20, center=True, min_periods=5
        )
        assert calculator.upper_line == 80
        assert calculator.lower_line == 20
        assert calculator.rolling_kwargs == {
            "window": 10,
            "center": True,
            "min_periods": 5,
        }

    @patch("logging.getLogger")
    def test_init_with_logging(self, mock_get_logger: MagicMock) -> None:
        """Test that logger is initialized properly."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        RsiCalculator()
        mock_get_logger.assert_called_once_with("tifft.rsi")
        mock_logger.debug.assert_called_once()

    def test_calculate_with_list_input(self) -> None:
        """Test RSI calculation with list input."""
        calculator = RsiCalculator(window_size=5)
        values = [44, 44.34, 44.09, 43.61, 44.33, 44.83, 45.10, 45.42, 45.84]

        result = calculator.calculate(values)

        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["value", "rs", "rsi", "signal"]
        assert len(result) == len(values)
        assert result["value"].tolist() == values

    def test_calculate_with_series_input(self) -> None:
        """Test RSI calculation with pandas Series input."""
        calculator = RsiCalculator(window_size=5)
        values = pd.Series([44, 44.34, 44.09, 43.61, 44.33, 44.83, 45.10, 45.42, 45.84])

        result = calculator.calculate(values)

        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["value", "rs", "rsi", "signal"]
        assert len(result) == len(values)
        assert result["value"].tolist() == values.tolist()

    def test_calculate_with_nan_values(self) -> None:
        """Test RSI calculation with NaN values."""
        calculator = RsiCalculator(window_size=3)
        values = [100, np.nan, 101, 103, np.nan, 104, 106, 108, 107, 109]

        result = calculator.calculate(values)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(values)
        # Check that NaN values are forward-filled internally for calculation
        assert not result["rsi"].iloc[4:].isna().all()  # After initial NaN period

    def test_rsi_range(self) -> None:
        """Test that RSI values are within 0-100 range."""
        calculator = RsiCalculator(window_size=5)
        values = [
            44,
            44.34,
            44.09,
            43.61,
            44.33,
            44.83,
            45.10,
            45.42,
            45.84,
            46.08,
            45.89,
        ]

        result = calculator.calculate(values)

        # RSI should be between 0 and 100 (excluding NaN values)
        rsi_values = result["rsi"].dropna()
        assert all(0 <= rsi <= 100 for rsi in rsi_values)

    def test_rsi_uptrend(self) -> None:
        """Test RSI behavior in a strong uptrend."""
        calculator = RsiCalculator(window_size=5)
        # Create a strong uptrend
        values = [100, 102, 104, 106, 108, 110, 112, 114, 116, 118]

        result = calculator.calculate(values)

        # In a strong uptrend, RSI should be high (close to 100)
        last_rsi = result["rsi"].iloc[-1]
        assert last_rsi > 70  # Should be in overbought territory

    def test_rsi_downtrend(self) -> None:
        """Test RSI behavior in a strong downtrend."""
        calculator = RsiCalculator(window_size=5)
        # Create a strong downtrend
        values = [120, 118, 116, 114, 112, 110, 108, 106, 104, 102]

        result = calculator.calculate(values)

        # In a strong downtrend, RSI should be low (close to 0)
        last_rsi = result["rsi"].iloc[-1]
        assert last_rsi < 30  # Should be in oversold territory

    def test_signal_generation(self) -> None:
        """Test signal generation based on RSI levels."""
        calculator = RsiCalculator(window_size=3, upper_line=70, lower_line=30)
        # Create values that will generate different RSI levels
        values = [
            100,
            102,
            104,
            106,
            108,  # Uptrend (high RSI)
            106,
            104,
            102,
            100,
            98,  # Downtrend (low RSI)
            99,
            100,
            101,
        ]  # Neutral

        result = calculator.calculate(values)

        # Check signals
        # During uptrend, should get overbought signal (1)
        assert any(result["signal"].iloc[3:7] == 1)
        # During downtrend, should get oversold signal (-1)
        assert any(result["signal"].iloc[7:10] == -1)

    def test_signal_thresholds(self) -> None:
        """Test that signals respect the upper and lower line thresholds."""
        calculator = RsiCalculator(window_size=3, upper_line=80, lower_line=20)
        values = list(range(100, 150))  # Strong uptrend

        result = calculator.calculate(values)

        # Signals should only be 1 when RSI > 80
        overbought_signals = result[result["signal"] == 1]
        assert all(overbought_signals["rsi"] > 80)

        # Create downtrend for oversold test
        values_down = list(range(150, 100, -1))
        result_down = calculator.calculate(values_down)

        # Signals should only be -1 when RSI < 20
        oversold_signals = result_down[result_down["signal"] == -1]
        if len(oversold_signals) > 0:
            assert all(oversold_signals["rsi"] < 20)

    def test_rs_calculation(self) -> None:
        """Test the Relative Strength calculation."""
        calculator = RsiCalculator(window_size=3)
        # Simple values with known gains and losses
        values = [100, 102, 101, 103]  # Gains: 2, 0, 2; Losses: 0, 1, 0

        result = calculator.calculate(values)

        # At index 3: avg_gain = (2+0+2)/3 = 4/3, avg_loss = (0+1+0)/3 = 1/3
        # RS = avg_gain / avg_loss = (4/3) / (1/3) = 4
        assert result["rs"].iloc[3] == pytest.approx(4.0, rel=1e-2)

    def test_rsi_formula(self) -> None:
        """Test the RSI formula calculation."""
        calculator = RsiCalculator(window_size=3)
        values = [100, 102, 101, 103, 105]

        result = calculator.calculate(values)

        # Verify RSI formula: RSI = 100 - 100/(1+RS)
        for idx in range(3, len(values)):  # Skip initial NaN values
            if not pd.isna(result["rs"].iloc[idx]):
                expected_rsi = 100 - 100 / (1 + result["rs"].iloc[idx])
                assert result["rsi"].iloc[idx] == pytest.approx(expected_rsi, rel=1e-10)

    def test_empty_input(self) -> None:
        """Test behavior with empty input."""
        calculator = RsiCalculator()

        result = calculator.calculate([])

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        assert list(result.columns) == ["value", "rs", "rsi", "signal"]

    def test_single_value_input(self) -> None:
        """Test behavior with single value input."""
        calculator = RsiCalculator()

        result = calculator.calculate([100])

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result["value"].iloc[0] == 100
        assert pd.isna(result["rs"].iloc[0])  # No previous value to calculate diff
        assert pd.isna(result["rsi"].iloc[0])

    def test_constant_values(self) -> None:
        """Test RSI with constant values."""
        calculator = RsiCalculator(window_size=3)
        values = [100, 100, 100, 100, 100]

        result = calculator.calculate(values)

        # With constant values, there are no gains or losses
        # RS calculation would involve 0/0, which results in NaN
        # RSI should handle this gracefully
        assert all(
            pd.isna(result["rsi"].iloc[1:])
        )  # All RSI values after first should be NaN

    def test_division_by_zero_handling(self) -> None:
        """Test handling when downward average is zero."""
        calculator = RsiCalculator(window_size=3)
        # Only upward movements
        values = [100, 101, 102, 103, 104]

        result = calculator.calculate(values)

        # When there are no losses, RS approaches infinity and RSI approaches 100
        last_rsi = result["rsi"].iloc[-1]
        assert last_rsi == pytest.approx(100.0, rel=1e-2)

    def test_custom_rolling_kwargs(self) -> None:
        """Test that custom rolling kwargs are properly applied."""
        calculator = RsiCalculator(window_size=5, min_periods=3)
        values = [100, 102, 101, 103, 105]

        result = calculator.calculate(values)

        # With min_periods=3, we should get non-NaN RSI values starting from index 3
        assert pd.isna(result["rsi"].iloc[2])
        assert not pd.isna(result["rsi"].iloc[3])

    def test_large_price_movements(self) -> None:
        """Test behavior with large price movements."""
        calculator = RsiCalculator(window_size=3)
        values = [100, 200, 50, 150, 75]  # Large swings

        result = calculator.calculate(values)

        # Check that calculations don't fail with large movements
        assert not result["rsi"].iloc[3:].isna().all()
        # Large movements should still produce valid RSI values
        rsi_values = result["rsi"].dropna()
        assert all(0 <= rsi <= 100 for rsi in rsi_values)

    def test_dataframe_structure(self) -> None:
        """Test the structure of the output DataFrame."""
        calculator = RsiCalculator()
        values = list(range(100, 120))

        result = calculator.calculate(values)

        # Check column order
        assert list(result.columns) == ["value", "rs", "rsi", "signal"]

        # Check data types
        assert result["value"].dtype in {np.dtype("int64"), np.dtype("float64")}
        assert result["rs"].dtype == np.dtype("float64")
        assert result["rsi"].dtype == np.dtype("float64")
        assert result["signal"].dtype == np.dtype("int64")
