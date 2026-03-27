"""
Momentum Strategy — buys when price is trending up, sells when trending down.
Uses short-term vs medium-term price comparison.
"""


class MomentumStrategy:
    name = "Momentum"

    def generate_signal(self, prices: list[float]) -> dict:
        if len(prices) < 5:
            return {"signal": "HOLD", "confidence": 0.0, "strategy": self.name}

        short_avg = sum(prices[-3:]) / 3
        medium_avg = sum(prices[-10:]) / min(len(prices), 10)
        current = prices[-1]

        momentum = (short_avg - medium_avg) / medium_avg

        if momentum > 0.005:
            signal = "BUY"
            confidence = min(abs(momentum) * 20, 1.0)
        elif momentum < -0.005:
            signal = "SELL"
            confidence = min(abs(momentum) * 20, 1.0)
        else:
            signal = "HOLD"
            confidence = 0.2

        return {
            "signal": signal,
            "confidence": round(confidence, 3),
            "strategy": self.name,
            "momentum": round(momentum, 6),
        }
