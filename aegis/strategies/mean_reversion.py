"""
Mean Reversion Strategy — sells when price is above SMA, buys when below.
Bets on price returning to the mean.
"""

import numpy as np


class MeanReversionStrategy:
    name = "MeanReversion"

    def __init__(self, window: int = 20):
        self.window = window

    def generate_signal(self, prices: list[float]) -> dict:
        if len(prices) < self.window:
            return {"signal": "HOLD", "confidence": 0.0, "strategy": self.name}

        recent = prices[-self.window:]
        sma = float(np.mean(recent))
        std = float(np.std(recent))
        current = prices[-1]

        if std == 0:
            return {"signal": "HOLD", "confidence": 0.0, "strategy": self.name}

        z_score = (current - sma) / std

        if z_score > 1.0:
            signal = "SELL"
            confidence = min(abs(z_score) / 3.0, 1.0)
        elif z_score < -1.0:
            signal = "BUY"
            confidence = min(abs(z_score) / 3.0, 1.0)
        else:
            signal = "HOLD"
            confidence = 0.1

        return {
            "signal": signal,
            "confidence": round(confidence, 3),
            "strategy": self.name,
            "z_score": round(z_score, 4),
        }
