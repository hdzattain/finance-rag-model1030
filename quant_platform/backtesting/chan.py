"""Simplified Chan theory utilities for quantitative strategies."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

import pandas as pd


@dataclass
class ChanSegment:
    """Represent a Chan-lun segment (笔) with trend direction and extremum."""

    start_index: int
    end_index: int
    direction: str  # "up" or "down"
    high: float
    low: float


class ChanLunAnalyzer:
    """Very lightweight Chan theory pattern detector."""

    def __init__(self, window: int = 5) -> None:
        self.window = window

    def _detect_swings(self, price: pd.Series) -> List[int]:
        """Detect swing points using rolling window extrema."""

        highs = price.rolling(self.window, center=True).max()
        lows = price.rolling(self.window, center=True).min()
        swing_points: List[int] = []
        for idx in range(self.window, len(price) - self.window):
            if price.iloc[idx] == highs.iloc[idx] or price.iloc[idx] == lows.iloc[idx]:
                swing_points.append(idx)
        return swing_points

    def extract_segments(self, data: pd.DataFrame) -> List[ChanSegment]:
        """Extract Chan segments from OHLC data."""

        close = data["close"]
        swing_points = self._detect_swings(close)
        segments: List[ChanSegment] = []
        for start, end in zip(swing_points, swing_points[1:]):
            segment_close = close.iloc[start:end + 1]
            direction = "up" if segment_close.iloc[-1] > segment_close.iloc[0] else "down"
            segments.append(
                ChanSegment(
                    start_index=start,
                    end_index=end,
                    direction=direction,
                    high=float(segment_close.max()),
                    low=float(segment_close.min()),
                )
            )
        return segments

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Create trading signals based on Chan segments and moving averages."""

        segments = self.extract_segments(data)
        signal = pd.Series(0, index=data.index)
        for segment in segments:
            if segment.direction == "up":
                signal.iloc[segment.end_index] = 1
            else:
                signal.iloc[segment.end_index] = -1
        return signal.ffill().fillna(0)


__all__ = ["ChanLunAnalyzer", "ChanSegment"]
