"""CLI utility demonstrating the Chan-lun backtest manager."""
from __future__ import annotations

import pandas as pd

from quant_platform import PlatformConfig
from quant_platform.backtesting import QuantBacktestManager


def load_sample_data() -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=60, freq="D")
    prices = pd.Series(range(60), index=dates).rolling(3).mean().fillna(method="bfill") + 100
    return pd.DataFrame({"close": prices}, index=dates)


def main() -> None:
    config = PlatformConfig()
    manager = QuantBacktestManager(platform_config=config.backtest)
    data = load_sample_data()
    report = manager.backtest_local(data)
    print("Backtest report:", report)


if __name__ == "__main__":
    main()
