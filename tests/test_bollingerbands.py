"""Unit tests for the Bollinger Bands calculator module."""

from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from tifft.bollingerbands import BollingerBandsCalculator


class TestBollingerBandsCalculator:
    """Test cases for the BollingerBandsCalculator class."""

    def test_init_default_parameters(self) -> None:
        """Test initialization with default parameters."""
        calculator = BollingerBandsCalculator()
        assert calculator.sd_multiplier == 2
        assert calculator.rolling_kwargs == {"window": 20}

    def test_init_custom_parameters(self) -> None:
        """Test initialization with custom parameters."""
        calculator = BollingerBandsCalculator(
            window_size=10, sd_multiplier=3, center=True, min_periods=5
        )
        assert calculator.sd_multiplier == 3
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

        BollingerBandsCalculator()
        mock_get_logger.assert_called_once_with("tifft.bollingerbands")
        mock_logger.debug.assert_called_once()

    def test_calculate_with_list_input(self) -> None:
        """Test Bollinger Bands calculation with list input."""
        calculator = BollingerBandsCalculator(window_size=5)
        values = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109]

        result = calculator.calculate(values)

        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == [
            "value",
            "ma",
            "sd",
            "lower_bb",
            "upper_bb",
            "signal",
        ]
        assert len(result) == len(values)
        assert result["value"].tolist() == values

    def test_calculate_with_series_input(self) -> None:
        """Test Bollinger Bands calculation with pandas Series input."""
        calculator = BollingerBandsCalculator(window_size=5)
        values = pd.Series([100, 102, 101, 103, 105, 104, 106, 108, 107, 109])

        result = calculator.calculate(values)

        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == [
            "value",
            "ma",
            "sd",
            "lower_bb",
            "upper_bb",
            "signal",
        ]
        assert len(result) == len(values)
        assert result["value"].tolist() == values.tolist()

    def test_calculate_with_nan_values(self) -> None:
        """Test Bollinger Bands calculation with NaN values."""
        calculator = BollingerBandsCalculator(window_size=3)
        values = [100, np.nan, 101, 103, np.nan, 104, 106, 108, 107, 109]

        result = calculator.calculate(values)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(values)
        # Check that NaN values are forward-filled internally for calculation
        assert not result["ma"].iloc[3:].isna().all()  # After window size
        assert not result["sd"].iloc[3:].isna().all()

    def test_moving_average_calculation(self) -> None:
        """Test that moving average is calculated correctly."""
        calculator = BollingerBandsCalculator(window_size=3)
        values = [10, 20, 30, 40, 50]

        result = calculator.calculate(values)

        # First two values should be NaN (window size = 3)
        assert pd.isna(result["ma"].iloc[0])
        assert pd.isna(result["ma"].iloc[1])
        # Third value should be (10 + 20 + 30) / 3 = 20
        assert result["ma"].iloc[2] == pytest.approx(20.0)
        # Fourth value should be (20 + 30 + 40) / 3 = 30
        assert result["ma"].iloc[3] == pytest.approx(30.0)

    def test_bollinger_bands_calculation(self) -> None:
        """Test that Bollinger Bands are calculated correctly."""
        calculator = BollingerBandsCalculator(window_size=3, sd_multiplier=2)
        values = [100, 100, 100, 110, 120]  # Constant then increasing

        result = calculator.calculate(values)

        # For constant values, SD should be 0
        assert result["sd"].iloc[2] == pytest.approx(0.0)
        assert result["lower_bb"].iloc[2] == result["ma"].iloc[2]
        assert result["upper_bb"].iloc[2] == result["ma"].iloc[2]

        # For varying values, bands should be separated
        assert result["sd"].iloc[4] > 0
        assert result["lower_bb"].iloc[4] < result["ma"].iloc[4]
        assert result["upper_bb"].iloc[4] > result["ma"].iloc[4]

    def test_band_width_with_different_multipliers(self) -> None:
        """Test band width changes with different SD multipliers."""
        values = [100, 102, 98, 101, 103, 99, 102, 100, 104, 101]

        calc_2sd = BollingerBandsCalculator(window_size=5, sd_multiplier=2)
        calc_3sd = BollingerBandsCalculator(window_size=5, sd_multiplier=3)

        result_2sd = calc_2sd.calculate(values)
        result_3sd = calc_3sd.calculate(values)

        # 3SD bands should be wider than 2SD bands
        band_width_2sd = result_2sd["upper_bb"] - result_2sd["lower_bb"]
        band_width_3sd = result_3sd["upper_bb"] - result_3sd["lower_bb"]

        # Compare non-NaN values
        valid_idx = ~band_width_2sd.isna()
        assert all(band_width_3sd[valid_idx] > band_width_2sd[valid_idx])

    def test_signal_generation(self) -> None:
        """Test signal generation based on residuals."""
        calculator = BollingerBandsCalculator(window_size=3)
        # Create values that will generate different signals
        values = [
            100,
            100,
            100,  # Start with constant
            110,  # Above MA
            90,  # Below MA
            100,
            100,
            100,
        ]

        result = calculator.calculate(values)

        # Signal should be positive when value > MA
        assert result["signal"].iloc[3] > 0
        # Signal should be negative when value < MA
        assert result["signal"].iloc[4] < 0

    def test_signal_calculation_logic(self) -> None:
        """Test the signal calculation logic in detail."""
        calculator = BollingerBandsCalculator(window_size=3, sd_multiplier=2)
        values = [100, 102, 98, 106, 94]

        result = calculator.calculate(values)

        # Manually verify signal calculation for non-NaN values
        for idx in range(2, len(values)):  # Skip initial NaN values
            if not pd.isna(result["sd"].iloc[idx]) and result["sd"].iloc[idx] > 0:
                residual = (
                    result["value"].iloc[idx] - result["ma"].iloc[idx]
                ) / result["sd"].iloc[idx]
                expected_signal = int(
                    np.floor(residual) if residual > 0 else np.ceil(residual)
                )
                assert result["signal"].iloc[idx] == expected_signal

    def test_empty_input(self) -> None:
        """Test behavior with empty input."""
        calculator = BollingerBandsCalculator()

        result = calculator.calculate([])

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        assert list(result.columns) == [
            "value",
            "ma",
            "sd",
            "lower_bb",
            "upper_bb",
            "signal",
        ]

    def test_single_value_input(self) -> None:
        """Test behavior with single value input."""
        calculator = BollingerBandsCalculator()

        result = calculator.calculate([100])

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result["value"].iloc[0] == 100
        assert pd.isna(result["ma"].iloc[0])  # Not enough data for MA

    def test_custom_rolling_kwargs(self) -> None:
        """Test that custom rolling kwargs are properly applied."""
        calculator = BollingerBandsCalculator(window_size=5, min_periods=3)
        values = [100, 102, 101, 103, 105]

        result = calculator.calculate(values)

        # With min_periods=3, we should get non-NaN values starting from index 2
        assert pd.isna(result["ma"].iloc[1])
        assert not pd.isna(result["ma"].iloc[2])

    def test_zero_standard_deviation(self) -> None:
        """Test behavior when standard deviation is zero."""
        calculator = BollingerBandsCalculator(window_size=3)
        values = [100, 100, 100, 100, 100]  # All same values

        result = calculator.calculate(values)

        # SD should be 0 for constant values
        assert all(result["sd"].iloc[2:] == 0)
        # Signal should be 0 when SD is 0 (residual fillna(0))
        assert all(result["signal"].iloc[2:] == 0)

    def test_large_price_movements(self) -> None:
        """Test behavior with large price movements."""
        calculator = BollingerBandsCalculator(window_size=3, sd_multiplier=2)
        values = [100, 100, 100, 200, 50]  # Large jumps

        result = calculator.calculate(values)

        # Check that calculations don't fail with large movements
        assert not result["ma"].isna().all()
        assert not result["sd"].isna().all()
        # Check specific signal values based on actual calculations
        # At index 3: residual = (200-133.33)/57.74 ≈ 1.15, signal = 1
        assert result["signal"].iloc[3] == 1
        # At index 4: residual = (50-116.67)/76.38 ≈ -0.87, signal = 0
        assert result["signal"].iloc[4] == 0

    def test_dataframe_structure(self) -> None:
        """Test the structure of the output DataFrame."""
        calculator = BollingerBandsCalculator()
        values = list(range(100, 130))

        result = calculator.calculate(values)

        # Check column order
        expected_columns = ["value", "ma", "sd", "lower_bb", "upper_bb", "signal"]
        assert list(result.columns) == expected_columns

        # Check data types
        assert result["value"].dtype in {np.dtype("int64"), np.dtype("float64")}
        assert result["ma"].dtype == np.dtype("float64")
        assert result["sd"].dtype == np.dtype("float64")
        assert result["lower_bb"].dtype == np.dtype("float64")
        assert result["upper_bb"].dtype == np.dtype("float64")
        assert result["signal"].dtype == np.dtype("int64")
